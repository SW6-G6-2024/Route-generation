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

print(graph)