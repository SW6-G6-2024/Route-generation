import pytest
import json
import os
from route_creation.route_creator import haversine, generate_shortest_route

def test_haversine_distance_known_points():
    # Coordinates of New York and London
    lat1, lon1 = 40.7128, -74.0060
    lat2, lon2 = 51.5074, -0.1278
    expected_distance = 5567  # Approximate distance in kilometers
    calculated_distance = haversine(lat1, lon1, lat2, lon2)
    assert abs(calculated_distance - expected_distance) < 100  # Allowing some margin for calculation differences

def test_generate_shortest_route():
    # Path to the JSON file relative to the test file
    current_dir = os.path.dirname(__file__)
    json_file_path = os.path.join(current_dir, 'geoJsonData', 'isabergData.json')

    # Load the JSON data from the file
    with open(json_file_path, 'r') as file:
      geojson_data = json.load(file)

    # Now, geojson_data contains the data loaded from isabergData.json
    # Use this data to test generate_shortest_route
    start = 360881297
    end = 360873433
    result = generate_shortest_route(start, end, geojson_data)

    expected_route = {
      'features': [{
        'geometry': {
          'coordinates': [
            (13.6189104, 57.4343994), 
            (13.6174589, 57.4336116), 
            (13.6128704, 57.4357791),
            (13.614203, 57.4342486)
          ],
          'type': 'LineString'
        },
        'properties': {
          'description': 'Shortest Path',
          'distance_km': 0.6767107552322736,  # Adjust the distance as necessary
          'piste:type': 'downhill'
        },
        'type': 'Feature'
      }],
      'type': 'FeatureCollection'
    }
    assert result == expected_route
