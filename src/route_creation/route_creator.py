from .dijkstra import dijkstra
from .graph import create_graph, find_connections_for_stranded_nodes, find_stranded_node_coordinates
from .haversine import haversine


def get_shortest_path_geojson(filtered_data:dict, shortest_path:list, shortest_distance:float):
	"""Converts the shortest path to a GeoJSON FeatureCollection.

	Args:
		filtered_data (dict): The filtered GeoJSON data from the Overpass API
		shortest_path (list): The list of node IDs in the shortest path
		shortest_distance (float): The distance of the shortest path

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
	if shortest_path:
		# Extract coordinates from the node IDs in the shortest path
		path_coordinates = [node_id_to_coords.get(node_id, ("Unknown", "Unknown")) for node_id in shortest_path]

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
				"distance_km": shortest_distance,
				"piste:type": "downhill"
			}
		}

		# Add the path Feature to the FeatureCollection
		geojson_data["features"].append(path_feature)

	return geojson_data
	

def generate_shortest_route(start: dict[float,float], end: dict[float,float], overpassData: dict):
	"""Generates the shortest route between two points using the Dijkstra algorithm.

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

	graph = create_graph(filtered_data)
	graph = find_connections_for_stranded_nodes(graph, filtered_data)

	shortest_path, shortest_distance = dijkstra(graph, start_node, end_node)

	# Use the function and print the GeoJSON data
	geojson_data = get_shortest_path_geojson(filtered_data, shortest_path, shortest_distance)

	return geojson_data

def find_nearest_node(coords, elements):
	"""Finds the id of the nearest node in a graph to the given coordinates.

	Args:
		coords (dict[float,float]): The coordinates to find the nearest node to

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
			lat, lon = element['geometry'][0]['lat'], element['geometry'][0]['lon']
			distance = haversine(coords.get('lat'), coords.get('lon'), lat, lon)
			if distance < min_distance:
				min_distance = distance
				nearest_node = node
	return nearest_node