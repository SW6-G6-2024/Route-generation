class DijkstraData:
	"""
 		A class to store the data structures used in Dijkstra's algorithm.
	"""
	def __init__(self, start_node: float, graph: dict):
		self.distances = {node: float('infinity') for node in graph}
		self.distances[start_node] = 0
		self.previous_nodes = {node: None for node in graph}
		self.priority_queue = [(0, start_node)]
  
class Node:
	"""A class to represent a node in the graph. 

	args:
		node_id (int): The ID of the node
		lat (float): The latitude of the node
		lon (float): The longitude of the node
	"""
	def __init__(self, node_id, lat, lon):
		self.node_id = node_id
		self.lat = lat
		self.lon = lon

class NearestNode:
	"""A class to represent the nearest node to a stranded node.
	
	args:
		distance (float): The distance to the nearest node
		node_id (int): The ID of the nearest node
	"""
	def __init__(self, distance=float('inf'), node_id: int=None):
		self.distance = distance
		self.node_id = node_id

class NodeResults:
	"""A class to store the results of the node search.
	Contains the nearest node and a list of the closest nodes.
	"""
	def __init__(self):
		self.closest_nodes = []
		self.nearest_node = NearestNode()