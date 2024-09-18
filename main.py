import subprocess
import requests
import cv2
import numpy as np

def get_device_ip():
    """Gets the IP address of the connected device using ADB."""

    try:
        result = subprocess.run(["adb", "shell", "ifconfig"], capture_output=True)
        output = result.stdout.decode()

        # Parse the output to extract the IP address
        for line in output.splitlines():
            if "wlan0" in line:
                # Find the next line containing "inet addr"
                for next_line in output.splitlines()[output.splitlines().index(line) + 1:]:
                    if "inet addr:" in next_line:
                        # Extract the IP address
                        ip_address = next_line.split()[1]
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


if __name__ == "__main__":
    ip_address = get_device_ip()
    if ip_address:
        print("Device IP address:", ip_address.split(":")[1])
    else:
        print("Error getting device IP")
    
    # Capture photo and get the captured image
    captured_image = capture_photo(ip_address.split(":")[1])

    # Process the captured image (if needed)
    # ...

    # Do something with the captured image
    print(captured_image.shape)  # Print the image dimensions