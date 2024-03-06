import heapq
class DijkstraData:
    """
    Class to encapsulate data structures used in Dijkstra's algorithm.
    """
    def __init__(self, start_node, graph):
        self.distances = {node: float('infinity') for node in graph}
        self.distances[start_node] = 0
        self.previous_nodes = {node: None for node in graph}
        self.priority_queue = [(0, start_node)]

def dijkstra(graph, start, end):
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
  
def explore_neighbors(graph, current_node, current_distance, dijkstra_data):
  for neighbor, weight in graph[current_node]:
      distance = current_distance + weight
        
      # If the distance to the neighbor is shorter by taking this path
      if distance < dijkstra_data.distances[neighbor]:
        dijkstra_data.distances[neighbor] = distance
        dijkstra_data.previous_nodes[neighbor] = current_node
        heapq.heappush(dijkstra_data.priority_queue, (distance, neighbor))
