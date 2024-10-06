import base64
import requests

# OpenAI API Key
api_key = "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"


import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Path to your image

image_path = "estamp.png"

def get_promt(ocr):
    prompt = f"""
    The following text is extracted from a traditional stamp paper. The certificate number may or may not be explicitly labeled with terms like:

    Here is the certificate format for different state.

    West Bengal (certificate number length: 10): 95AB ------

    However, the certificate number is usually a sequence of digits or a combination of letters and digits, often located prominently on the document. In some cases, there may be no label, and the number could appear on its own.

    Please examine the following extracted text and identify the sequence that most likely represents the certificate number, even if no label is present. It could be a long number (8–12 digits) or a combination of digits and letters.

    Here is the extracted text:

    '{ocr}'

    Return Only the certificate number, don't use sentence for ansering, also remove space in between certificate number. 
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

# Function to encode the image
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
        # print(response.json())
        try:
            response = response.json()['choices'][0]['message']['content']
        except:
            response = None
        return response
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

# print(ocr_text)
# print(check_certificate_present(ocr_text))


# data = {'id': 'chatcmpl-ACTJoRFsJFbrzRlATKPjBC3qXOseg', 'object': 'chat.completion', 'created': 1727536000, 'model': 'gpt-4o-mini-2024-07-18', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': '95AB488151', 'refusal': None}, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 14372, 'completion_tokens': 4, 'total_tokens': 14376, 'completion_tokens_details': {'reasoning_tokens': 0}}, 'system_fingerprint': 'fp_74ba47b4ac'}

# print(data["choices"][0]['message']['content'])


def extract_e_stamp_value(ocr_text):
    import re
    # print(ocr_text)
    certificate_number = re.search(r"IN-[A-Z0-9]+", ocr_text)

    if certificate_number:
        return certificate_number.group(0)
    else:
        print("Unable to find the value after 'e-Stamp'.")
    return None

# print(extract_e_stamp_value())


def get_certificate_from_all():
    import os
    # folder_path = "stamp_paper"  # Replace with your actual folder path. Make sure the folder exists.
    # file_names = [filename for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename))]
    # for filename in file_names:
    #     filename = filename.split("/")[-1]
    #     print(f"Processing {filename}")
    #     filename = f'stamp_paper/{filename}'
    # Loop through all the files in the folder
    

    ocr_text = ocr_image('stamp_paper/E-Stamp.pdf-image-005.jpg')
    # print(ocr_text)
    if ocr_text:
        # print(ocr_text)
        #  Case 1: If the text contains "certificate", i.e. it's a e-stamp.
        if check_certificate_present(ocr_text):
            print(f"Format: E-Stamp Delhi")
            certificate_number = extract_e_stamp_value(ocr_text)
            print(f"certificate_number : {certificate_number}")
        #  Case 2: If the text doesn't contain "certificate", i.e. it's not a e-stamp.
        # Check If West Bengal stamp. 
        elif check_bengal_format:
            print(f"Format: Stamp West Bengal")
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


# get_certificate_from_all()
print(ocr_image('stamp_paper/E-Stamp.pdf-image-005.jpg'))

get_certificate_from_all()