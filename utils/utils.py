from models.emission_model import EmissionModel
from models.ground_travel_model import GroundTravelModel
from models.hotel_emission_model import HotelEmissionModel
import csv
import requests

def calculate_carbon_emission(miles):
    # For 1 passenger-mile travelled, 0.160308027 kgs of CO2 is emitted(kg)
    #emission = Miles*Emission/passenger-mile

    #GCD Correction
    kms = miles_to_kms(miles)

    if kms < 550:
        kms += 50
    elif kms > 550 and kms < 5500:
        kms += 100
    elif kms > 5500:
        kms += 125


    fuel = calculate_fuel(kms)

    #Average P/C = 82.53
    #2024 Load Factor = 83.39

    # Formula = CO2 emmissions = Fuel * (Passenger/Cargo Ratio / Total occupied seats) * Total Seats * 3.16
    

    return fuel * (82.53/83.39) * 100 * 3.16

def miles_to_kms(miles):
    kms = miles * 1.60934
    return kms

def calculate_fuel(distance):
    distances = [125, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500]
    fuel_consumptions = [1683.5, 3434.5, 4550, 6132.5, 7644.5, 10535, 13306, 15994.5, 45734.5, 52412, 58824.5, 64882, 70842.5, 76714.5, 82226, 87364, 92390.5, 107440, 112934, 118340]

    if distance <= distances[0]:
        return fuel_consumptions[0]
    elif distance >= distances[-1]:
        return fuel_consumptions[-1]
    else:
        for i in range(len(distances) - 1):
            if distances[i] <= distance < distances[i+1]:
                x0, x1 = distances[i], distances[i+1]
                y0, y1 = fuel_consumptions[i], fuel_consumptions[i+1]
                return y0 + (y1 - y0) * (distance - x0) / (x1 - x0)

    return 0  # This should never happen if the input is valid

    

def calculate_ground_carbon_emission(miles):
    # For 1 mile travelled, 0.404 kgs of CO2 is emitted
    return miles * 0.404

def calculate_ground_travel_miles(dollar_spent):
    # 1 mile travelled = $0.67 spent as per 2024 IRS Mileage Rates
    return dollar_spent / 0.67

def ground_carbon_emission(dollar_spent):
    miles = calculate_ground_travel_miles(dollar_spent)
    return calculate_ground_carbon_emission(miles)


def create_flight_emissions_report(emissions : list[EmissionModel]):
    file_name = "emission_report.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["S.No","Source IATA Code", "Destination IATA Code","Flight Company","Source Latitude", "Destination Latitude", "Source Longitude", "Destination Longitude", "Miles", "Carbon Emission"])
        index = 0
        # Write each emission model as a row in the CSV
        for emission in emissions:
            if emission is not None:
                 
                 writer.writerow([ index+1,
                emission.source_iata_code,
                emission.destination_iata_code,
                emission.flight_company,
                emission.latitude_source,
                emission.latitude_destination,
                emission.longitude_source,
                emission.longitude_destination,
                emission.miles,
                emission.carbon_emission
            ])
                 index += 1
            else:
                 print('Emissions is None')     
                 
        print(f"Emission report created successfully: {file_name}")

def create_ground_emission_report(emission: list[GroundTravelModel]):
    file_name = "ground_emissions_data.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['S.No','ID','Travel Begin Date','Travel End Date','Travel Category','Account','Project ID','Amount','Carbon Emission'])
        index = 0
        # Write each emission model as a row in the CSV
        for e in emission:
            if e is not None:
                 writer.writerow([ index +1,
                e.id if e.id is not None else "",
                e.travel_begin_date,
                e.travel_end_date,
                e.travel_expense_category,
                e.account,
                e.project_id,
                e.amount,
                e.carbon_emission
            ])
                 index += 1
            else:
                 print('Emission is None')     
                 
            

        print(f"Ground Emission report created successfully: {file_name}")

def create_hotel_emissions_report(emission: list[HotelEmissionModel]):
    file_name = "hotel_emissions_data.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['S.No','Hotel Name','Location','Hotel Type','Carbon Emission'])
        index = 0
        # Write each emission model as a row in the CSV
        for e in emission:
            if e is not None:
                 writer.writerow([ index +1,
                e.hotel_name,
                e.location,
                e.hotel_type,
                e.carbon_emission
            ])
                 index += 1
            else:
                 print('Emission is None')     
                 
            

        print(f"Hotel Emission report created successfully: {file_name}")
            
# def create_airports_database(airport_codes : set):
#     file_name = "airport_code.csv"
#     with open(file_name, mode='w', newline='') as file:
#         writer = csv.writer(file)

#         # Write the header row
#         writer.writerow(["Source IATA Code", "Destination IATA Code"])

#         # Write each emission model as a row in the CSV
#         for s,d in airport_codes:
#             writer.writerow([
#                 s,d
#             ])

#             print(f"Airport report created successfully: {file_name}")
        

def calculate_flight_emissions(trip):
    response = requests.post(f'https://airportgap.com/api/airports/distance?from={trip["from_airport"]}&to={trip["to_airport"]}')
    model = None
    if response.status_code == 200:
                data = response.json()
                carbon_emission = calculate_carbon_emission(data['data']['attributes']['miles'])
                print(carbon_emission)
                model = EmissionModel(trip['from_airport'],
                                    trip['to_airport'],
                                    trip['flight_company'],
                                    data['data']['attributes']['from_airport']['latitude'],
                                    data['data']['attributes']['to_airport']['latitude'],
                                    data['data']['attributes']['from_airport']['longitude'],  
                                    data['data']['attributes']['to_airport']['longitude'],
                                    data['data']['attributes']['miles'],
                                    carbon_emission)
    else:
         print(f"Error {response.status_code}: {response.text}")            
    return model            
