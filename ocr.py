import cv2, zxingcpp

img = cv2.imread('image.png')
results = zxingcpp.read_barcodes(img)
for result in results:
	print('Found barcode:'
		f'\n Text:    "{result.text}"'
		f'\n Format:   {result.format}'
		f'\n Content:  {result.content_type}'
		f'\n Position: {result.position}')
if len(results) == 0:
	print("Could not find any barcode.")