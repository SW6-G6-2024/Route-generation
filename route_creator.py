import requests
import math
import heapq
import json

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


# Create a graph from the data and connect nodes
def create_graph(filtered_data):
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
  return graph


def find_connections_for_stranded_nodes(graph, filtered_data):
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
  return graph


def find_nodes_within_distance_or_nearest(stranded_node_lat, stranded_node_lon, elements, stranded_node_id, graph, max_distance_km=0.2):
    closest_nodes = []
    min_distance = float('inf')
    nearest_node_id = None

    # Retrieve existing connections for the stranded node to exclude them
    existing_connections = {conn[0] for conn in graph.get(stranded_node_id, [])}

    for element in elements:
        element_type = 'lift' if 'aerialway' in element.get('tags', {}) else 'piste'

        for i, geom in enumerate(element.get('geometry', [])):
            lat, lon = geom['lat'], geom['lon']
            node_id = element['nodes'][i]
            # Skip if the current node is the stranded node itself or already connected
            if node_id == stranded_node_id or node_id in existing_connections:
                continue

            distance = haversine(stranded_node_lat, stranded_node_lon, lat, lon)

            # For lifts, ensure only the first node is considered for connections
            if element_type == 'lift' and i != 0:
                continue  # Skip all nodes except the first node of a lift

            # Check distance against the 50m criterion for all nodes
            if distance <= max_distance_km:
                if distance < min_distance:
                    min_distance = distance
                    nearest_node_id = node_id
                # For lifts, since we continue the loop for i != 0, this will only append the first node
                closest_nodes.append((node_id, distance))

    # If no nodes are found within 50 meters, include the nearest found node outside this range
    if not closest_nodes and nearest_node_id:
        closest_nodes.append((nearest_node_id, min_distance))

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
    

# south, west, north, east = 61.29560770030594, 12.127237063661534, 61.33240275253347, 12.266869460358693  # Replace these values with your coordinates

def generate_shortest_route(south, west, east, north):
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

  graph = create_graph(filtered_data)
  graph = find_connections_for_stranded_nodes(graph, filtered_data)

  start_node = 347047780
  end_node = 370586596
  shortest_path, shortest_distance = dijkstra(graph, start_node, end_node)

  # Use the function and print the GeoJSON data
  geojson_data = get_shortest_path_geojson(filtered_data, shortest_path, shortest_distance)

  # for node_id in graph:
  #   if not graph[node_id]:
  #     print(f"Stranded Node {node_id} has no connections")

  return geojson_data