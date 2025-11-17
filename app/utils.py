import networkx as nx
from haversine import haversine, Unit
from Data import ExportBusGraphAsNetworkX

def edge_cost_fn(edge: nx.edges, edge_para='travel_time') -> float:
    return nx.get_edge_attributes(edge, edge_para)

def get_node_distance(G: nx.DiGraph, origin_node: nx.nodes, dist_node: nx.nodes) -> float:
    return round(haversine((origin_node.get_Longitude(), origin_node.get_Latitude()), (dist_node.get_Longitude(), dist_node.get_Latitude()), unit=Unit.KILOMETERS), 2)

