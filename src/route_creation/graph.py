from .haversine import haversine
from .node_links import find_nodes_within_distance_or_nearest

# Create a graph from the data and connect nodes
def create_graph(filtered_data):
  graph = {}
  for element in filtered_data['elements']:
    if 'nodes' in element and 'geometry' in element:
      create_vertex_connections(graph, element)
  return graph

def create_vertex_connections(graph, element):
  """
  Create connections between nodes in the graph based on the given element.
  """
  for i in range(len(element['nodes']) - 1):
    node_a = element['nodes'][i]
    node_b = element['nodes'][i + 1]
    lat1, lon1 = element['geometry'][i]['lat'], element['geometry'][i]['lon']
    lat2, lon2 = element['geometry'][i + 1]['lat'], element['geometry'][i + 1]['lon']
    distance = haversine(lat1, lon1, lat2, lon2)

    if node_a not in graph:
        graph[node_a] = []
    if node_b not in graph:
        graph[node_b] = []

    graph[node_a].append((node_b, distance))

class Node:
  def __init__(self, node_id, lat, lon):
    self.node_id = node_id
    self.lat = lat
    self.lon = lon

def find_connections_for_stranded_nodes(graph, filtered_data):
  for node_id in graph:
    if not graph[node_id]:  # This node is stranded
      stranded_lat, stranded_lon = find_stranded_node_coordinates(node_id, filtered_data)
      if stranded_lat is not None and stranded_lon is not None:
        node = Node(node_id, stranded_lat, stranded_lon)
        nodes = find_nodes_within_distance_or_nearest(filtered_data['elements'], graph, node)
        update_graph_with_connections(graph, node_id, nodes)
  return graph

def find_stranded_node_coordinates(node_id, filtered_data):
  for element in filtered_data['elements']:
    if node_id in element['nodes']:
      index = element['nodes'].index(node_id)
      return element['geometry'][index]['lat'], element['geometry'][index]['lon']
  return None, None

def update_graph_with_connections(graph, node_id, nodes):
  for nearest_node, distance in nodes:
    if nearest_node != node_id and (nearest_node, distance) not in graph[node_id]:
      graph[node_id].append((nearest_node, distance))