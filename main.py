import subprocess
import requests
import cv2
import numpy as np
import win32print
import win32ui
from dbr import *
import time
import pandas as pd
from win32con import DM_ORIENTATION, DMORIENT_LANDSCAPE, SRCCOPY, BLACK_PEN, TRANSPARENT, WHITE_BRUSH
from ctypes import windll, Structure, c_float, byref
from ctypes.wintypes import LONG
import re
import base64

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


''' Pro
1. Get IP of connected phone
2. Check Available Printer
3. Capture Photo stamp
4. Scan the barcode | OCR Image
5. Use OCR text or GPT
6. Search against ref number in excel
7. Get value from excel and print in stamp
'''

debug=False

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# OpenAI API Key
api_key = ""
def get_device_ip():
    """Gets the IP address of the connected device using ADB."""

    try:
        result = subprocess.run(["adb.exe", "shell", "ifconfig"], capture_output=True)
        print(result)
        output = result.stdout.decode()
        if debug:
            print(f"\n\nadb output: {output} \n\n")

        # Parse the output to extract the IP address
        for line in output.splitlines():
            print(line)
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

def get_promt(ocr):
    prompt = f"""
    The following text is extracted from a traditional stamp paper. The certificate number may or may not be explicitly labeled with terms like:

    Here is the certificate format for different state.

    West Bengal (certificate number length: 10): 95AB ------

    However, the certificate number is usually a sequence of digits or a combination of letters and digits, often located prominently on the document. In some cases, there may be no label, and the number could appear on its own.

    Please examine the following extracted text and identify the sequence that most likely represents the certificate number, even if no label is present. It could be a long number (8–12 digits) or a combination of digits and letters.

    Here is the extracted text:

    '{ocr}'

    Return Only the certificate number, don't use sentence for answering, also remove space in between certificate number. 
    """
    return prompt

def ocr_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        if len(text) == 0:
            return None
        else: return text

    except Exception as e:
        print(f"Error performing OCR: {e}")
        return None

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def gptvision(image_path):
    # Getting the base64 string
    base64_image = encode_image(image_path)
    ocr_text = ocr_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            # "text": "Tell only certificate number from INdian stamp paper. nothing else."
            "text": get_promt(ocr_text)
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.json():
        return response.json()['choices'][0]['message']['content']
def gpt_text(image_path):
    ocr_text = ocr_image(image_path)
    if ocr_text:
    # Preparing the request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        print(ocr_text)
        # Prompt to extract the certificate number
        # prompt = f"Tell only value of certificate no. from provided text extracted from the traditional stamp paper Here is the text: {ocr_text}. Certificate number is mix of alphabets and numbers."
        prompt = get_promt(ocr_text)
        # Payload for the GPT-3.5 API
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 50
        }

        # Sending the API request to OpenAI
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Printing the response from GPT-3.5
        print(response.json())
        return response.json()
    else:
        print("OCR failed. No text extracted from the image.")

# check if "certificate" text present in the ocr text
# Case 1
def check_certificate_present(text):
    """
    Check if the oct text contains the word "certificate".
    """
    return "certificate" in text.lower()
# Case 2
def check_bengal_format(text):
    return "bengal" in text.lower()
def extract_certificate_bengal(text):
    import re
    pattern = r"95AB [0-9]+"
    # Search for the certificate number in the text
    certificate_number = re.search(pattern, text)
    return certificate_number.group(0) if certificate_number else None

def extract_e_stamp_value(ocr_text):
    import re
    # print(ocr_text)
    certificate_number = re.search(r"IN-[A-Z0-9]+", ocr_text)

    if certificate_number:
        return certificate_number.group(0)
    else:
        print("Unable to find the value after 'e-Stamp'.")
    return None

# Using the services DBR API to scan the barcode
# It gives text results, not reliable as it contains encoded dada sometimes
def scan_barcode(filename):
    data = {}
    BarcodeReader.init_license(
        't0068lQAAAJjRSR7zR0cWZB2EpQhYsioGSFbQAlGV5iUjFQ9VBxh8QTU02FpSwicmdcuAnQTAfS5QWAEOBGCP5kdYv2cM6HA=;t0068lQAAADk5uQYPOxgZPZTg3Q/8w9Fw08L+K5ptt41B2WijIOMUleSGJTj5Alch7age51koH2YKKoC66tYhDba+d0336E0=')
    dbr_reader = BarcodeReader()
    filename = "captured_photo.jpg"
    img = cv2.imread(filename)
    try:
        start = time.time()
        dbr_results = dbr_reader.decode_file(filename)
        elapsed_time = time.time() - start

        if dbr_results != None:
            for text_result in dbr_results:
                # print(textResult["BarcodeFormatString"])
                if debug:
                    print('Dynamsoft Barcode Reader: {}. Elapsed time: {}ms'.format(
                        text_result.barcode_text, int(elapsed_time * 1000)))
                data = text_result.barcode_text
                points = text_result.localization_result.localization_points
                cv2.drawContours(
                    img, [np.intp([points[0], points[1], points[2], points[3]])], 0, (0, 255, 0), 2)
                break
            # cv2.imshow('DBR', img)
            return data
        else:
            print("DBR failed to decode {}".format(filename))
    except Exception as err:
        print("DBR failed to decode {}".format(filename))

    return None

# 
def parse_text_to_dict(text):
    import re
    """Parses the given text into a dictionary.

    Args:
        text: The input text string.

    Returns:
        A dictionary containing the parsed key-value pairs.
    """

    result = {}
    lines = text.splitlines()

    for line in lines:
        key_value = line.split(":")
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip()
            result[key] = value

    return result

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

class XFORM(Structure):
    _fields_ = [("eM11", c_float),
                ("eM12", c_float),
                ("eM21", c_float),
                ("eM22", c_float),
                ("eDx", c_float),
                ("eDy", c_float)]

def rotate_dc_180(hDC, x_center, y_center):
    """Apply 180-degree rotation using transformation matrix."""
    # Set the graphics mode to advanced to support world transformations
    windll.gdi32.SetGraphicsMode(hDC.GetSafeHdc(), 2)  # 2 = GM_ADVANCED
    
    # Create a 180-degree rotation matrix (negative scale on both axes)
    xform = XFORM()
    xform.eM11 = -1.0  # Mirror horizontally
    xform.eM12 = 0.0
    xform.eM21 = 0.0
    xform.eM22 = -1.0  # Mirror vertically
    xform.eDx = 2 * x_center  # Move back to original position
    xform.eDy = 2 * y_center

    # Apply the transformation to the device context
    windll.gdi32.SetWorldTransform(hDC.GetSafeHdc(), byref(xform))

def print_stamp(printer_name, text, x, y, rotate=True):
    try:
        # Get the printer handle
        printer_handle = win32print.OpenPrinter(printer_name)

        # Initialize the printer device context
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)

        # Start the document and the printing page
        hDC.StartDoc('Print Document')
        hDC.StartPage()

        # Set text color (RGB)
        hDC.SetTextColor(0x000000)  # Black color in RGB (0,0,0)

        # Apply 180-degree rotation if specified
        if rotate:
            # Calculate the center of the text (based on where text will be printed)
            text_width, text_height = hDC.GetTextExtent(text)
            x_center = x + text_width // 2
            y_center = y + text_height // 2
            rotate_dc_180(hDC, x_center, y_center)

        # Print the text at the specified position
        hDC.TextOut(x, y, text)

        # End the page and document
        hDC.EndPage()
        hDC.EndDoc()

        # Close the printer handle
        win32print.ClosePrinter(printer_handle)

    except Exception as e:
        print(f"Error printing: {e}")

def load_stamp_data(csv_file_path):
    """Loads the CSV data into a pandas DataFrame with 'stamp_code' as string."""
    return pd.read_csv(csv_file_path, dtype={'stamp_code': str})

def get_stamp_value_excel(stamp_code, df):
    """Fetches the value for a given stamp_code."""
    # print(df)
    # Clean up stamp_code and DataFrame values to remove extra quotes and spaces
    df['stamp_code'] = df['stamp_code'].astype(str).str.strip().str.replace('"', '')
    stamp_code = stamp_code.strip().replace('"', '')
    
    # Fetch the row with the matching stamp code
    row = df[df['stamp_code'] == stamp_code]
    # print(f"row {row}")
    if not row.empty:
        return row['value'].values[0]
    return None

def start_gui():
    subprocess.run(['python', 'stamp_gui.py'])
def runner():
    # folder_path = "stamp_paper"  # Replace with your actual folder path. Make sure the folder exists.
    # file_names = [filename for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename))]
    # for filename in file_names:
    #     filename = filename.split("/")[-1]
    #     print(f"Processing {filename}")
    #     filename = f'stamp_paper/{filename}'
    # Loop through all the files in the folder
    
    # 1 Get IP of connected device
    '''ip_address = get_device_ip()
    if ip_address:
        print("Device IP address:", ip_address)
    else:
        print("Error getting device IP. Exiting...")
        exit(0)
    #2 Get printer List
    printer_name = list_printers()
    print(printer_name)'''

    # 3 Capture photo and get the captured image
    '''captured_image = capture_photo(ip_address)'''

    ocr_text = ocr_image('stamp_paper/E-Stamp.pdf-image-007.jpg')
    certificate_number = None
    print(ocr_text)
    if ocr_text:
        # print(ocr_text)
        #  Case 1: If the text contains "certificate", i.e. it's a e-stamp.
        if check_certificate_present(ocr_text):
            print(f"Format: E-Stamp Delhi")
            certificate_number = extract_e_stamp_value(ocr_text)
            print(f"certificate_number : {certificate_number}")
        #  Case 2: If the text doesn't contain "certificate", i.e. it's not a e-stamp.
        # Check If West Bengal stamp. 
        elif check_bengal_format(ocr_text):
            print(f"Format: Stamp West Bengal")
            certificate_number = extract_certificate_bengal(ocr_text)
            print(f"certificate_number : {certificate_number}")
        else:
            # try methods without state checks
            certificate_number = extract_certificate_bengal(ocr_text)
            print(f"certificate_number : {certificate_number}")
    elif ocr_text is None:
        print("OCR failed. No text extracted from the image. Using GPTVision")
        # use gpt vision
        certificate_number = gptvision('stamp_paper/E-Stamp.pdf-image-005.jpg')
        print(f"certificate_number : {certificate_number}")

        # Verify certificate number
        # TODO: Add verification logic here.
        # gpt_text()
    else:
        certificate_number = None

    printer_name  = "test" # TODO: Remove this line once you have a valid printer name.
    if certificate_number and printer_name:
        stamp_df = load_stamp_data('data.csv')
        value = get_stamp_value_excel(certificate_number.replace('.',''), stamp_df)
        print(f"Value: {value}")

        # Save the data in processed_data.csv
        processed_data = pd.DataFrame({'certificate_number': certificate_number, 'value': value if value else 'None', 'status': True if value else False}, index={'index': [0]})
        processed_data.to_csv('processed_data.csv', mode='a', index=False, header=False)

        # Do something with the captured image
        print_stamp(printer_name, value, 1500, 200)
    else:
        print("No certificate/Printer found. Exiting...")
        print_stamp(printer_name, "", 1500, 200)

   

if __name__ == "__main__":
    ''' Pro
    1. Get IP of connected phone
    2. Check Available Printer
    3. Capture Photo stamp
    4. Scan the barcode, get ref number
    6. Search against ref number in excel
    7. Get value from excel and print in stamp
    '''
    # import subprocess
    # from multiprocessing import Process

    # if __name__ == "__main__":
    #     # Start the GUI in a separate process
    #     gui_process = Process(target=start_gui)
    #     gui_process.start()

    #     # Run runner() 10 times in the main process
    #     for i in range(10):
    #         runner()

    #     # Wait for the GUI process to finish (optional)
    #     gui_process.join()
    
