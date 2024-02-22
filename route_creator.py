import requests
import math
import heapq

def dijkstra(graph, start, end):
  # Initialize distances with infinity, except for the start node
  distances = {node: float('infinity') for node in graph}
  distances[start] = 0
  
  # Priority queue: stores tuples of (distance, node)
  queue = [(0, start)]
  
  # To store the path taken
  previous_nodes = {node: None for node in graph}
  
  while queue:
    # Get the node with the smallest distance
    current_distance, current_node = heapq.heappop(queue)
    
    # If we've reached the end node, we can stop
    if current_node == end:
      break
    
    for neighbor, weight in graph[current_node]:
      distance = current_distance + weight
        
      # If the distance to the neighbor is shorter by taking this path
      if distance < distances[neighbor]:
        distances[neighbor] = distance
        previous_nodes[neighbor] = current_node
        heapq.heappush(queue, (distance, neighbor))

  # Reconstruct the shortest path
  path = []
  current = end
  while current is not None:
    path.append(current)
    current = previous_nodes[current]
  path.reverse()
  
  return path, distances[end]

def haversine(lat1, lon1, lat2, lon2):
  # Radius of the Earth in kilometers
  R = 6371.0

  # Convert latitude and longitude from degrees to radians
  lat1_rad = math.radians(lat1)
  lon1_rad = math.radians(lon1)
  lat2_rad = math.radians(lat2)
  lon2_rad = math.radians(lon2)

  # Difference in coordinates
  dlat = lat2_rad - lat1_rad
  dlon = lon2_rad - lon1_rad

  # Haversine formula
  a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

  distance = R * c

  return distance

def find_nodes_within_distance_or_nearest(stranded_node_lat, stranded_node_lon, elements, stranded_node_id, graph, max_distance_km=0.05):
  closest_node_per_element = {}
  min_distance = float('inf')
  nearest_node_id = None
  nearest_node_element_id = None  # Track the element ID of the nearest node for distinction

  # Retrieve existing connections for the stranded node to exclude them
  existing_connections = {conn[0] for conn in graph.get(stranded_node_id, [])}

  for element in elements:
    element_type = 'lift' if 'aerialway' in element.get('tags', {}) else 'piste'
    element_id = element['id']

    for i, geom in enumerate(element.get('geometry', [])):
      lat, lon = geom['lat'], geom['lon']
      node_id = element['nodes'][i]
      # Skip if the current node is the stranded node itself or already connected
      if node_id == stranded_node_id or node_id in existing_connections:
        continue

      distance = haversine(stranded_node_lat, stranded_node_lon, lat, lon)

      # For lifts, only the first node matters, and it should not be more than 100m away
      if element_type == 'lift' and i == 0 and distance <= 0.1:
        if (distance < min_distance or nearest_node_element_id != element_id):
          min_distance = distance
          nearest_node_id = node_id
          nearest_node_element_id = element_id

      # For pistes, find the closest node within max_distance_km distance, avoiding duplicates
      elif element_type == 'piste' and distance <= max_distance_km:
        if element_id not in closest_node_per_element or distance < closest_node_per_element[element_id][1]:
          closest_node_per_element[element_id] = (node_id, distance)

      elif element_type == 'piste' and (nearest_node_element_id is None or distance < min_distance):
        # Update nearest node if this node is closer and not a lift already considered
        min_distance = distance
        nearest_node_id = node_id
        nearest_node_element_id = element_id

  # Compile the results, ensuring no duplicates and excluding already connected nodes
  result_nodes = list(closest_node_per_element.values())

  # If no nodes are found within the preferred distance, consider the nearest node
  if not result_nodes and nearest_node_id:
    result_nodes.append((nearest_node_id, min_distance))

  return result_nodes



south, west, north, east = 61.29560770030594, 12.127237063661534, 61.33240275253347, 12.266869460358693  # Replace these values with your coordinates

query = f"""
[out:json];
(
  // Fetch downhill pistes within the bounding box
  way["piste:type"="downhill"]({south},{west},{north},{east});
  // Fetch all ski lifts within the bounding box
  way["aerialway"]({south},{west},{north},{east});
);
out geom;
"""

response = requests.get(f"https://overpass-api.de/api/interpreter?data={requests.utils.quote(query)}")

if not response.ok:
  raise Exception('Network response was not ok')

data = response.json()

filtered_data = [
    element for element in data['elements']
    if (
        ('piste:type' in element['tags'] and element['tags']['piste:type'] == 'downhill' and
         element['tags'].get('piste:difficulty') not in ['freeride', 'extreme'] and
         (element['tags'].get('ref') or element['tags'].get('name')))
        or
        ('aerialway' in element['tags'])
    )
]

filtered_data = {'elements': filtered_data}

if 'elements' in filtered_data and len(filtered_data['elements']) <= 0:
  print("No elements found in the filtered_data")

# Create a graph from the data with already connected nodes
graph = {}
for element in filtered_data['elements']:
  if 'nodes' in element and 'geometry' in element:
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


for node_id in graph:
  if not graph[node_id]:  # This node is stranded
    # Find the stranded node's latitude and longitude directly from its first occurrence in the elements
    found = False
    for element in filtered_data['elements']:
      if node_id in element['nodes']:
        index = element['nodes'].index(node_id)
        stranded_lat = element['geometry'][index]['lat']
        stranded_lon = element['geometry'][index]['lon']
        found = True
        break  # Exit after finding the first occurrence

    if found:
      # Now call the function with the updated signature, including 'graph' and 'node_id'
      nodes = find_nodes_within_distance_or_nearest(stranded_lat, stranded_lon, filtered_data['elements'], node_id, graph)

      for nearest_node, distance in nodes:
        if nearest_node != node_id and (graph[node_id].__contains__((nearest_node, distance)) == False):
          graph[node_id].append((nearest_node, distance))

start_node = 5875336381
end_node = 347047601
shortest_path, shortest_distance = dijkstra(graph, start_node, end_node)
print("Shortest path:", shortest_path)
print("Shortest distance:", shortest_distance, "km")

for node_id in graph:
  if not graph[node_id]:
    print(f"Stranded Node {node_id} has no connections")
  else:
    print(f"Node {node_id} connects to nodes {graph[node_id]}")