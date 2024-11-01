import pymupdf  # PyMuPDF
import airportsdata
import re
import requests
from utils.utils import ground_carbon_emission
from collections import defaultdict
import csv
import os
from models.emission_model import EmissionModel
from models.ground_travel_model import GroundTravelModel
from utils.utils import calculate_carbon_emission, create_emission_report,create_ground_emission_report
import csv
from openai import OpenAI
import json
from dotenv import load_dotenv
from clean_data import get_airports_from_data
from compute_air_emissions import get_airport_pairs

#Load the airports data using IATA code
airports = airportsdata.load('IATA')
pattern = r'\b[A-Z]{3}\b'

existing_airports = defaultdict(EmissionModel)
# Open the PDF file

def isAirport(airport_code):
    airport_codes = [code for code in airport_code if code in airports]
    return airport_codes

def getPDFfromURL():

    login_payload = {
        'username': 'dummy',
        'password': 'dummy'
    }
    URL = ''

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

def load_emission_data_from_csv(csv_file):
    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                source = row['Source IATA Code']
                destination = row['Destination IATA Code']
                source_lat = row['Source Latitude']
                destination_lat = row['Destination Latitude']
                source_long = row['Source Longitude']
                destination_long = row['Destination Longitude']
                miles = row['Miles']
                carbon_emission = row['Carbon Emission']

                existing_airports[(source, destination)] = EmissionModel(source, destination, source_lat, destination_lat, source_long, destination_long, miles, carbon_emission)

    else:
        print(f"File {csv_file} does not exist")

def send_to_LLM(lines):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key = openai_api_key)
    
    content = '''
    Extract all the airport legs for the travel based on the given content and return it in this required format?
    [{
        "from_airport": "IATA Code",
        "to_airport": "IATA Code"
    }]
    '''
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ".".join(lines)},
                {"role": "user", "content": content}
            ],
            max_tokens=150,
            )
        output = response.choices[0].message.content
        output_lines = output.splitlines()
        output_lines = output_lines[1:-1]
        output = "\n".join(output_lines)
        # print(output)
        flight_data = json.loads(output)
        return flight_data
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_works_data():
    flight_codes = get_airports_from_data()

def extract_text_from_pdf(file_path):

    # doc = pymupdf.open(file_path)
    # airport_codes = []
    # airports_set_toadd = set()
    # lines_list = []
    # for page in doc:
    #     # Extract text from the page
    #     text = page.get_text()
    #     # text = page
    #     lines = ".".join(list(text.split("\n")))
    #     lines_list.append(lines)
        # for line in lines:
        #     if line.strip() and len(line) == 3:
                # airport_codes.extend(isAirport(re.findall(pattern,line)))
    # flight_codes = send_to_LLM(lines_list)
    flight_codes = get_airport_pairs()
    # print(flight_codes)
    # print(f"flight codes for ${file_path}:",flight_codes)
    # # flight_codes = [{'from_airport': 'RDU', 'to_airport': 'CLT'}, {'from_airport': 'CLT', 'to_airport': 'SDF'}, {'from_airport': 'SDF', 'to_airport': 'CLT'}, {'from_airport': 'CLT', 'to_airport': 'RDU'}]
    # if flight_codes:
    #     for flight in flight_codes:
    #         # print(flight['from_airport'],flight['to_airport'])
    #         if (flight['from_airport'],flight['to_airport']) in existing_airports:
    #             model = existing_airports[(flight['from_airport'],flight['to_airport'])]
    #             print("Already exists:",flight['from_airport'],flight['to_airport'])
    #         elif (flight['to_airport'],flight['from_airport']) in existing_airports:
    #             model = existing_airports[(flight['to_airport'],flight['from_airport'])]
    #             print("Already exists:",(flight['to_airport'],flight['from_airport']))
    #         else:
    #             print('Sending to API')
    #             response = requests.post(f'https://airportgap.com/api/airports/distance?from={flight['from_airport']}&to={flight['to_airport']}')
    #             if response.status_code == 200:
    #                 data = response.json()
    #                 carbon_emission = calculate_carbon_emission(data['data']['attributes']['miles'])
    #                 model = EmissionModel(flight['from_airport'],
    #                                     flight['to_airport'],
    #                                     data['data']['attributes']['from_airport']['latitude'],
    #                                     data['data']['attributes']['to_airport']['latitude'],
    #                                     data['data']['attributes']['from_airport']['longitude'],  
    #                                     data['data']['attributes']['to_airport']['longitude'],
    #                                     data['data']['attributes']['miles'],
    #                                     carbon_emission)
    #                 existing_airports[(flight['from_airport'],flight['to_airport'])] = model
    # return list(existing_airports.values())
        # all_emission_data.append(model)
                
    # for i in range(len(airport_codes)-1):
    #     if airport_codes[i] == airport_codes[i+1]:
    #         continue
    #     if (airport_codes[i],airport_codes[i+1]) or (airport_codes[i+1],airport_codes[i]) in  existing_airports:
    #         continue
    #     else:
    #         response = requests.post(f'https://airportgap.com/api/airports/distance?from={airport_codes[i]}&to={airport_codes[i+1]}')
    #         if response.status_code == 200:
    #             data = response.json()
    #             carbon_emission = calculate_carbon_emission(data['data']['attributes']['miles'])
    #             model = EmissionModel(airport_codes[i],
    #                                   airport_codes[i+`1],
    #                                   data['data']['attributes']['from_airport']['latitude'],
    #                                   data['data']['attributes']['to_airport']['latitude'],
    #                                   data['data']['attributes']['from_airport']['longitude'],  
    #                                   data['data']['attributes']['to_airport']['longitude'],
    #                                   data['data']['attributes']['miles'],
    #                                   carbon_emission)
    #             all_emission_data.append(model)
    #             existing_airports[(airport_codes[i],airport_codes[i+1])] = model


def generate_ground_emission_report():
    # Read the CSV file
    ground_travel_dict = defaultdict(GroundTravelModel)
    with open('ground_travel_data.csv', mode='r') as file:
        reader = csv.reader(file)
        for i,row in enumerate(reader):
            id = row[0].strip()
            travel_begin_date = row[1].strip()
            travel_end_date = row[2].strip()
            travel_expense_category = row[3].strip()
            account = row[4].strip()
            project_id = row[5].strip()
            amount = row[6].replace(',', '').strip()
            if amount == 'AMOUNT':
                ground_travel_dict[i] = GroundTravelModel(id, travel_begin_date, travel_end_date, travel_expense_category, account, project_id, amount, 'CARBON EMISSION')
                continue
            
            dollar_spent = float(amount)
            carbon_emission = ground_carbon_emission(dollar_spent)
            ground_travel_dict[i] = GroundTravelModel(id, travel_begin_date, travel_end_date, travel_expense_category, account, project_id, amount, carbon_emission)
    return ground_travel_dict
            # print(f"Dollar spent: {dollar_spent}, Carbon emission: {carbon_emission}")

    
if __name__ == "__main__":

    load_dotenv(".env.development")
    #Creating Ground Travel Emission
    ground_travel_dict = generate_ground_emission_report()
    create_ground_emission_report(list(ground_travel_dict.values()))
    #Creating Air Travel Emission
    pdf_directory = "./pdfs"
    all_emission_data = []
    # for filename in os.listdir(pdf_directory):
    #     if filename.endswith(".pdf"):
    #         file_path = os.path.join(pdf_directory, filename)
    #         load_emission_data_from_csv('emission_report.csv')
    #         all_emission_data = extract_text_from_pdf(file_path)
    load_emission_data_from_csv('emission_report.csv')
    all_emission_data = extract_text_from_pdf("")        
    create_emission_report(all_emission_data)

    
