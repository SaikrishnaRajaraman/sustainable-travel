class HotelEmissionModel:
    def __init__(self, hotel_name=None, location=None,carbon_emission=0.0):
        self.hotel_name = hotel_name
        self.location = location
        self.carbon_emission = carbon_emission