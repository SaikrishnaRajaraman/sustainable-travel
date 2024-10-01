from models.emission_model import EmissionModel
import csv

def calculate_carbon_emission(miles):
    return miles * 0.000621371 * 19.6

def calculate_ground_carbon_emission(miles):
    # For 1 mile travelled, 0.404 kgs of CO2 is emitted
    return miles * 0.404

def calculate_ground_travel_miles(dollar_spent):
    # 1 mile travelled = $0.67 spent as per 2024 IRS Mileage Rates
    return dollar_spent / 0.67

def calculate_ground_carbon_emission(dollar_spent):
    miles = calculate_ground_travel_miles(dollar_spent)
    return calculate_ground_carbon_emission(miles)


def create_emission_report(emissions : list[EmissionModel]):
    file_name = "emission_report.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(["Source Latitude", "Destination Latitude", "Source Longitude", "Destination Longitude", "Miles", "Carbon Emission"])

        # Write each emission model as a row in the CSV
        for emission in emissions:
            writer.writerow([
                emission.latitude_source,
                emission.latitude_destination,
                emission.longitude_source,
                emission.longitude_destination,
                emission.miles,
                emission.carbon_emission
            ])

            print(f"Emission report created successfully: {file_name}")
            
        
