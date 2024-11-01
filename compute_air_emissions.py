import pandas as pd


def get_airport_pairs():

    file_path = 'nc_state_travel/NC_State_Air_travel.xlsx'

    data = pd.read_excel(file_path)

    airport_pairs = []

    for index, row in data.iterrows():
        airport_codes = row['Routing'].split(" ")
        pairs = [{"from_airport": airport_codes[i], "to_airport": airport_codes[i+1]} 
            for i in range(len(airport_codes) - 1)]
        airport_pairs.extend(pairs)

    return airport_pairs    

# print(data)