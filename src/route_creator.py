import requests
import math
import heapq
import json

from classes.node_processor import NodeProcessor
from classes.djikstra_data import DijkstraData

from utils.haversine import haversine


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


def find_nodes_within_distance_or_nearest(elements, graph, node, max_distance_km=0.2):
    existing_connections = {conn[0] for conn in graph.get(node.node_id, [])}
    processor = NodeProcessor(node, existing_connections, max_distance_km)

    for element in elements:
        element_type = 'lift' if 'aerialway' in element.get('tags', {}) else 'piste'
        for i, geom in enumerate(element.get('geometry', [])):
            processor.process_element_node(element, i, geom, element_type)

    closest_nodes = processor.closest_nodes
    if not closest_nodes and processor.nearest_node_details['nearest_node_id']:
        closest_nodes.append((processor.nearest_node_details['nearest_node_id'], processor.nearest_node_details['min_distance']))

    return closest_nodes

def get_shortest_path_geojson(filtered_data, shortest_path, shortest_distance):
    # Create a lookup table for node IDs to their coordinates
    node_id_to_coords = {}
    for element in filtered_data['elements']:
        for i, node_id in enumerate(element['nodes']):
            lat, lon = element['geometry'][i]['lat'], element['geometry'][i]['lon']
            node_id_to_coords[node_id] = (lat, lon)

    # Initialize an empty GeoJSON FeatureCollection
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Check if there is a shortest path to convert
    if shortest_path:
        # Extract coordinates from the node IDs in the shortest path
        path_coordinates = [node_id_to_coords.get(node_id, ("Unknown", "Unknown")) for node_id in shortest_path]

        # Ensure coordinates are not 'Unknown' before attempting to switch to avoid errors
        path_coordinates = [(lon, lat) for lat, lon in path_coordinates if (lat, lon) != ("Unknown", "Unknown")]

        # Create a GeoJSON Feature for the LineString representing the shortest path
        path_feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": path_coordinates
            },
            "properties": {
                "description": "Shortest Path",
                "distance_km": shortest_distance,
                "piste:type": "downhill"
            }
        }

        # Add the path Feature to the FeatureCollection
        geojson_data["features"].append(path_feature)

    return geojson_data
    

def generate_shortest_route(start, end, overpassData):
  filtered_data = overpassData

  if 'elements' in filtered_data and len(filtered_data['elements']) <= 0:
    print("No elements found in the filtered_data")

  graph = create_graph(filtered_data)
  graph = find_connections_for_stranded_nodes(graph, filtered_data)

  shortest_path, shortest_distance = dijkstra(graph, start, end)

  # Use the function and print the GeoJSON data
  geojson_data = get_shortest_path_geojson(filtered_data, shortest_path, shortest_distance)

  return geojson_data