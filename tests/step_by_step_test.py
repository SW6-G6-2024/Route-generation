import pytest
import json
import os

from src.route_creation.step_by_step import step_by_step_guide

def test_step_by_step_guide():
  # Path to the JSON file relative to the test file
  current_dir = os.path.dirname(__file__)
  json_file_path = os.path.join(current_dir, 'geoJsonData', 'isabergData.json')
  shortest_path_file_path = os.path.join(current_dir, 'geoJsonData', 'shortestPath.json')

  # Load the shortest path data from the file
  with open(shortest_path_file_path, 'r') as file:
    shortest_path_expected = json.load(file)

  # Load the JSON data from the file
  with open(json_file_path, 'r') as file:
    geojson_data = json.load(file)
  

  result = step_by_step_guide(shortest_path_expected, geojson_data)
  assert result == ['Norrliften', 'Transporten', 'Gamla backen', 'Slalombacken', 'Isabergsexpressen', 'Familjebacken', 'Toppliftarna']