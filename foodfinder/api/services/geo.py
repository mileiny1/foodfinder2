"""
Module for geographic calculations, including distance calculations between coordinates.
"""

import math

def haversine_m(lat1, lng1, lat2, lng2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point in degrees.
        lng1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lng2 (float): Longitude of the second point in degrees.

    Returns:
        int: Distance in meters between the two points.
    """
    # Earth's radius in meters
    R = 6371000
    # Convert latitudes to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    # Difference in latitudes and longitudes in radians
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    # Haversine formula calculation
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Return distance in meters, rounded to integer
    return int(R * c)

