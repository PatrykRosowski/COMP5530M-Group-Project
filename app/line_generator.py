import utils
import networkx as nx
from random import randint, choice
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

def get_nodes_covered_by_config(config: tuple) -> set:
    nodes = set()
    for path in config:
        if path:
            nodes.update(path)
    return nodes

def generate_network_config(all_line_candidates: dict) -> list[tuple]:
    all_lists_of_lines = []
    for mode in all_line_candidates:
        all_lists_of_lines.extend(all_lists_of_lines[mode])

    if not all_lists_of_lines:
        return []
    
    return list(product(*all_lists_of_lines))

def generate_od_pairs(G: nx.DiGraph, config: tuple, M: int, Y: float) -> list[tuple]:
    covered_nodes = list(get_nodes_covered_by_config(config))
    all_nodes = list(G.nodes)
    od_pairs = set()

    if not covered_nodes:
        return []
    
    attempts = 0
    max_attempts = M * 100

    while len(od_pairs) < M and attempts < max_attempts:
        start_node = choice(covered_nodes)
        end_node = choice(all_nodes)

        if start_node == end_node:
            attempts += 1
            continue

        if utils.get_node_distance(start_node, end_node) >= Y:
            od_pairs.add((start_node, end_node))

        attempts += 1

    if len(od_pairs) < M:
        print(f'Could only find {len(od_pairs)} OD pairs')

    return list(od_pairs)


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



