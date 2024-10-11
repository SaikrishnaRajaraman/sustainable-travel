import pdfplumber

with pdfplumber.open("./pdfs/pdf5.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_table()
        for table in tables:
            for data in table:
                if data:
                    print(data)
    # first_page = pdf.pages[0]
    # print(first_page.extract_text())