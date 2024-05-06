def update_graph_with_connections(graph, node_id, nodes, isBestRoute: bool = False):
  if isBestRoute:
    best_route_graph(graph, node_id, nodes)
  else:
    shortest_route_graph(graph, node_id, nodes)

def best_route_graph(graph, node_id, nodes):
	for nearest_node, weight in nodes:
		if nearest_node != node_id and (nearest_node, weight) not in graph[node_id]:
			graph[node_id].append((nearest_node, weight))
   
def shortest_route_graph(graph, node_id, nodes):
	for nearest_node, distance in nodes:
		if nearest_node != node_id and (nearest_node, distance) not in graph[node_id]:
			graph[node_id].append((nearest_node, distance))