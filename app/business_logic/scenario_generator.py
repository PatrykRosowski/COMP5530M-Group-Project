import networkx as nx
from random import choice
from itertools import product

from app.utils.graph_helpers import get_node_distance


def select_random_nodes(G: nx.DiGraph, X: float) -> tuple[nx.nodes, nx.nodes]:
    """
    Selects a random pair of nodes (Origin, Destination) that are at least X kilometers apart.

    Args:
        G (nx.DiGraph): The network graph.
        X (float): The minimum distance threshold in kilometers.

    Raises:
        ValueError: If the graph has fewer than 2 nodes or if no pairs satisfy the distance threshold.

    Returns:
        tuple[nx.nodes, nx.nodes]: A tuple containing the keys of the two selected nodes.
    """
    list_of_nodes = list(G.nodes)
    valid_pairs = []

    if len(list_of_nodes) < 2:
        raise ValueError("Graph must have at least two nodes")

    for i in range(len(list_of_nodes)):
        for j in range(len(list_of_nodes)):
            if i == j:
                continue

            node_A_key = list_of_nodes[i]
            node_B_key = list_of_nodes[j]

            node_A_data = G.nodes[node_A_key]
            node_B_data = G.nodes[node_B_key]

            dist = get_node_distance(G, node_A_data, node_B_data)

            if dist >= X:
                valid_pairs.append((node_A_key, node_B_key))

    if not valid_pairs:
        raise ValueError("No node pairs found")

    return choice(valid_pairs)


def get_nodes_covered_by_config(config: tuple) -> set:
    """
    Extracts a set of unique nodes covered by a network configuration.

    Args:
        config (tuple): A tuple containing lists of paths (where each path is a list of nodes).

    Returns:
        set: A set of unique node IDs present in the configuration.
    """
    nodes = set()
    for path in config:
        if path:
            nodes.update(path)
    return nodes


def generate_network_config(all_line_candidates: dict) -> list[tuple]:
    """
    Generates all possible network configurations by taking the Cartesian product of line candidates.

    Args:
        all_line_candidates (dict): A dictionary where keys are transport modes (e.g., 'bus')
                                    and values are lists of candidate paths. Currently on 'bus' is in used.

    Returns:
        list[tuple]: A list of network configurations, where each configuration is a tuple of paths.
    """
    all_lists_of_lines = []
    for mode in all_line_candidates:
        all_lists_of_lines.extend(all_line_candidates[mode])

    if not all_lists_of_lines:
        return []

    return list(product(*all_lists_of_lines))


def generate_od_pairs(G: nx.DiGraph, config: tuple, M: int, Y: float) -> list[tuple]:
    """
    Generates random Origin-Destination (OD) pairs for testing a network configuration.

    The origin is selected from nodes covered by the config, while the destination is any node in the graph.

    Args:
        G (nx.DiGraph): The network graph.
        config (tuple): The current network configuration (used to identify covered nodes).
        M (int): The target number of OD pairs to generate.
        Y (float): The minimum distance threshold between origin and destination.

    Returns:
        list[tuple]: A list of (origin, destination) tuples. May return fewer than M pairs if generation fails.
    """
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

        if get_node_distance(G, G.nodes[start_node], G.nodes[end_node]) >= Y:
            od_pairs.add((start_node, end_node))

        attempts += 1

    if len(od_pairs) < M:
        print(f"Could only find {len(od_pairs)} OD pairs")

    return list(od_pairs)
