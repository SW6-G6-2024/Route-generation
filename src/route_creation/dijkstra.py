import heapq
from .classes import DijkstraData

def dijkstra(graph:dict, start:int, end:int):
	"""
 Find the shortest path between two nodes in a graph using Dijkstra's algorithm based on some weight.

	Args:
		graph (dict): The graph to search for the shortest path
		start (int): The id of the start node
		end (int): The id of the end node

	Returns:
		dict, float: A list of node ids representing the shortest path, and the distance of the shortest path in kilometers
	"""
	dijkstra_data = DijkstraData(start, graph)
	
	while dijkstra_data.priority_queue:
		# Get the node with the smallest distance
		current_distance, current_node = heapq.heappop(dijkstra_data.priority_queue)
		
		# If we've reached the end node, we can stop
		if current_node == end:
			break
		
		explore_neighbors(graph, current_node, current_distance, dijkstra_data)

	# Reconstruct the shortest path
	path = []
	current = end
	while current is not None:
		path.append(current)
		current = dijkstra_data.previous_nodes[current]
	path.reverse()
	
	return path, dijkstra_data.distances[end]
	
def explore_neighbors(graph:dict, current_node: int, current_distance: float, dijkstra_data: DijkstraData):
	"""Searches for the shortest path to the neighbors of the current node.

	Args:
			graph (dict): The graph to search for the shortest path
			current_node (int): The id of the current node
			current_distance (float): The distance to the current node
			dijkstra_data (DijkstraData): The data structures used in Dijkstra's algorithm. Contains the distances, previous nodes, and priority queue
	"""
	for neighbor, weight in graph[current_node]:
		#print("await", weight)
		distance = current_distance + weight
			
		# If the distance to the neighbor is shorter by taking this path
		if distance < dijkstra_data.distances[neighbor]:
			dijkstra_data.distances[neighbor] = distance
			dijkstra_data.previous_nodes[neighbor] = current_node
			heapq.heappush(dijkstra_data.priority_queue, (distance, neighbor))
