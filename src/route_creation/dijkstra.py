import heapq
from .classes import DijkstraData

def dijkstra(graph: dict, start: int, end: int):
    """
    Find the most optimal path between two nodes in a graph using Dijkstra's algorithm based on some weight.

    Args:
        graph (dict): The graph to search for the path
        start (int): The id of the start node
        end (int): The id of the end node

    Returns:
        dict, float: A list of node ids representing the path, and the weight of the path
    """
    dijkstra_data = DijkstraData(start, graph)

    while dijkstra_data.priority_queue:
        # Get the node with the lowest weight
        current_weight, current_node = heapq.heappop(dijkstra_data.priority_queue)
        
        # If we've reached the end node, we can stop
        if current_node == end:
            break
        
        explore_neighbors(graph, current_node, current_weight, dijkstra_data)

    # Reconstruct the path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = dijkstra_data.previous_nodes[current]
    path.reverse()
 
    return path, dijkstra_data.weights[end]

def explore_neighbors(graph: dict, current_node: int, current_weight: float, dijkstra_data: DijkstraData):
    """Searches for the best path to the neighbors of the current node.

    Args:
        graph (dict): The graph to search for the path
        current_node (int): The id of the current node
        current_weight (float): The weight of the current node
        dijkstra_data (DijkstraData): The data structures used in Dijkstra's algorithm. Contains the weights, previous nodes, and priority queue
    """
    for neighbor, weight in graph[current_node]:
        new_weight = current_weight + weight
        
        # If the distance to the neighbor is shorter by taking this path
        if new_weight < dijkstra_data.weights[neighbor]:
            dijkstra_data.weights[neighbor] = new_weight
            dijkstra_data.previous_nodes[neighbor] = current_node
            heapq.heappush(dijkstra_data.priority_queue, (new_weight, neighbor))
