from models.emission_model import EmissionModel
from models.ground_travel_model import GroundTravelModel
import csv

def calculate_carbon_emission(miles):
    # For 1 passenger-mile travelled, 0.160308027 kgs of CO2 is emitted(kg)
    #emission = Miles*Emission/passenger-mile
    return miles * 0.160308027

def calculate_ground_carbon_emission(miles):
    # For 1 mile travelled, 0.404 kgs of CO2 is emitted
    return miles * 0.404

def calculate_ground_travel_miles(dollar_spent):
    # 1 mile travelled = $0.67 spent as per 2024 IRS Mileage Rates
    return dollar_spent / 0.67

def ground_carbon_emission(dollar_spent):
    miles = calculate_ground_travel_miles(dollar_spent)
    return calculate_ground_carbon_emission(miles)


def create_emission_report(emissions : list[EmissionModel]):
    file_name = "emission_report.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Source IATA Code", "Destination IATA Code", "Source Latitude", "Destination Latitude", "Source Longitude", "Destination Longitude", "Miles", "Carbon Emission"])

        # Write each emission model as a row in the CSV
        for emission in emissions:
            writer.writerow([
                emission.source_iata_code,
                emission.destination_iata_code,
                emission.latitude_source,
                emission.latitude_destination,
                emission.longitude_source,
                emission.longitude_destination,
                emission.miles,
                emission.carbon_emission
            ])

        print(f"Emission report created successfully: {file_name}")

def create_ground_emission_report(emission: list[GroundTravelModel]):
    file_name = "ground_travel_data.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write each emission model as a row in the CSV
        for e in emission:
            writer.writerow([
                e.id,
                e.travel_begin_date,
                e.travel_end_date,
                e.travel_expense_category,
                e.account,
                e.project_id,
                e.amount,
                e.carbon_emission
            ])

        print(f"Ground Emission report created successfully: {file_name}")
            
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
        
