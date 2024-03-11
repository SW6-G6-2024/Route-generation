import numpy as np

def haversine(lat1, lon1, lats, lons):
    """
    Calculate the Haversine distance between a point and multiple points provided as arrays.
    
    Args:
    lat1, lon1: Coordinates of the initial point in degrees.
    lats, lons: Numpy arrays of latitudes and longitudes of the points to compare against.
    
    Returns:
    distances: Numpy array of distances from (lat1, lon1) to each point in (lats, lons).
    """
    R = 6371.0  # Radius of the Earth in kilometers
    lat1, lon1 = np.radians(lat1), np.radians(lon1)
    lats, lons = np.radians(lats), np.radians(lons)
    
    dlat = lats - lat1
    dlon = lons - lon1
    
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lats) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    distances = R * c
    return distances