from dbr import *
import cv2
import numpy as np
import time

BarcodeReader.init_license(
    't0068lQAAAJjRSR7zR0cWZB2EpQhYsioGSFbQAlGV5iUjFQ9VBxh8QTU02FpSwicmdcuAnQTAfS5QWAEOBGCP5kdYv2cM6HA=;t0068lQAAADk5uQYPOxgZPZTg3Q/8w9Fw08L+K5ptt41B2WijIOMUleSGJTj5Alch7age51koH2YKKoC66tYhDba+d0336E0=')
dbr_reader = BarcodeReader()

def dbr_decode(dbr_reader):
    data = {}
    filename = "captured_photo.jpg"
    img = cv2.imread(filename)
    try:
        start = time.time()
        dbr_results = dbr_reader.decode_file(filename)
        elapsed_time = time.time() - start

        if dbr_results != None:
            for text_result in dbr_results:
                # print(textResult["BarcodeFormatString"])
                # print('Dynamsoft Barcode Reader: {}. Elapsed time: {}ms'.format(
                #     text_result.barcode_text, int(elapsed_time * 1000)))
                # print(dbr_results.)
                data = text_result.barcode_text
                points = text_result.localization_result.localization_points
                cv2.drawContours(
                    img, [np.intp([points[0], points[1], points[2], points[3]])], 0, (0, 255, 0), 2)
                break
            cv2.imshow('DBR', img)
            return data
        
        else:
            print("DBR failed to decode {}".format(filename))
    except Exception as err:
        print("DBR failed to decode {}".format(filename))

    return None

barcode_text = dbr_decode(dbr_reader)

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

parsed_dict = parse_text_to_dict(barcode_text)
print(parsed_dict)