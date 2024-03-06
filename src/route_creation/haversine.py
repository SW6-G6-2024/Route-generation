import math

def haversine(lat1:float, lon1:float, lat2:float, lon2:float):
	"""Calculates the distance between two coordinates using the Haversine formula.
	Args:
			lat1 (float): The latitude of the first coordinate
			lon1 (float): The longitude of the first coordinate
			lat2 (float): The latitude of the second coordinate
			lon2 (float): The longitude of the second coordinate

	Returns:
			float: The distance between the two coordinates in kilometers
	"""
  # Radius of the Earth in kilometers
	R = 6371.0

  # Convert latitude and longitude from degrees to radians
	lat1_rad = math.radians(lat1)
	lon1_rad = math.radians(lon1)
	lat2_rad = math.radians(lat2)
	lon2_rad = math.radians(lon2)

  # Difference in coordinates
	dlat = lat2_rad - lat1_rad
	dlon = lon2_rad - lon1_rad

  # Haversine formula
	a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

	distance = R * c

	return distance