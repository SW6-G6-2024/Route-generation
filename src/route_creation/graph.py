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


def create_vertex_connections(graph: dict, element: dict):
    """Create connections between the nodes of an element in the graph.

    Args:
        graph (dict): The graph to add the connections to
        element (dict): An element from the filtered geojson data
    """
    piste_type = element.get('tags', {}).get('piste:type', None)
    
    for i in range(len(element['nodes']) - 1):
        node_a = element['nodes'][i]
        node_b = element['nodes'][i + 1]
        lat1, lon1 = element['geometry'][i]['lat'], element['geometry'][i]['lon']
        lat2, lon2 = element['geometry'][i + 1]['lat'], element['geometry'][i + 1]['lon']
        distance = haversine(lat1, lon1, lat2, lon2)
        rating = element.get('rating', 0)
        weight = 20

        if piste_type:  # Check if piste_type is not None
            weight = 6 - rating

        if node_a not in graph:
            graph[node_a] = []
        if node_b not in graph:
            graph[node_b] = []
				
        graph[node_a].append((node_b, weight))


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
				nodes = find_nodes_within_distance_or_nearest(filtered_data['elements'], graph, node)
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
	for nearest_node, weight in nodes:
		if nearest_node != node_id and (nearest_node, weight) not in graph[node_id]:
			graph[node_id].append((nearest_node, weight))