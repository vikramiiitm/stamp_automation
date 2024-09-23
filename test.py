import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def ocr_image(image_path):
    """Performs OCR on the specified image and returns the recognized text.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The recognized text from the image.
    """

    try:
        image = Image.open("stamp.png")
        text = pytesseract.image_to_string(image)
        return text

    except Exception as e:
        print(f"Error performing OCR: {e}")
        return None
recognized_text = ocr_image("captured_photo.jpg")
print(recognized_text)
import re

def extract_e_stamp_value(text):

  pattern = r"e-Stamp\s+(\S+)"  # Regular expression pattern
  match = re.search(pattern, text)

  if match:
    return match.group(1)
  else:
    print("Unable to find the value after 'e-Stamp'.")
    return None

if recognized_text:
    output = extract_e_stamp_value(recognized_text)
    print(output.replace('.', ''))
else:
    print("OCR failed.")