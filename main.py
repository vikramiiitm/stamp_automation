import subprocess
import requests
import cv2
import numpy as np
import win32print
import win32ui

''' Pro
1. Get IP of connected phone
2. Check Available Printer
3. Capture Photo stamp
4. Scan the barcode, get ref number
6. Search against ref number in excel
7. Get value from excel and print in stamp
'''

debug=True
def get_device_ip():
    """Gets the IP address of the connected device using ADB."""

    try:
        result = subprocess.run(["adb.exe", "shell", "ifconfig"], capture_output=True)
        output = result.stdout.decode()
        if debug:
            print(f"\n\nadb output: {output} \n\n")

        # Parse the output to extract the IP address
        for line in output.splitlines():
            if "wlan0" in line:
                # Find the next line containing "inet addr"
                for next_line in output.splitlines()[output.splitlines().index(line) + 1:]:
                    if "inet addr:" in next_line or "ccmni2" in next_line:
                        '''with wifi
                            wlan0
                                inet addr:192.168.29.21  Bcast:192.168.29.255  Mask:255.255.255.0 
                                inet addr:192.168.29.21  Bcast:192.168.29.255  Mask:255.255.255.0
                        '''
                        ''' without wifi
                            ccmni2    Link encap:UNSPEC
                                inet addr:100.95.141.196  Mask:255.0.0.0
                                inet6 addr: 2401:4900:55a2:18dc:dc38:4a44:b0af:728b/64 Scope: Global
                                inet6 addr: fe80::dc38:4a44:b0af:728b/64 Scope: Link
                                UP RUNNING NOARP  MTU:1500  Metric:1
                                RX packets:96752 errors:0 dropped:0 overruns:0 frame:0
                                TX packets:29000 errors:0 dropped:0 overruns:0 carrier:0
                                collisions:0 txqueuelen:1000
                                RX bytes:102249064 TX bytes:10128480
                        '''
                        # Extract the IP address
                        ip_address = next_line.split()[1].split(":")[1]
                        return ip_address

                # IP address not found in next line
                print("IP address not found for wlan0 interface")
                return None

        # wlan0 not found
        print("wlan0 interface not found")
        return None

    except Exception as e:
        print("Error getting device IP:", str(e))
        return None
# Replace the below URL with your own. Make sure to add "/shot.jpg" at last.

def capture_photo(ip=None):
    filename="captured_photo.jpg"
    if not ip:
        exit(0)
    url = f"http://{ip}:8080/shot.jpg"
    """Captures a photo from the IP camera and saves it to the specified filename.

    Args:
        filename (str, optional): The filename to save the photo. Defaults to "captured_photo.jpg".

    Returns:
        numpy.ndarray: The captured image as a NumPy array.
    """

    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)

    # Resize the image if needed
    # img = imutils.resize(img, width=1000, height=1800)

    # Save the photo
    cv2.imwrite(filename, img)
    print(f"Photo saved as {filename}")

    return img

def scan_barcode(filename):
    from test import read
    data = read()
    print(data)

def list_printers():

    try:
        # List all printers with verbose information retrieval
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS | win32print.PRINTER_ENUM_LOCAL, None, 1)  # 2 for PRINTER_ENUM_FULL
        if debug:
            print(f"\n\n Printers Found: {printers} \n\n")
        for index, printer in enumerate(printers):
            printer_name = printer[2]  # Printer name is at index 2
            if debug:
                print(f"Printer #{index+1}: {printer_name}")
            if printer_name == "EPSON L3250 Series":
                break
        if printer_name is not None and printer_name:
            return printer_name
        else:
            return None
    except win32print.WinError as e:
        print(f"Error listing printers: {e}")
        return None

def print_stamp(printer_name, text, x, y):
    try:
        hDC = win32ui.CreateDC()
        hDC.StartDoc(text)
        hDC.StartPage()

        # Set the font and text color
        hDC.SelectObject(win32ui.CreateFont({
            'name': 'Arial',
            'size': 12,
            'weight': win32ui.BOLD,
            'color': win32ui.RGB(0, 0, 0)  # Black
        }))

        # Assuming A4 paper dimensions in pixels (adjust if needed)
        a4_width_pixels = 2480
        a4_height_pixels = 3508

        # Calculate the desired coordinates based on A4 paper dimensions
        desired_x = a4_width_pixels // 2  # Center horizontally
        desired_y = a4_height_pixels - (a4_height_pixels * 0.25)  # 1/4 from the bottom

        # Adjust x and y coordinates based on text size and margins
        text_width, text_height = hDC.GetTextExtent(text)
        desired_x -= text_width // 2  # Center horizontally
        desired_y -= text_height // 2  # Center vertically

        hDC.TextOut(desired_x, desired_y, text)

        hDC.EndPage()
        hDC.EndDoc()
    except Exception as e:
        print(f"Error printing: {e}")

if __name__ == "__main__":
    ''' Pro
    1. Get IP of connected phone
    2. Check Available Printer
    3. Capture Photo stamp
    4. Scan the barcode, get ref number
    6. Search against ref number in excel
    7. Get value from excel and print in stamp
    '''

    # 1
    ip_address = get_device_ip()
    if ip_address:
        print("Device IP address:", ip_address)
    else:
        print("Error getting device IP")

    #2 Get printer List
    # printer_name = list_printers()
    # print(printer_name)
    
    # Capture photo and get the captured image
    captured_image = capture_photo(ip_address)
    scan_barcode("captured_photo.jpg")

    # Process the captured image (if needed)
    # ...

    # Do something with the captured image
    # print(captured_image.shape)  # Print the image dimensions
    # print_stamp(printer_name, "Hello", 0,0)


    # Printer print
