import utils
import networkx as nx
from random import randint
from itertools import product

def select_random_nodes(G: nx.DiGraph, X: float) -> tuple[nx.nodes, nx.nodes]:
    list_of_nodes = list(G.nodes)

    origin_node = list_of_nodes[randint(0, len(list_of_nodes))]

    while True:
        dest_node = list_of_nodes(randint(0, len(list_of_nodes)))
        if utils.get_node_distance(origin_node, dest_node) > X:
            break

    return origin_node, dest_node

def shortest_distance_to_path(G: nx.DiGraph, node: nx.nodes, path_nodes: list[str]) -> float:
    min_distance = float('inf')
    for p in path_nodes:
        try:
            dist = nx.shortest_path_length(G, node, p, weight='travel_time') # default to djikstra with travel time as weight
            if dist < min_distance:
                min_distance = dist
        except nx.NetworkXNoPath:
            continue
    
    return min_distance

def generate_od_pairs(G: nx.DiGraph, config: tuple, M: int, Y: float) -> list[tuple]:
    return None

def generate_network_config(all_line_candidates):
    return None


def compute_mesp(G: nx.DiGraph, start_route: nx.nodes, end_route: nx.nodes, K: int) -> list[str]:
    all_paths = nx.shortest_simple_paths(G, start_route, end_route, 'travel_time') # implementation based on yen's k shortest path
    k_paths = all_paths[:K]

    min_eccentricity = float('inf')
    best_path = None

    for path in k_paths:
        eccentricity = 0
        for node in list(G.nodes):
            distance = shortest_distance_to_path(G, node, path)
            if distance > eccentricity:
                eccentricity = distance
        if eccentricity < min_eccentricity:
            min_eccentricity = eccentricity
            best_path = path

    return best_path



