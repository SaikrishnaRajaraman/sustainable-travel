import pymupdf  # PyMuPDF
import airportsdata
import re
import requests
from utils.utils import ground_carbon_emission,calculate_flight_emissions
from collections import defaultdict
import csv
import os
from models.emission_model import EmissionModel
from models.ground_travel_model import GroundTravelModel
from utils.utils import calculate_carbon_emission, create_flight_emissions_report,create_ground_emission_report,create_hotel_emissions_report
import csv
from openai import OpenAI
import json
from dotenv import load_dotenv
from compute_air_emissions import get_airports_from_athletics_data,get_airports_data_from_works_report
from compute_motor_emissions import get_ground_travel_data_from_athletics,generate_ground_emission_report
from compute_hotel_emissions import get_hotel_data

#Load the airports data using IATA code
airports = airportsdata.load('IATA')
pattern = r'\b[A-Z]{3}\b'

existing_airports = defaultdict(EmissionModel)
# Open the PDF file

def isAirport(airport_code):
    airport_codes = [code for code in airport_code if code in airports]
    return airport_codes

# def getPDFfromURL():

#     login_payload = {
#         'username': 'dummy',
#         'password': 'dummy'
#     }
#     URL = ''

#     session = requests.Session()

#     login_response = session.post(URL, data=login_payload)

#     if login_response.status_code == 200:
#         print("Logged in successfully!")

#         response = session.get(URL, stream=True)

#         # Check if the request was successful
#         if response.status_code == 200:
#             # Print the content of the page (HTML source)
#             print(response.text)
#         else:
#             print(f"Failed to access the page. Status code: {response.status_code}")

#         # content_type = response.headers.get('Content-Type', '')
#         # if 'application/pdf' in content_type:
#         #     print("PDF found")
#         # else: 
#         #     print()
#     return
#     # Raise an exception for HTTP errors (4xx or 5xx)
#     response.raise_for_status()

#     content_type = response.headers.get('Content-Type', '')

#     if 'application/pdf' in content_type:
#         print("PDF found")
#     return
#     # Check if the response contains a PDF
#     content_type = response.headers.get('Content-Type', '')
#     response = requests.get(URL)
#     if response.status_code == 200:
#         with open('downloaded_pdf.pdf', 'wb') as f:
#             for chunk in response.iter_content(chunk_size=1024):
#                     if chunk:  # Filter out keep-alive new chunks
#                         print(chunk)
#                         f.write(chunk)
#         print("PDF downloaded successfully")
#     else:
#         print(f"Failed to download PDF. Status code: {response.status_code}")

def load_emission_data_from_csv(csv_file):
    emissions_data = defaultdict(EmissionModel)
    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                source = row['Source IATA Code']
                destination = row['Destination IATA Code']
                flight_company = row['Flight Company']
                source_lat = row['Source Latitude']
                destination_lat = row['Destination Latitude']
                source_long = row['Source Longitude']
                destination_long = row['Destination Longitude']
                miles = row['Miles']
                carbon_emission = row['Carbon Emission']

                emissions_data[(source, destination)] = EmissionModel(source, destination,flight_company, source_lat, destination_lat, source_long, destination_long, miles, carbon_emission)

    else:
        print(f"File {csv_file} does not exist")

    return emissions_data   

# def send_to_LLM(lines):
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     client = OpenAI(api_key = openai_api_key)
    
#     content = '''
#     Extract all the airport legs for the travel based on the given content and return it in this required format?
#     [{
#         "from_airport": "IATA Code",
#         "to_airport": "IATA Code"
#     }]
#     '''
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": ".".join(lines)},
#                 {"role": "user", "content": content}
#             ],
#             max_tokens=150,
#             )
#         output = response.choices[0].message.content
#         output_lines = output.splitlines()
#         output_lines = output_lines[1:-1]
#         output = "\n".join(output_lines)
#         # print(output)
#         flight_data = json.loads(output)
#         return flight_data
#     except Exception as e:
#         print(f"An error occurred: {e}")

def extract_works_data():
    return get_airports_data_from_works_report()

# def extract_text_from_pdf(file_path):

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



            # print(f"Dollar spent: {dollar_spent}, Carbon emission: {carbon_emission}")

    
if __name__ == "__main__":

    load_dotenv(".env.development")
    #Creating Ground Travel Emission
    # ground_travel_dict = generate_ground_emission_report()
    # create_ground_emission_report(list(ground_travel_dict.values()))
    #Creating Air Travel Emission
    pdf_directory = "./pdfs"
    all_emission_data = []
    existing_airports = load_emission_data_from_csv('emission_report.csv')
   

    # # # Calculating works flight data
    works_flight_data = extract_works_data()

    # # Calculating the athletics flight data
    athletics_flight_data = get_airports_from_athletics_data()

    airports_data = []
    airports_data.extend(works_flight_data)
    airports_data.extend(athletics_flight_data)
   
    final_emissions_data = []


    index = 0
    for trip in airports_data:
        print(f"Processing {index + 1} of {len(airports_data)} ({(index + 1) / len(airports_data) * 100:.2f}%)")
        index += 1
        if (trip['from_airport'],trip['to_airport'],trip['flight_company']) in existing_airports:
            model = existing_airports[(trip['from_airport'],trip['to_airport'],trip['flight_company'])]
            final_emissions_data.append(model)
        else:
            if trip['from_airport'] and trip['to_airport'] :
                model = calculate_flight_emissions(trip)
                if model:
                    existing_airports[(trip['from_airport'],trip['to_airport'],trip['flight_company'])] = model
                    final_emissions_data.append(model)

                 

               

    print(final_emissions_data)
    create_flight_emissions_report(final_emissions_data)    


    # Calculating Ground Travel emissions

    # all_ground_travel = []
    # athletics_ground_travel = get_ground_travel_data_from_athletics()
    # works_ground_travel = generate_ground_emission_report()


    # all_ground_travel.extend(athletics_ground_travel)
    # all_ground_travel.extend(works_ground_travel)

    # create_ground_emission_report(all_ground_travel)

    # hotel_emissions_data = get_hotel_data()
    # create_hotel_emissions_report(hotel_emissions_data)

        


    