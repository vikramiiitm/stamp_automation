import cups

def list_printers():
    printers = cups.getPrinters()
    for printer in printers:
        print(f"Printer Name: {printer['name']}")
        print(f"Location: {printer['location']}")
        print(f"Status: {printer['state']}")
        print()

if __name__ == "__main__":
    list_printers()