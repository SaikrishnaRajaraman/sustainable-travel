import pandas as pd
import numpy as np
import json
import requests
from utils.utils import calculate_carbon_emission
from pandas import ExcelWriter


def get_airports_from_data():

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
        if idx == 10:
            break
        origin_code = row["Air Origin Code"]
        destination_code = row["Air Destination Code"]
        response = requests.post(f'https://airportgap.com/api/airports/distance?from={origin_code}&to={destination_code}')
        if response.status_code == 200:
            api_data = response.json()
            carbon_emission = calculate_carbon_emission(api_data['data']['attributes']['miles'])
            data.loc[index, 'Carbon Emission'] = carbon_emission
        airport_pair = {}
        airport_pair["from_airport"] = origin_code
        airport_pair["to_airport"] = destination_code
        airports.append(airport_pair)
        idx+=1
    print(data)
    # with ExcelWriter("airline_data.xls",mode="a",engine="xlwt",if_sheet_exists="replace") as writer:
    #     data.to_excel(writer, sheet_name='sheet_1')
    return airports
