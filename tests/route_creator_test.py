import pytest
import json
import os
from route_creation.route_creator import generate_shortest_route
from route_creation.haversine import haversine

def test_haversine_distance_known_points():
    # Coordinates of New York and London
    lat1, lon1 = 40.7128, -74.0060
    lat2, lon2 = 51.5074, -0.1278
    expected_distance = 5567
    calculated_distance = haversine(lat1, lon1, lat2, lon2)
    assert abs(calculated_distance - expected_distance) < 10

def test_generate_shortest_route():
    current_dir = os.path.dirname(__file__)
    json_file_path = os.path.join(current_dir, 'geoJsonData', 'isabergData.json')

    with open(json_file_path, 'r') as file:
      geojson_data = json.load(file)

    start = {'lat': 57.43440, 'lon': 13.61891}
    end = {'lat': 57.43408, 'lon': 13.60994}
    result = generate_shortest_route(start, end, geojson_data)

    expected_route = {
      'type': 'FeatureCollection',
      'features': [
        {'type': 'Feature', 
        'geometry': {'type': 'LineString', 'coordinates': [
          (13.6189104, 57.4343994),
          (13.6180357, 57.4337156),
          (13.617388, 57.4335146),
          (13.6175624, 57.4327791),
          (13.6177393, 57.4322106),
          (13.6178398, 57.4321149),
          (13.6171322, 57.4320809),
          (13.6155724, 57.4320059),
          (13.6139298, 57.431927),
          (13.611095, 57.4317907),
          (13.6103415, 57.4317545),
          (13.6101596, 57.4320558),
          (13.6103643, 57.4326649),
          (13.6102709, 57.4333236),
          (13.6099347, 57.4340827)]},
        'properties': {'description':
          'Shortest Path',
          'distance_km': 1.0107236513009064,
          'piste:type': 'downhill'}}]}
          
    compare_geojson(expected_route, result)

# Helper function to compare two GeoJSON objects
def compare_geojson(expected, result):
    assert expected['type'] == result['type']
    assert len(expected['features']) == len(result['features'])
    for exp_feature, res_feature in zip(expected['features'], result['features']):
        assert exp_feature['type'] == res_feature['type']
        assert exp_feature['geometry']['type'] == res_feature['geometry']['type']
        # Compare properties except 'distance_km'
        for key in exp_feature['properties']:
            if key != 'distance_km':
                assert exp_feature['properties'][key] == res_feature['properties'][key]
        # Special comparison for 'distance_km' with tolerance
        expected_distance = exp_feature['properties']['distance_km']
        result_distance = res_feature['properties']['distance_km']
        tolerance = expected_distance * 0.05  # 5% tolerance
        assert expected_distance - tolerance <= result_distance <= expected_distance + tolerance
