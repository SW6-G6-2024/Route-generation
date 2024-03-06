from .haversine import haversine

class NearestNode:
    def __init__(self, distance=float('inf'), node_id=None):
        self.distance = distance
        self.node_id = node_id

class NodeResults:
    def __init__(self):
        self.closest_nodes = []
        self.nearest_node = NearestNode()
      
def find_nodes_within_distance_or_nearest(elements, graph, node):
    closest_nodes = []
    min_distance = float('inf')
    nearest_node_id = None
            
    node_results = NodeResults()

    # Retrieve existing connections for the stranded node to exclude them
    existing_connections = {conn[0] for conn in graph.get(node.node_id, [])}

    # Find the nearest node within 100 meters
    for element in elements:
      node_results = find_nearest_nodes(node, node_results, existing_connections, element)

    # If no nodes are found within 100 meters, include the nearest found node outside this range
    if not node_results.closest_nodes and node_results.nearest_node.node_id:
        node_results.closest_nodes.append((nearest_node_id, min_distance))

    return node_results.closest_nodes

def find_nearest_nodes(node, node_results, existing_connections, element):
    # Determine the type of element (piste or lift)
    element_type = 'lift' if 'aerialway' in element.get('tags', {}) else 'piste'
    
    # Iterate over the nodes of the element to find the nearest node
    for i, geom in enumerate(element.get('geometry', [])):
        lat, lon = geom['lat'], geom['lon']
        node_id = element['nodes'][i]
          # Skip if the current node is the stranded node itself or already connected
        if node_id == node.node_id or node_id in existing_connections:
            continue

        distance = haversine(node.lat, node.lon, lat, lon)

          # For lifts, ensure only the first node is considered for connections
        if element_type == 'lift' and i != 0:
            continue  # Skip all nodes except the first node of a lift

          # Check distance against the 50m criterion for all nodes
        node_results.nearest_node, node_results.closest_nodes = check_distance(node_results, node_id, distance)
    return node_results
  

def check_distance(node_results, node_id, distance):
	max_distance_km = 0.1
	if distance <= max_distance_km:
			if distance < node_results.nearest_node.distance:
					node_results.nearest_node.distance = distance
					node_results.nearest_node.node_id = node_id
						# For lifts, since we continue the loop for i != 0, this will only append the first node
			node_results.closest_nodes.append((node_id, distance))
	return NearestNode(node_results.nearest_node.distance, node_results.nearest_node.node_id), node_results.closest_nodes