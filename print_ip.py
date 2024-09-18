from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import win32ui,win32print
from glob import glob
from win32print import (
    OpenPrinter,
    PRINTER_ALL_ACCESS,  # Use this instead of PRINTER_ACCESS_WRITE
    StartDocPrinter,
    StartPagePrinter,
    WritePrinter,
    EndPagePrinter,
    EndDocPrinter,
    ClosePrinter,
)
import win32api

def print_text_reportlab(printer_name, text, x, y):
    try:
        # Create a PDF document
        doc = canvas.Canvas('output.pdf', pagesize=A4)

        # Set the font and text color
        doc.setFont('Helvetica', 12)
        doc.setFillColorRGB(0, 0, 0)  # Black

        # Draw the text at the specified coordinates
        doc.drawString(x, y, text)

        # Save the PDF to a file
        doc.save()
        
        # Open the printer
        name = win32print.GetDefaultPrinter() # verify that it matches with the name of your printer
        printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS} # Doesn't work with PRINTER_ACCESS_USE
        handle = win32print.OpenPrinter(name, printdefaults)
        level = 2
        attributes = win32print.GetPrinter(handle, level)
        attributes['pDevMode'].Duplex = 1  #no flip
        #attributes['pDevMode'].Duplex = 2  #flip up
        # attributes['pDevMode'].Duplex = 3   #flip over
        win32print.SetPrinter(handle, level, attributes, 0)
        win32print.GetPrinter(handle, level)['pDevMode'].Duplex
        win32api.ShellExecute(0,'print','output.pdf','.','/manualstoprint',0)
    except Exception as e:
        print(f"Error printing: {e}")

if __name__ == "__main__":
    print_text_reportlab("EPSON L3250 Series", "Hello, world!", 100, 700)  # Adjust coordinates as needed


