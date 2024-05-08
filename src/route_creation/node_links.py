from .haversine import haversine
from .classes import Node, NearestNode, NodeResults


def find_nodes_within_distance_or_nearest(elements: dict, graph: dict, node: Node, isBestRoute: bool = False):
	"""Find nodes within 100 meters of the stranded node or the nearest node outside this range.

	Args:
			elements (dict): The elements from the filtered geojson data
			graph (dict): The graph representing the connections between nodes
			node (Node): The stranded node

	Returns:
			list: A list of the closest nodes to the stranded node
	"""
	node_results = NodeResults()

	# Retrieve existing connections for the stranded node to exclude them
	existing_connections = {conn[0] for conn in graph.get(node.node_id, [])}

	# Find the nearest node within 100 meters
	for element in elements:
		node_results = find_nearest_nodes(
			node, node_results, existing_connections, element, isBestRoute)

	# Use either the weight or distance for the nearest node
	weight = node_results.nearest_node.weight
 
	# If no nodes are found within 100 meters, include the nearest found node outside this range
	if not node_results.closest_nodes and node_results.nearest_node.node_id:
		node_results.closest_nodes.append(
			(node_results.nearest_node.node_id, weight))

	return node_results.closest_nodes


def find_nearest_nodes(node: Node, node_results: NodeResults, existing_connections: dict, element: dict, isBestRoute: bool = False):
	"""Find the nearest nodes to a stranded node within 100 meters.

	Args:
			node (Node): The stranded node
			node_results (NodeResults): The results of the node search
			existing_connections (dict): The existing connections for the stranded node
			element (dict): An element from the filtered geojson data

	Returns:
			NodeResults: The updated results of the node search
	"""
	# Determine the type of element (piste or lift)
	element_type = 'lift' if 'aerialway' in element.get(
		'tags', {}) else 'piste'

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

			# Check distance against the 100m criterion for all nodes
		node_results.nearest_node, node_results.closest_nodes = check_distance(
			node_results, node_id, distance, isBestRoute)
	return node_results


def check_distance(node_results: NodeResults, node_id: int, distance: float, isBestRoute: bool = False):
	"""Check if the distance to a node is less than the current nearest node.

	Args:
			node_results (NodeResults): The results of the node search
			node_id (int): The ID of the node
			distance (float): The distance to the node

	Returns:
			tuple[NearestNode, list]: The updated results of the node search, and the list of the closest nodes
	"""
	max_distance_km = 0.1
	weight = 6 if isBestRoute else distance
 
	if distance <= max_distance_km:
		if distance < node_results.nearest_node.weight:
			node_results.nearest_node.weight = weight
			node_results.nearest_node.node_id = node_id
			# For lifts, since we continue the loop for i != 0, this will only append the first node
		node_results.closest_nodes.append((node_id, weight))
	return NearestNode(node_results.nearest_node.weight, node_results.nearest_node.node_id), node_results.closest_nodes
