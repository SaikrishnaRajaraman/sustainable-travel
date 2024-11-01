import pandas as pd
import numpy as np
import json

def get_airports_from_data():

    data = pd.read_excel('airline_data.xls', sheet_name='sheet_1')

    # Remove Null Air Leg
    data = data.dropna(subset=['Air Leg'])

    data = data[data['Amount'] >= 0]

    # Remove the rows which have airport codes XXX

    # data = data[data['Air Origin Code'] == 'XXX']
    data = data[(data['Air Origin Code'] != 'XXX') & (data['Air Destination Code'] != 'XXX')]

    airports = []

    for index, row in data.iterrows():
        origin_code = row['Air Origin Code']
        destination_code = row['Air Destination Code']
        airport_pair = {}
        airport_pair['from_airport'] = origin_code
        airport_pair['to_airport'] = destination_code

        airports.append(airport_pair)


    return json.dumps(airports, indent=4)


def get_hotels_from_data():

    data = pd.read_excel('airline_data.xls', sheet_name='sheet_1')

