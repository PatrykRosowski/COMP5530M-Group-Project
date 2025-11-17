import networkx as nx
from haversine import haversine, Unit
from Data import ExportBusGraphAsNetworkX

def edge_cost_fn(edge: nx.edges, edge_para='travel_time') -> float:
    return nx.get_edge_attributes(edge, edge_para)

def get_node_distance(G: nx.DiGraph, origin_node: nx.nodes, dist_node: nx.nodes) -> float:
    return round(haversine((origin_node['Longitude'], origin_node['Latitude']), (dist_node['Longitude'], dist_node['Latitude']), unit=Unit.KILOMETERS), 2)

def calculate_path_latency(G: nx.DiGraph, path: list[str], transfer_penalty=None) -> float:
    latency = 0
    edge_att = nx.get_edge_attributes(G, 'travel_time')
    for i in range(len(path)-1):
        latency += edge_att[(path[i], path[i+1])]

    return latency
