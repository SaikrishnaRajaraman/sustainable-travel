import pandas as pd
from models.ground_travel_model import GroundTravelModel
from utils.utils import ground_carbon_emission


def get_airport_pairs():

    file_path = 'nc_state_travel/NC_State_Motor_travel.xlsx'

    data = pd.read_excel(file_path)

    airport_pairs = []

    for index, row in data.iterrows():

        # airport_codes = row['Routing'].split(" ")
        # pairs = [{"from_airport": airport_codes[i], "to_airport": airport_codes[i+1]} 
        #     for i in range(len(airport_codes) - 1)]
        # airport_pairs.extend(pairs)

        ground_model = GroundTravelModel()
        ground_model.amount = row['Total Paid']
        carbon_emission = ground_carbon_emission(ground_model.amount)
        ground_model.carbon_emission = carbon_emission
        
    return airport_pairs  