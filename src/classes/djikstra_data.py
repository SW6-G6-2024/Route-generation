class DijkstraData:
    """
    Class to encapsulate data structures used in Dijkstra's algorithm.
    """
    def __init__(self, start_node, graph):
        self.distances = {node: float('infinity') for node in graph}
        self.distances[start_node] = 0
        self.previous_nodes = {node: None for node in graph}
        self.priority_queue = [(0, start_node)]