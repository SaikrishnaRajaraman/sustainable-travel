import csv
class EmissionModel:
    def __init__(self, source_iata_code, destination_iata_code,flight_company, latitude_source, latitude_destination, longitude_source, longitude_destination, miles, carbon_emission):
        self.source_iata_code = source_iata_code
        self.destination_iata_code = destination_iata_code
        self.flight_company = flight_company
        self.latitude_source = latitude_source
        self.latitude_destination = latitude_destination
        self.longitude_source = longitude_source
        self.longitude_destination = longitude_destination
        self.miles = miles
        self.carbon_emission = carbon_emission
        