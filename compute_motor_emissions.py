import pandas as pd
from models.ground_travel_model import GroundTravelModel
from utils.utils import ground_carbon_emission


def get_ground_travel_data_from_athletics():

    file_path = 'nc_state_travel/NC_State_Motor_travel.xlsx'

    data = pd.read_excel(file_path)

    ground_emissions_data = []

    for index, row in data.iterrows():

        # airport_codes = row['Routing'].split(" ")
        # pairs = [{"from_airport": airport_codes[i], "to_airport": airport_codes[i+1]} 
        #     for i in range(len(airport_codes) - 1)]
        # airport_pairs.extend(pairs)

        if row['Transaction Type'] == 'Refund':
            continue

        confirmation_number = row['Confirmation Number']

        if 'TIP' in confirmation_number or 'GRATUITY' in confirmation_number:
            continue

        ground_model = GroundTravelModel()
        ground_model.amount = row['Total Paid']
        ground_model.travel_begin_date = row['Start Date']
        ground_model.travel_end_date = row['End Date']

        carbon_emission = ground_carbon_emission(ground_model.amount)
        ground_model.carbon_emission = carbon_emission
        ground_emissions_data.append(ground_model)

        
    return ground_emissions_data


def generate_ground_emission_report():

    file_path = 'ground_travel_data.csv'
    data = pd.read_excel("2022-24-ncsu-pcard.xlsx", sheet_name="2022-24-ncsu-CAR")
    # Read the CSV file
    ground_travel_dict = []
    
    for i,row in data.iterrows():
            id = row[0].strip()
            travel_begin_date = row['Purchase Date']
            travel_end_date = row['Post Date']
            amount = row['Amount']
            # if amount == 'AMOUNT':
            #     ground_travel_dict.append(GroundTravelModel(id, travel_begin_date, travel_end_date, travel_expense_category, account, project_id, amount, 'CARBON EMISSION'))
            #     continue
            
            dollar_spent = float(amount)
            carbon_emission = ground_carbon_emission(dollar_spent)
            ground_travel_model = GroundTravelModel()
            ground_travel_model.id = id
            ground_travel_model.travel_begin_date = travel_begin_date
            ground_travel_model.travel_end_date = travel_end_date
            ground_travel_model.amount = dollar_spent
            ground_travel_model.carbon_emission = carbon_emission
            ground_travel_dict.append(ground_travel_model) 
    return ground_travel_dict