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
                        (13.6135492, 57.4365511), (13.6131763, 57.4363491), (13.6126619, 57.4361137),
                        (13.6124373, 57.4359717), (13.6123371, 57.4359084), (13.6122503, 57.4358178),
                        (13.611834, 57.4353907), (13.6114646, 57.4350506), (13.6113121, 57.4349155),
                        (13.6109853, 57.4346261), (13.6094631, 57.4342844)
                    ]
                },
                'properties': {
                    'description': 'Shortest Path',
                    'weight': 0.9113198207803078,
                    'piste:type': 'downhill'
                }
            }
        ]
    }

		assert result[0] == expected_route
