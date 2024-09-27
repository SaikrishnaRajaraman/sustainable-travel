class EmissionModel:
    def __init__(self, latitude_source, latitude_destination, longitude_source, longitude_destination, miles, carbon_emission):
        self.latitude_source = latitude_source
        self.latitude_destination = latitude_destination
        self.longitude_source = longitude_source
        self.longitude_destination = longitude_destination
        self.miles = miles
        self.carbon_emission = carbon_emission
        