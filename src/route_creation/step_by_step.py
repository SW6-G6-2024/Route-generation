def step_by_step_guide(path, overpassData):
    """
    Uses the found path's node IDs to find and refine way elements from the overpass data.
    It then adds the way name/ref to a list, avoiding consecutive duplicates directly.
    It prioritizes staying on the same way at intersections unless the path explicitly changes.

    Args:
        path (list): A list of node IDs representing the found path.
        overpassData (dict): A dictionary containing GeoJSON data from the Overpass API.

    Returns:
        list: A refined list of way names or IDs corresponding to the found path,
              with consecutive duplicates already avoided.
    """
    last_added_way_name = None
    path_set = set(path)
    relevant_ways = [
      element for element in overpassData['elements']
      if element['type'] == 'way' and set(element['nodes']).intersection(path_set)
    ]
    way_to_nodes = build_way_to_nodes_mapping(relevant_ways)
    refined_sequence = []
    
    # Process the path to refine the sequence of way names or IDs.
    refined_sequence, last_added_way_name = process_path(path, way_to_nodes, last_added_way_name)

    return refined_sequence


def build_way_to_nodes_mapping(relevant_ways):
    """
    Maps way names/refs to their nodes for the relevant ways.
    
    Args:
        relevant_ways (list): A list of way elements relevant to the path.
    
    Returns:
        dict: A dictionary mapping way names/refs to their corresponding set of node IDs.
    """
    way_to_nodes = {}
    for element in relevant_ways:
      way_name = element['tags'].get('name', element['tags'].get('ref', "?"))
      way_difficulty = element['tags'].get('piste:difficulty', None)
      way_lift_type = element['tags'].get('aerialway', None)
      if way_lift_type == 'drag_lift':
        way_lift_type = element['tags'].get('aerialway:drag_lift')
      way_to_nodes[way_name] = {'nodes': set(element['nodes']), 'difficulty': way_difficulty, 'lift_type': way_lift_type}
    return way_to_nodes

def is_node_in_way(node_id, nodes, next_node_id):
    """
    Checks if the current node and optionally the next node are part of the given way's nodes.
    
    Args:
        node_id (int): The current node ID.
        nodes (set): The set of node IDs belonging to a way.
        next_node_id (int): The next node ID in the path, if any.
    
    Returns:
        bool: True if the current node is in the way and (if applicable) the next node is also in the way.
    """
    current_node_in_way = node_id in nodes
    next_node_in_way = next_node_id is None or next_node_id in nodes
    return current_node_in_way and next_node_in_way

def determine_current_way(node_id, next_node_id, way_to_nodes, last_added_way_name):
    """
    Determines the current way based on the given node and the next node in the path.
    """
    for way_name, data in way_to_nodes.items():
        if is_node_in_way(node_id, data['nodes'], next_node_id) and last_added_way_name != way_name:
            return {'name': way_name, 'difficulty': data['difficulty'], 'lift_type': data['lift_type']}
    return None


def update_refined_sequence(way, refined_sequence, last_added_way_name):
    """
    Updates the refined sequence with the current way name if it's different from the last added way.

    Args:
        way_name (str): The current way name/ref to be potentially added to the sequence.
        refined_sequence (list): The current sequence of refined way names/refs.
        last_added_way_name (str): The last way name/ref added to the sequence.
    
    Returns:
        str: The updated last added way name/ref.
    """
    if way:
      refined_sequence.append(way)
      return way['name']  # Update the last added way name
    return last_added_way_name


def process_path(path, way_to_nodes, last_added_way_name):
    """
    Processes each node in the path to refine the sequence of way names or refs.

    Args:
        path (list): A list of node IDs representing the path.
        way_to_nodes (dict): Mapping of way names/refs to their corresponding node IDs.
        last_added_way_name (str): The last way name/ref added to the sequence.

    Returns:
        tuple: A tuple containing the refined sequence of way names/refs and the last added way name/ref.
    """
    refined_sequence = []

    for i, node_id in enumerate(path):
      next_node_id = path[i + 1] if i + 1 < len(path) else None
      current_way = determine_current_way(node_id, next_node_id, way_to_nodes, last_added_way_name)
      if current_way:
        last_added_way_name = update_refined_sequence(current_way, refined_sequence, last_added_way_name)

    return refined_sequence, last_added_way_name
