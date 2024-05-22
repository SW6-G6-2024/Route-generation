from .haversine import haversine
from .node_links import find_nodes_within_distance_or_nearest
from .classes import Node
from .graph_nodes import update_graph_with_connections

# Create a graph from the data and connect nodes
def create_graph(filtered_data: dict, isBestRoute: bool = False):
    """Create a graph from the filtered data.

    Args:
        filtered_data (dict): The filtered geojson data

    Returns:
        dict: A graph representing the connections between nodes
    """
    graph = {}
    for element in filtered_data['elements']:
        if 'nodes' in element and 'geometry' in element:
            create_vertex_connections(graph, element, isBestRoute)

    # Connect nearby nodes to the first lift nodes
    graph = find_nearby_and_connect_to_first_lift_nodes(graph, filtered_data, isBestRoute)

    # Connect stranded nodes
    graph = find_connections_for_stranded_nodes(graph, filtered_data, isBestRoute)

    return graph

def create_vertex_connections(graph: dict, element: dict, isBestRoute: bool = False):
    """Create connections between the nodes of an element in the graph.

    Args:
        graph (dict): The graph to add the connections to
        element (dict): An element from the filtered geojson data
    """
    piste_type = element.get('tags', {}).get('piste:type', None)

    edges = len(element['nodes']) - 1
    
    for i in range(edges):
        node_a = element['nodes'][i]
        node_b = element['nodes'][i + 1]
        lat1, lon1 = element['geometry'][i]['lat'], element['geometry'][i]['lon']
        lat2, lon2 = element['geometry'][i + 1]['lat'], element['geometry'][i + 1]['lon']
        distance = haversine(lat1, lon1, lat2, lon2)
        rating = element.get('rating', 0)
        
        # Weight is based on rating or lift penalty if looking for best route, otherwise distance 
        weight = (6 - rating) / edges if piste_type and isBestRoute else 20 / edges if isBestRoute else distance

        if node_a not in graph:
            graph[node_a] = []
        if node_b not in graph:
            graph[node_b] = []
				
        graph[node_a].append((node_b, weight))

def is_node_connected(graph: dict, node_id: int) -> list:
    """
    Check if a specific node is part of any other node's connections.

    Args:
        graph (dict): The graph to search for the specific node.
        node_id (int): The id of the node to check.

    Returns:
        list: A list of node ids that have the given node_id as a neighbor.
    """
    connections = []
    for key, neighbors in graph.items():
        for neighbor, _ in neighbors:
            if neighbor == node_id:
                connections.append(key)

    return connections

def check_lift_first_nodes_connections(graph: dict, lift_first_nodes: list) -> dict:
    """
    Check connections for all first lift nodes in the graph.

    Args:
        graph (dict): The graph representing the connections between nodes
        lift_first_nodes (list): A list of first lift node IDs

    Returns:
        dict: A dictionary with lift node IDs as keys and a list of node IDs that have connections to them
    """
    connections_status = {}
    for node_id in lift_first_nodes:
        connections_status[node_id] = is_node_connected(graph, node_id)
    return connections_status

def find_nearby_and_connect_to_first_lift_nodes(graph: dict, filtered_data: dict, isBestRoute: bool = False) -> dict:
    """Find nearby nodes and connect them to the first nodes of all lift elements.

    Args:
        graph (dict): The graph representing the connections between nodes
        filtered_data (dict): The filtered geojson data
        isBestRoute (bool): Whether to use the best route (rating-based) or shortest distance

    Returns:
        dict: The updated graph with connections to the first nodes of all lift elements
    """
    first_lift_nodes = find_lift_first_nodes(filtered_data)
    lift_connections_status = check_lift_first_nodes_connections(graph, first_lift_nodes)

    for node_id, connections in lift_connections_status.items():
        if not connections:  # Only process nodes that have no incoming connections
            # Find the coordinates of the first lift node
            stranded_lat, stranded_lon = find_stranded_node_coordinates(node_id, filtered_data)

            if stranded_lat is not None and stranded_lon is not None:
                node = Node(node_id, stranded_lat, stranded_lon)

                # Find nearby nodes and connect them to the first lift node
                nearby_nodes = find_nodes_within_distance_or_nearest(filtered_data['elements'], graph, node, isBestRoute)
                reverse_update_graph_with_connections(graph, node_id, nearby_nodes)

    return graph

def reverse_update_graph_with_connections(graph: dict, lift_node_id: int, nodes: list):
    """Update the graph by connecting nearby nodes to the first lift node.

    Args:
        graph (dict): The graph representing the connections between nodes
        lift_node_id (int): The first lift node to be connected to
        nodes (list): List of nearby nodes and their distances/weights
    """
    for nearby_node_id, weight_or_distance in nodes:
        if nearby_node_id not in graph:
            graph[nearby_node_id] = []
        if (lift_node_id, weight_or_distance) not in graph[nearby_node_id]:
            graph[nearby_node_id].append((lift_node_id, weight_or_distance))

def find_connections_for_stranded_nodes(graph: dict, filtered_data: dict, isBestRoute: bool = False):
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
                nodes = find_nodes_within_distance_or_nearest(filtered_data['elements'], graph, node, isBestRoute)
                update_graph_with_connections(graph, node_id, nodes, isBestRoute)
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

def find_lift_first_nodes(filtered_data: dict) -> list:
    """Find the first nodes of all lift elements in the filtered data.
    
    Args:
        filtered_data (dict): The filtered GeoJSON data

    Returns:
        list: A list of IDs of the first nodes of all lift elements
    """
    lift_first_nodes = []
    for element in filtered_data['elements']:
        if 'aerialway' in element.get('tags', {}):
            lift_first_nodes.append(element['nodes'][0])
    return lift_first_nodes
