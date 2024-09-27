from models.emission_model import EmissionModel
import csv

def calculate_carbon_emission(miles):
    return miles * 0.000621371 * 19.6

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
            
        
