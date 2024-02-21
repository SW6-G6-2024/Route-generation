import requests

# Define your bounding box coordinates
south, west, north, east = 61.29560770030594, 12.127237063661534, 61.33240275253347, 12.266869460358693  # Replace these values with your coordinates

# Define the Overpass QL query
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

# Encode the query and make the GET request to the Overpass API
response = requests.get(f"https://overpass-api.de/api/interpreter?data={requests.utils.quote(query)}")

# Check if the response is successful
if not response.ok:
    raise Exception('Network response was not ok')

# Parse the JSON data from the response
data = response.json()

print(data)
