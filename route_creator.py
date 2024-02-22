import requests
import math

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

def find_nodes_within_distance_or_nearest(stranded_node_lat, stranded_node_lon, stranded_node_type, elements, max_distance_km=0.05):
    nodes_within_distance = []
    min_distance = float('inf')
    nearest_node_id = None
    seen_node_ids = set()  # Track seen node IDs to avoid duplicates

    for element in elements:
        element_type = 'lift' if 'aerialway' in element.get('tags', {}) else 'piste'
        if element_type != stranded_node_type:
            for i, geom in enumerate(element.get('geometry', [])):
                lat, lon = geom['lat'], geom['lon']
                node_id = element['nodes'][i]
                # Skip this node if we've already processed it
                if node_id in seen_node_ids:
                    continue
                seen_node_ids.add(node_id)  # Mark this node ID as seen

                distance = haversine(stranded_node_lat, stranded_node_lon, lat, lon)
                if distance <= max_distance_km:
                    nodes_within_distance.append((node_id, distance))
                elif distance < min_distance:
                    min_distance = distance
                    nearest_node_id = node_id

    # Sort nodes within distance by their distance, so closest nodes are first
    nodes_within_distance.sort(key=lambda x: x[1])

    # If we found nodes within 20 meters, return them; otherwise, return the nearest node
    if nodes_within_distance:
        return nodes_within_distance
    else:
        return [(nearest_node_id, min_distance)] if nearest_node_id else []


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

if 'elements' in data and len(data['elements']) > 0:
    first_element = data['elements'][32]
    print(first_element)
else:
    print("No elements found in the data")

# Create a graph from the data with already connected nodes
graph = {}
for element in data['elements']:
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
        for element in data['elements']:
            if node_id in element['nodes']:
                index = element['nodes'].index(node_id)
                stranded_lat = element['geometry'][index]['lat']
                stranded_lon = element['geometry'][index]['lon']
                stranded_type = 'lift' if 'aerialway' in element.get('tags', {}) else 'piste'
                nodes = find_nodes_within_distance_or_nearest(stranded_lat, stranded_lon, stranded_type, data['elements'])

                for nearest_node, distance in nodes:
                    graph[node_id].append((nearest_node, distance))
                    print(f"Stranded Node {node_id} connects to node {nearest_node} with distance {distance} km")
                break

#print(graph)