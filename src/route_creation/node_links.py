import numpy as np
from .haversine import haversine
from .classes import Node, NearestNode, NodeResults


def find_nodes_within_distance_or_nearest(elements, graph, node):
    """Find nodes within 100 meters of the stranded node or the nearest node outside this range using NumPy.
    
    Args:
        elements (dict): The elements from the filtered geojson data
        graph (dict): The graph representing the connections between nodes
        node (Node): The stranded node

    Returns:
        NodeResults: A list of the closest nodes to the stranded node
    """
    node_results = NodeResults()

    # Retrieve existing connections for the stranded node to exclude them
    existing_connections = {conn[0] for conn in graph.get(node.node_id, [])}
    
    # Extract all node positions and IDs from elements
    all_node_ids = []
    all_lats = []
    all_lons = []
    
    for element in elements['elements']:
        for i, geom in enumerate(element.get('geometry', [])):
            lat, lon = geom['lat'], geom['lon']
            node_id = element['nodes'][i]
            if node_id != node.node_id and node_id not in existing_connections:
                all_node_ids.append(node_id)
                all_lats.append(lat)
                all_lons.append(lon)
                
    # Convert to NumPy arrays
    all_lats = np.array(all_lats)
    all_lons = np.array(all_lons)
    distances = haversine(node.lat, node.lon, all_lats, all_lons)
    
    # Find nodes within 100 meters
    within_distance_indices = np.where(distances <= 0.1)[0]
    
    # Update nearest and closest nodes
    for index in within_distance_indices:
        node_results.closest_nodes.append((all_node_ids[index], distances[index]))
    
    # If no nodes found within 100m, find the nearest node outside this range
    if not node_results.closest_nodes:
        nearest_index = np.argmin(distances)
        node_results.nearest_node.distance = distances[nearest_index]
        node_results.nearest_node.node_id = all_node_ids[nearest_index]
        node_results.closest_nodes.append((node_results.nearest_node.node_id, node_results.nearest_node.distance))
    
    return node_results.closest_nodes