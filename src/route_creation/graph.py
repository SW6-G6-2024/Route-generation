import numpy as np
from .haversine import haversine
from .node_links import find_nodes_within_distance_or_nearest
from .classes import Node

# Create a graph from the data and connect nodes
def create_graph(filtered_data: dict):
	"""Create a graph from the filtered data.

	Args:
		filtered_data (dict): The filtered geojson data

	Returns:
		dict: A graph representing the connections between nodes
	"""
	graph = {}
	for element in filtered_data['elements']:
		if 'nodes' in element and 'geometry' in element:
			create_vertex_connections(graph, element)
	return graph

def create_vertex_connections(graph, element):
    """Optimized version using NumPy for distance calculations."""
    node_ids = element['nodes']
    geometry = np.array([(geom['lat'], geom['lon']) for geom in element['geometry']])
    
    # Calculate distances between consecutive nodes in a vectorized manner
    lat1, lon1 = geometry[:-1, 0], geometry[:-1, 1]
    lat2, lon2 = geometry[1:, 0], geometry[1:, 1]
    distances = haversine(lat1, lon1, lat2, lon2)
    
    for i, distance in enumerate(distances):
        node_a, node_b = node_ids[i], node_ids[i + 1]
        if node_a not in graph:
            graph[node_a] = []
        if node_b not in graph:
            graph[node_b] = []
        graph[node_a].append((node_b, distance))

def find_connections_for_stranded_nodes(graph: dict, filtered_data: dict):
	"""Find connections for stranded nodes in the graph (nodes with no connections).

	Args:
		graph (dict): The graph representing the connections between nodes
		filtered_data (dict): The filtered geoJson data

	Returns:
		dict: The updated graph with connections for stranded nodes
	"""
	for node_id in graph:
		if not graph[node_id]:  # This node is stranded
			stranded_lat, stranded_lon = find_stranded_node_coordinates(node_id, filtered_data)
			if stranded_lat is not None and stranded_lon is not None:
				node = Node(node_id, stranded_lat, stranded_lon)
				nodes = find_nodes_within_distance_or_nearest(filtered_data, graph, node)
				update_graph_with_connections(graph, node_id, nodes)
	return graph

def find_stranded_node_coordinates(node_id: int, filtered_data: dict):
	"""Find the coordinates of a stranded node in the filtered data.

	Args:
		node_id (int): The ID of the stranded node
		filtered_data (dict): The filtered geojson data

	Returns:
		float, float: The latitude and longitude of the stranded node
	"""
	for element in filtered_data['elements']:
		if node_id in element['nodes']:
			index = element['nodes'].index(node_id)
			return element['geometry'][index]['lat'], element['geometry'][index]['lon']
	return None, None

def update_graph_with_connections(graph, node_id, nodes):
	for nearest_node, distance in nodes:
		if nearest_node != node_id and (nearest_node, distance) not in graph[node_id]:
			graph[node_id].append((nearest_node, distance))