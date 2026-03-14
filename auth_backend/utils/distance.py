"""
Distance calculation utilities using Haversine formula
For GPS coordinates (lat/lon) → distance in meters
Suitable for college project explanation (Earth radius approx).
"""

import math
from typing import Tuple

EARTH_RADIUS_KM = 6371.0  # Average Earth radius in km

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two GPS points.
    Returns distance in METERS.
    Formula: Explainable trig (sin/haversine) for viva.
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (math.sin(dlat / 2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance_km = EARTH_RADIUS_KM * c
    return distance_km * 1000  # Convert to meters

def calculate_eta(distance_m: float, avg_speed_kmph: float = 40) -> float:
    """
    ETA in minutes: distance / speed.
    Default ambulance speed 40 km/h (explainable).
    """
    distance_km = distance_m / 1000
    time_hours = distance_km / avg_speed_kmph
    return round(time_hours * 60, 1)  # Minutes

if __name__ == "__main__":
    # Demo
    print("🧭 Distance Utils Demo")
    dist = haversine_distance(17.3850, 78.4867, 17.3900, 78.4900)  # ~500m Hyderabad
    print(f"Distance: {dist:.0f}m")
    print(f"ETA (40km/h): {calculate_eta(dist):.1f} min")

