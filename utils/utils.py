from models.emission_model import EmissionModel
from models.ground_travel_model import GroundTravelModel
from models.hotel_emission_model import HotelEmissionModel
import csv
import requests
import pandas as pd
from dataclasses import dataclass
from math import radians, degrees, sin, cos, tan, sqrt, atan, atan2, pi
from enum import Enum
from typing import Tuple, Optional

def calculate_carbon_emission(miles):
    # For 1 passenger-mile travelled, 0.160308027 kgs of CO2 is emitted(kg)
    #emission = Miles*Emission/passenger-mile

    #GCD Correction
    kms = miles_to_kms(miles)

    if kms < 550:
        kms += 50
    elif kms > 550 and kms < 5500:
        kms += 100
    elif kms > 5500:
        kms += 125


    fuel = calculate_fuel(kms)

    #Average P/C = 82.53
    #2024 Load Factor = 83.39

    # Formula = CO2 emmissions = Fuel * (Passenger/Cargo Ratio / Total occupied seats) * Total Seats * 3.16
    

    return fuel * (82.53/83.39) * 100 * 3.16

def miles_to_kms(miles):
    kms = miles * 1.60934
    return kms

def calculate_fuel(distance):
    distances = [125, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500]
    fuel_consumptions = [1683.5, 3434.5, 4550, 6132.5, 7644.5, 10535, 13306, 15994.5, 45734.5, 52412, 58824.5, 64882, 70842.5, 76714.5, 82226, 87364, 92390.5, 107440, 112934, 118340]

    if distance <= distances[0]:
        return fuel_consumptions[0]
    elif distance >= distances[-1]:
        return fuel_consumptions[-1]
    else:
        for i in range(len(distances) - 1):
            if distances[i] <= distance < distances[i+1]:
                x0, x1 = distances[i], distances[i+1]
                y0, y1 = fuel_consumptions[i], fuel_consumptions[i+1]
                return y0 + (y1 - y0) * (distance - x0) / (x1 - x0)

    return 0  # This should never happen if the input is valid

    

def calculate_ground_carbon_emission(miles):
    # For 1 mile travelled, 0.404 kgs of CO2 is emitted
    return miles * 0.404

def calculate_ground_travel_miles(dollar_spent):
    # 1 mile travelled = $0.67 spent as per 2024 IRS Mileage Rates
    return dollar_spent / 0.67

def ground_carbon_emission(dollar_spent):
    miles = calculate_ground_travel_miles(dollar_spent)
    return calculate_ground_carbon_emission(miles)


def create_flight_emissions_report(emissions : list[EmissionModel]):
    file_name = "emission_report.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["S.No","Source IATA Code", "Destination IATA Code","Flight Company","Source Latitude", "Destination Latitude", "Source Longitude", "Destination Longitude", "Miles", "Carbon Emission"])
        index = 0
        # Write each emission model as a row in the CSV
        for emission in emissions:
            if emission is not None:
                 
                 writer.writerow([ index+1,
                emission.source_iata_code,
                emission.destination_iata_code,
                emission.flight_company,
                emission.latitude_source,
                emission.latitude_destination,
                emission.longitude_source,
                emission.longitude_destination,
                emission.miles,
                emission.carbon_emission
            ])
                 index += 1
            else:
                 print('Emissions is None')     
                 
        print(f"Emission report created successfully: {file_name}")

def create_ground_emission_report(emission: list[GroundTravelModel]):
    file_name = "ground_emissions_data.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['S.No','ID','Travel Begin Date','Travel End Date','Travel Category','Account','Project ID','Amount','Carbon Emission'])
        index = 0
        # Write each emission model as a row in the CSV
        for e in emission:
            if e is not None:
                 writer.writerow([ index +1,
                e.id if e.id is not None else "",
                e.travel_begin_date,
                e.travel_end_date,
                e.travel_expense_category,
                e.account,
                e.project_id,
                e.amount,
                e.carbon_emission
            ])
                 index += 1
            else:
                 print('Emission is None')     
                 
            

        print(f"Ground Emission report created successfully: {file_name}")

def create_hotel_emissions_report(emission: list[HotelEmissionModel]):
    file_name = "hotel_emissions_data.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['S.No','Hotel Name','Location','Hotel Type','Carbon Emission'])
        index = 0
        # Write each emission model as a row in the CSV
        for e in emission:
            if e is not None:
                 writer.writerow([ index +1,
                e.hotel_name,
                e.location,
                e.hotel_type,
                e.carbon_emission
            ])
                 index += 1
            else:
                 print('Emission is None')     
                 
            

        print(f"Hotel Emission report created successfully: {file_name}")
            
# def create_airports_database(airport_codes : set):
#     file_name = "airport_code.csv"
#     with open(file_name, mode='w', newline='') as file:
#         writer = csv.writer(file)

#         # Write the header row
#         writer.writerow(["Source IATA Code", "Destination IATA Code"])

#         # Write each emission model as a row in the CSV
#         for s,d in airport_codes:
#             writer.writerow([
#                 s,d
#             ])

#             print(f"Airport report created successfully: {file_name}")

class DistanceUnit(Enum):
    """Available units for distance measurement"""
    METERS = "meters"
    KILOMETERS = "kilometers"
    MILES = "miles"
    NAUTICAL_MILES = "nautical_miles"
    FEET = "feet"

@dataclass
class GeoCoordinate:
    """Represents a geographic coordinate with validation"""
    latitude: float
    longitude: float

    def __post_init__(self):
        if not isinstance(self.latitude, (int, float)) or not isinstance(self.longitude, (int, float)):
            raise ValueError("Coordinates must be numeric values")
        if self.latitude < -90 or self.latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if self.longitude < -180 or self.longitude > 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")

@dataclass
class DistanceResult:
    """Contains the results of distance calculations"""
    distance: float
    initial_bearing: float
    final_bearing: float
    unit: DistanceUnit

def convert_distance(meters: float, unit: DistanceUnit) -> float:
    """Convert distance from meters to specified unit"""
    conversion_factors = {
        DistanceUnit.METERS: 1,
        DistanceUnit.KILOMETERS: 0.001,
        DistanceUnit.MILES: 0.000621371,
        DistanceUnit.NAUTICAL_MILES: 0.000539957,
        DistanceUnit.FEET: 3.28084
    }
    return meters * conversion_factors[unit]



def calculate_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float, 
    unit: DistanceUnit = DistanceUnit.MILES
) -> Optional[DistanceResult]:
    """
    Calculate the distance between two points on Earth using Vincenty's formula.
    
    Parameters:
    lat1, lon1: First point's latitude and longitude in degrees
    lat2, lon2: Second point's latitude and longitude in degrees
    unit: Desired output unit (default: meters)
    
    Returns:
    DistanceResult object containing distance, bearings, and unit
    
    Raises:
    ValueError: If coordinates are invalid or calculation fails
    """
    try:
        # Validate coordinates
        point1 = GeoCoordinate(lat1, lon1)
        point2 = GeoCoordinate(lat2, lon2)
        
        # WGS-84 ellipsoidal constants
        a = 6378137.0  # semi-major axis in meters
        f = 1/298.257223563  # flattening
        b = (1 - f) * a  # semi-minor axis
        
        # Convert to radians
        phi1 = radians(point1.latitude)
        phi2 = radians(point2.latitude)
        lambda1 = radians(point1.longitude)
        lambda2 = radians(point2.longitude)
        
        # Handle identical points
        if phi1 == phi2 and lambda1 == lambda2:
            return DistanceResult(0.0, 0.0, 0.0, unit)
        
        # Calculate reduced latitudes (beta)
        U1 = atan((1 - f) * tan(phi1))
        U2 = atan((1 - f) * tan(phi2))
        
        sin_U1 = sin(U1)
        cos_U1 = cos(U1)
        sin_U2 = sin(U2)
        cos_U2 = cos(U2)
        
        # Initialize lambda for iteration
        L = lambda2 - lambda1
        lambda_new = L
        
        # Iteration limits
        max_iterations = 100
        tolerance = 1e-12  # about 0.06mm
        
        # Iterate until convergence
        for iteration in range(max_iterations):
            sin_lambda = sin(lambda_new)
            cos_lambda = cos(lambda_new)
            
            sin_sigma = sqrt((cos_U2 * sin_lambda) ** 2 + 
                           (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2)
            
            if sin_sigma == 0:
                return DistanceResult(0.0, 0.0, 0.0, unit)
                
            cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
            sigma = atan2(sin_sigma, cos_sigma)
            
            sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
            cos_sq_alpha = 1 - sin_alpha ** 2
            
            if cos_sq_alpha == 0:
                cos_2sigma_m = 0
            else:
                cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos_sq_alpha
                
            C = f/16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
            
            lambda_old = lambda_new
            lambda_new = L + (1 - C) * f * sin_alpha * (sigma + C * sin_sigma * 
                        (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))
            
            if abs(lambda_new - lambda_old) < tolerance:
                break
        else:
            raise ValueError("Vincenty formula failed to converge")
        
        # Calculate final variables
        u_sq = cos_sq_alpha * (a ** 2 - b ** 2) / b ** 2
        A = 1 + u_sq/16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
        B = u_sq/1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
        
        delta_sigma = (B * sin_sigma * 
                      (cos_2sigma_m + B/4 * 
                       (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) - 
                        B/6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * 
                        (-3 + 4 * cos_2sigma_m ** 2))))
        
        distance_meters = b * A * (sigma - delta_sigma)
        
        # Convert distance to requested unit
        distance = convert_distance(distance_meters, unit)
        
        # Calculate bearings
        initial_bearing = degrees(
            atan2(cos_U2 * sin_lambda, 
                  cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda)
        ) % 360
        
        final_bearing = degrees(
            atan2(cos_U1 * sin_lambda,
                  -sin_U1 * cos_U2 + cos_U1 * sin_U2 * cos_lambda)
        ) % 360
        
        return DistanceResult(distance, initial_bearing, final_bearing, unit)
        
    except Exception as e:
        print(e)
        raise ValueError(f"Error calculating distance: {str(e)}")
        

def calculate_flight_emissions(trip):
    file_name = "data/airports.csv"
    df = pd.read_csv(file_name)

    def get_coordinates(iata_code):
        result = df[df['iata'] == iata_code]
        if not result.empty:
            latitude = result.iloc[0]['latitude']
            longitude = result.iloc[0]['longitude']
            return latitude, longitude
        else:
            return 0, 0
        

    lat1,lon1 = get_coordinates(trip['from_airport'])
    lat2,lon2 = get_coordinates(trip['to_airport'])

    if (lat1 == 0 and lon1 == 0) or (lat2 == 0 and lon2 == 0):
        return None

    print("From : ",trip['from_airport'])
    print("To : ",trip['to_airport'])
    print("Lat1 : ",lat1)
    print("Lon1 : ",lon1)
    print("Lat2 : ",lat2)
    print("Lon2 : ",lon2)

        
    distance_miles = calculate_distance(
                lat1=lat1,
                lon1=lon1,
                lat2=lat2,
                lon2=lon2,
                unit=DistanceUnit.MILES
            ).distance     
        
    model = None
    carbon_emission = calculate_carbon_emission(distance_miles)
    print(carbon_emission)
    model = EmissionModel(trip['from_airport'],
                                    trip['to_airport'],
                                    trip['flight_company'],
                                    lat1,
                                    lat2,
                                    lon1,  
                                    lon2,
                                    distance_miles,
                                    carbon_emission)          
    return model            