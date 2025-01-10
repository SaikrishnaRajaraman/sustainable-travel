class HotelEmissionModel:
    def __init__(self, hotel_name=None, location=None,carbon_emission=0.0,hotel_type=None):
        self.hotel_name = hotel_name
        self.location = location
        self.carbon_emission = carbon_emission
        self.hotel_type = hotel_type