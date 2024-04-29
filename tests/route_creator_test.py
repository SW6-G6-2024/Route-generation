import pytest
import json
import os

from src.route_creation.haversine import haversine
from src.route_creation.route_creator import generate_rated_route


def test_haversine_distance_known_points():
		# Coordinates of New York and London
		lat1, lon1 = 40.7128, -74.0060
		lat2, lon2 = 51.5074, -0.1278
		expected_distance = 5567  # Approximate distance in kilometers
		calculated_distance = haversine(lat1, lon1, lat2, lon2)
		# Allowing some margin for calculation differences
		assert abs(calculated_distance - expected_distance) < 10


def test_generate_shortest_route():
		# Path to the JSON file relative to the test file
		current_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(current_dir, 'geoJsonData', 'isabergData.json')

		# Load the JSON data from the file
		with open(json_file_path, 'r') as file:
			geojson_data = json.load(file)

		# Now, geojson_data contains the data loaded from isabergData.json
		# Use this data to test generate_shortest_route
		start = {'lat': 57.43440, 'lon': 13.61891}
		end = {'lat': 57.43408, 'lon': 13.60994}
		isBestRoute = False
		result = generate_rated_route(start, end, isBestRoute, geojson_data)
		
		expected_route = {
			'type': 'FeatureCollection', 
			'features': [
				{
					'type': 'Feature', 
		      'geometry': {
						'type': 'LineString', 
						'coordinates': [
        			(13.6189639, 57.434509), (13.6182169, 57.4349174), (13.6175045, 57.4353069),
							(13.6171025, 57.4355267), (13.6165525, 57.4359116), (13.6159986, 57.4362036),
							(13.6154772, 57.4364532), (13.6147205, 57.4368846), (13.6137803, 57.4374205),
							(13.6137921, 57.436526), (13.6141096, 57.4363852), (13.6143565, 57.4363376),
							(13.6146144, 57.4361248), (13.6147761, 57.4360025), (13.6147879, 57.4358684),
							(13.6150679, 57.4350086), (13.6153914, 57.4348824), (13.6167944, 57.4346954),
							(13.617416, 57.4344698), (13.6179757, 57.4341638), (13.6180238, 57.4339349),
							(13.6180357, 57.4337156), (13.617388, 57.4335146), (13.6175624, 57.4327791),
							(13.6177393, 57.4322106), (13.6178398, 57.4321149), (13.6171322, 57.4320809),
							(13.6155724, 57.4320059), (13.6139298, 57.431927), (13.611095, 57.4317907),
							(13.6103415, 57.4317545), (13.6101596, 57.4320558), (13.6103643, 57.4326649),
							(13.6102709, 57.4333236), (13.6099347, 57.4340827), (13.6094631, 57.4342844)
            ]
					}, 
					'properties': {
						'description': 'Shortest Path', 
						'distance_km': 1.9531140006376295, 
						'piste:type': 'downhill'
					}
				}
			]	
    }

		assert result[0] == expected_route
