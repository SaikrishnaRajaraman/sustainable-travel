import pymupdf  # PyMuPDF

# Open the PDF file
def extract_text_from_pdf():
    doc = pymupdf.open("invoice_data.pdf")
    print("PDF opened successfully")
    # Iterate through each page
    for page in doc:
        # Extract text from the page
        text = page.get_text()
        print(type(text))
        break

if __name__ == "__main__":
    pdf_path = "/Users/vengateshd/Downloads/PCard Statements Maria/ Gallardo-Williams.pdf"
    print("Inside main")
    extract_text_from_pdf()
