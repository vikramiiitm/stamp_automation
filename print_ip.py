import zxing
import cv2
import json
# file = 
reader = zxing.BarCodeReader()
print(reader.zxing_version, reader.zxing_version_info)

barcode = reader.decode("image.png")
print(barcode)