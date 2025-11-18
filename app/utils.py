import networkx as nx
from haversine import haversine, Unit
from Data import ExportBusGraphAsNetworkX

def edge_cost_fn(edge: nx.edges, edge_para='travel_time') -> float:
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
    return round(haversine((origin_node['Longitude'], origin_node['Latitude']), (dist_node['Longitude'], dist_node['Latitude']), unit=Unit.KILOMETERS), 2)

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
    edge_att = nx.get_edge_attributes(G, 'travel_time')
    for i in range(len(path)-1):
        latency += edge_att[(path[i], path[i+1])]

    return latency
