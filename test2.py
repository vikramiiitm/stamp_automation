import win32print
import win32ui
from ctypes import windll, Structure, c_float, byref
from ctypes.wintypes import LONG

# Define a XFORM structure required for SetWorldTransform
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

def print_stamp(printer_name, text, x, y, rotate=False):
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

# Example usage
printer_name = 'Your_Printer_Name'
text = '01013418092024010961'
x, y = 1200, 200
rotate_text = True  # Set to True if you want to rotate the text 180 degrees

print_stamp("EPSON L3250 Series", text, x, y, rotate=rotate_text)
