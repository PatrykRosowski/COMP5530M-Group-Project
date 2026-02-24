import networkx as nx
import requests
import json
import polyline
from haversine import haversine, Unit

VALHALLA_URL = "http://localhost:8002/route"

def edge_cost_fn(edge: nx.edges, edge_para="travel_time") -> float:
    """
    Retrieves a specific attribute (cost) from a graph edge.

    Args:
        edge (nx.edges): The edge object from which to retrieve the attribute.
        edge_para (str, optional): The key of the attribute to retrieve.
                                   Defaults to 'travel_time'.

    Returns:
        float: The 'travel_time' of the edge.
    """
    return nx.get_edge_attributes(edge, edge_para)


def get_node_distance(G: nx.DiGraph, origin_node: nx.nodes, dist_node: nx.nodes) -> float:
    """
    Calculates the Haversine distance (in kilometers) between two nodes.

    Args:
        G (nx.DiGraph): The network graph containing the nodes.
        origin_node (dict): The data dictionary of the starting node (must contain 'Latitude' and 'Longitude').
        dist_node (dict): The data dictionary of the destination node (must contain 'Latitude' and 'Longitude').

    Returns:
        float: The distance between the two nodes in kilometers, rounded to 2 decimal places.
    """
    return round(
        haversine(
            (origin_node["Latitude"], origin_node["Longitude"]),
            (dist_node["Latitude"], dist_node["Longitude"]),
            unit=Unit.KILOMETERS,
        ),
        2,
    )


def calculate_path_latency(G: nx.DiGraph, path: list[str], transfer_penalty=None) -> float:
    """
    Calculates the total travel time (latency) for a specific path in the graph.

    Args:
        G (nx.DiGraph): The network graph containing edge attributes.
        path (list[str]): A list of node IDs representing the sequential path.
        transfer_penalty (float, optional): A penalty value to add for transfers (currently unused).

    Returns:
        float: The cumulative 'travel_time' of all edges in the path.
    """
    latency = 0
    edge_att = nx.get_edge_attributes(G, "travel_time")
    for i in range(len(path) - 1):
        latency += edge_att[(path[i], path[i + 1])]

    return latency

def _get_straight_line_fallback(locations: list[tuple]):
    coords = [[loc['lon'], loc['lat']] for loc in locations]
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': coords
        },
        'properties': {'error': 'Routing failed, used straight lines'}
    }

def get_shape_for_stop_sequence(G: nx.DiGraph, node_ids: list[str]) -> str:
    print(f"DEBUG: Routing shape for sequence: {node_ids}")
    locations = []
    for i, node in enumerate(node_ids):
        node_data = G.nodes[node]
        location_type = 'break'

        if 0 < i < len(node_ids) - 1: 
            location_type = 'through' # use 'through' mode for intermediate stops

        locations.append({
            'lat': node_data['Latitude'],
            'lon': node_data['Longitude'],
            'type': location_type,
        })

    payload = {
        'locations': locations,
        'costing': 'bus',
        'directions_options': {
            'units': 'km'
        }
    }

    try:
        response = requests.post(VALHALLA_URL, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        all_coordinates = []


        for i, leg in enumerate(data['trip']['legs']):
            decoded_points = polyline.decode(leg['shape'], 6)
            geojson_points = [[lon, lat] for lat, lon in decoded_points]

            if i > 0:
                all_coordinates.extend(geojson_points[1:])
            else:
                all_coordinates.extend(geojson_points)

        return {
            'type': 'Feature',
            'properties': {
                'order': node_ids
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': all_coordinates
            }
        }
    
    except Exception as e:
        print(f'Error routing path: {e}')
        print(f"DEBUG: Fallback triggered for nodes: {node_ids}")
        return _get_straight_line_fallback(locations)
