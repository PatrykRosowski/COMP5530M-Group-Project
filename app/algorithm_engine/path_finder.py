import networkx as nx
from itertools import islice
import math


def shortest_distance_to_path(G: nx.DiGraph, path_nodes: list[str]) -> float:
    """
    Calculates the shortest travel time from a specific node to any node within a given path.

    Args:
        G (nx.DiGraph): The network graph.
        path_nodes (list[str]): A list of node identifiers constituting the target path.

    Returns:
        dict: A dictionary mapping each node in the graph to the minimum distance of the closest node in the path.
    """
    # Using networkx more improved function for finding minimum distance
    try:

        distance, _ = nx.multi_source_dijkstra(
            G.reverse(copy=False), path_nodes, weight="travel_time"
        )
        return distance
    except nx.NetworkXNoPath:
        return float("inf")


def compute_least_eccentric_path(
    G: nx.DiGraph, start_route: nx.nodes, end_route: nx.nodes, K: int
) -> list[str]:
    """
    Computes a path that minimizes the maximum eccentricity (distance) from all other nodes
    in the graph to the path, chosen from the K shortest paths.

    Args:
        G (nx.DiGraph): The network graph.
        start_route (nx.nodes): The starting node of the potential line.
        end_route (nx.nodes): The ending node of the potential line.
        K (int): The number of shortest paths (via Yen's algorithm equivalent) to evaluate.

    Returns:
        list[str] or None: The path (list of nodes) with the lowest eccentricity,
                           or None if no paths exist between start and end.
    """
    try:
        all_paths = nx.shortest_simple_paths(
            G, start_route, end_route, "travel_time"
        )  # implementation based on yen's k shortest path
        k_paths = islice(all_paths, K)  # all_path is a generator type
    except nx.NetworkXNoPath:
        print(f"No path found between {start_route} and {end_route}")

    min_eccentricity = float("inf")
    best_path = None
    paths_evaluated = 0

    for path in k_paths:
        paths_evaluated += 1
        distances = shortest_distance_to_path(G, path)
        # Iterate dictionary to extract maximum eccentricity
        eccentricity = max(distances.values())
        if eccentricity < min_eccentricity:
            min_eccentricity = eccentricity
            best_path = path

    if paths_evaluated == 0:
        print(f"Path exists between {start_route} and {end_route}, no paths returned K = {K}")
        return None

    return best_path
