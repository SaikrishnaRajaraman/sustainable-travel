import pymupdf  # PyMuPDF
import airportsdata
import re
import requests
from collections import defaultdict
#Load the airports data using IATA code
airports = airportsdata.load('IATA')
pattern = r'\b[A-Z]{3}\b'
# Open the PDF file

def isAirport(airport_code):
    airport_codes = [code for code in airport_code if code in airports]
    return airport_codes

def getPDFfromURL():

    login_payload = {
        'username': 'dummy',
        'password': 'dummy'
    }
    URL = 'https://onb20prd.acs.ncsu.edu/AppNet/docpop/PdfPop.aspx'

    session = requests.Session()

    login_response = session.post(URL, data=login_payload)

    if login_response.status_code == 200:
        print("Logged in successfully!")

        response = session.get(URL, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Print the content of the page (HTML source)
            print(response.text)
        else:
            print(f"Failed to access the page. Status code: {response.status_code}")

        # content_type = response.headers.get('Content-Type', '')
        # if 'application/pdf' in content_type:
        #     print("PDF found")
        # else: 
        #     print()
    return
    # Raise an exception for HTTP errors (4xx or 5xx)
    response.raise_for_status()

    content_type = response.headers.get('Content-Type', '')

    if 'application/pdf' in content_type:
        print("PDF found")
    return
    # Check if the response contains a PDF
    content_type = response.headers.get('Content-Type', '')
    response = requests.get(URL)
    if response.status_code == 200:
        with open('downloaded_pdf.pdf', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # Filter out keep-alive new chunks
                        print(chunk)
                        f.write(chunk)
        print("PDF downloaded successfully")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")

def extract_text_from_pdf():
    # print(airports['RDU'])

    doc = pymupdf.open("./pdfs/invoice_data2.pdf")
    print("PDF opened successfully")
    airport_codes = []
    # Iterate through each page
    # doc = ["This is a sample","IS this able to identify SFO"]
    # print(doc[0].get_text())
    # return
    dist_airports = defaultdict(float)
    for page in doc:
        # Extract text from the page
        text = page.get_text()
        total_miles = 0
        # text = page
        lines = list(text.split("\n"))
        for line in lines:
            if line.strip() and len(line) == 3:
                airport_codes.extend(isAirport(re.findall(pattern,line)))
    print(airport_codes)
    for i in range(len(airport_codes)-1):
        if airport_codes[i] == airport_codes[i+1]:
            continue
        if (airport_codes[i],airport_codes[i+1]) in  dist_airports:
            total_miles+=dist_airports[(airport_codes[i],airport_codes[i+1])]
        elif (airport_codes[i+1],airport_codes[i]) in dist_airports:
            total_miles+=dist_airports[(airport_codes[i+1],airport_codes[i])]
        else:
            response = requests.post(f'https://airportgap.com/api/airports/distance?from={airport_codes[i]}&to={airport_codes[i+1]}')
            if response.status_code == 200:
                data = response.json()
                total_miles += data['data']['attributes']['miles']
                dist_airports[(airport_codes[i],airport_codes[i+1])] = data['data']['attributes']['miles']

    print(f"Total miles: {total_miles}")
    # print(dist_airports)
    
if __name__ == "__main__":
    print("Inside main")
    extract_text_from_pdf()
    
