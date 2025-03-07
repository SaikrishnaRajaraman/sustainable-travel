from math import radians, degrees, sin, cos, tan, sqrt, atan, atan2, pi
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional

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
    unit: DistanceUnit = DistanceUnit.METERS
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
        raise ValueError(f"Error calculating distance: {str(e)}")