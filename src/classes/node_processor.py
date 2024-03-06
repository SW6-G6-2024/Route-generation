from utils.haversine import haversine

class NodeProcessor:
    def __init__(self, node, existing_connections, max_distance_km):
        self.node = node
        self.existing_connections = existing_connections
        self.closest_nodes = []
        self.nearest_node_details = {'min_distance': float('inf'), 'nearest_node_id': None}
        self.max_distance_km = max_distance_km

    def process_element_node(self, element, i, geom, element_type):
        lat, lon = geom['lat'], geom['lon']
        node_id = element['nodes'][i]
        if node_id == self.node.node_id or node_id in self.existing_connections:
            return

        distance = haversine(self.node.lat, self.node.lon, lat, lon)
        if element_type == 'lift' and i != 0:
            return

        if distance <= self.max_distance_km:
            if distance < self.nearest_node_details['min_distance']:
                self.nearest_node_details['min_distance'] = distance
                self.nearest_node_details['nearest_node_id'] = node_id
            self.closest_nodes.append((node_id, distance))
