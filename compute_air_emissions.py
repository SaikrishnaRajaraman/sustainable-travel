import pandas as pd
import numpy as np
import json
import requests
from utils.utils import calculate_carbon_emission
from pandas import ExcelWriter


def get_airports_from_athletics_data():

    file_path = 'nc_state_travel/NC_State_Air_travel.xlsx'

    data = pd.read_excel(file_path)

    airport_pairs = []

    for index, row in data.iterrows():
        transaction_type = row['Transaction Type']
        if transaction_type == 'Refund' or transaction_type == 'Exchange':
            continue
        airport_codes = row['Routing'].split(" ")
        pairs = [{"from_airport": airport_codes[i], "to_airport": airport_codes[i+1]} 
            for i in range(len(airport_codes) - 1)]
        airport_pairs.extend(pairs)
    return airport_pairs    

# print(data)


def get_airports_data_from_works_report():

    data = pd.read_excel("airline_data.xls", sheet_name="sheet_1")

    # Remove Null Air Leg
    data = data.dropna(subset=["Air Leg"])
    # currently only considering the amount >0
    data = data[data["Amount"] >= 0]

    # Remove the rows which have airport codes XXX

    # data = data[data['Air Origin Code'] == 'XXX']
    data = data[
        (data["Air Origin Code"] != "XXX") & (data["Air Destination Code"] != "XXX")
    ]

    airports = []
    idx = 0
    for index, row in data.iterrows():
        # if idx == 10:
        #     break
        
        origin_code = row["Air Origin Code"]
        destination_code = row["Air Destination Code"]
        airport_pair = {}
        airport_pair["from_airport"] = origin_code
        airport_pair["to_airport"] = destination_code
        airports.append(airport_pair)
   
    return airports