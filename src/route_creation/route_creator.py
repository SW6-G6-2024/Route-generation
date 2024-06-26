from .dijkstra import dijkstra
from .graph import create_graph, find_connections_for_stranded_nodes
from .haversine import haversine
from .step_by_step import step_by_step_guide


def path_to_geojson(filtered_data:dict, path:list, weight:float):
	"""Converts the shortest path to a GeoJSON FeatureCollection.

	Args:
		filtered_data (dict): The filtered GeoJSON data from the Overpass API
		path (list): The list of node IDs in the shortest path
		weight (float): The weight of the shortest path

	Returns:
		dict: A GeoJSON FeatureCollection representing the shortest path
	"""
	
	# Create a lookup table for node IDs to their coordinates
	node_id_to_coords = {}
	for element in filtered_data['elements']:
		for i, node_id in enumerate(element['nodes']):
			lat, lon = element['geometry'][i]['lat'], element['geometry'][i]['lon']
			node_id_to_coords[node_id] = (lat, lon)

	# Initialize an empty GeoJSON FeatureCollection
	geojson_data = {
		"type": "FeatureCollection",
		"features": []
	}

	# Check if there is a shortest path to convert
	if path:
		# Extract coordinates from the node IDs in the shortest path
		path_coordinates = [node_id_to_coords.get(node_id, ("Unknown", "Unknown")) for node_id in path]

		# Ensure coordinates are not 'Unknown' before attempting to switch to avoid errors
		path_coordinates = [(lon, lat) for lat, lon in path_coordinates if (lat, lon) != ("Unknown", "Unknown")]

		# Create a GeoJSON Feature for the LineString representing the shortest path
		path_feature = {
			"type": "Feature",
			"geometry": {
				"type": "LineString",
				"coordinates": path_coordinates
			},
			"properties": {
				"description": "Shortest Path",
				"weight": weight,
				"piste:type": "downhill"
			}
		}

		# Add the path Feature to the FeatureCollection
		geojson_data["features"].append(path_feature)

	return geojson_data
	

def generate_rated_route(start: dict[float,float], end: dict[float,float], isBestRoute: bool, overpassData: dict):
	"""Generates the most optimal route between two points using the Dijkstra algorithm.

	Args:
		start (dict[float,float]): The coordinates of the start point
		end (dict[float,float]): The coordinates of the end point
		overpassData (dict): The GeoJSON data from the Overpass API

	Returns:
		dict: A GeoJSON FeatureCollection representing the shortest path
	"""  
	filtered_data = overpassData

	if 'elements' in filtered_data and len(filtered_data['elements']) <= 0:
		print("No elements found in the filtered_data")

	start_node = find_nearest_node(start, filtered_data)
	end_node = find_nearest_node(end, filtered_data)

	graph = create_graph(filtered_data, isBestRoute)
	graph = find_connections_for_stranded_nodes(graph, filtered_data, isBestRoute)

	shortest_path, weight = dijkstra(graph, start_node, end_node)

	# Use the function and print the GeoJSON data
	geojson_data = path_to_geojson(filtered_data, shortest_path, weight)

	# Creates the step-by-step guide
	step_guide = step_by_step_guide(shortest_path, filtered_data)

	return [geojson_data, step_guide]

def find_nearest_node(coords: dict[float,float], elements: dict):
	"""Finds the id of the nearest node in a graph to the given coordinates.

	Args:
		coords (dict[float,float]): The coordinates to find the nearest node to
		elements (dict): The elements from the filtered GeoJSON data

	Returns:
		int: The id of the nearest node
	"""
	nearest_node = None
	min_distance = float('inf')
	for element in elements['elements']:
		for i, node in enumerate(element['nodes']):
			# Skip if the current node in the middle of a lift
			if 'aerialway' in element.get('tags', {}) and i != 0:
				continue
			lat, lon = element['geometry'][i]['lat'], element['geometry'][i]['lon']
			distance = haversine(coords.get('lat'), coords.get('lon'), lat, lon)
			if distance < min_distance:
				min_distance = distance
				nearest_node = node
	return nearest_node