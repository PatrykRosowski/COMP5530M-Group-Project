import networkx as nx
from itertools import islice


def shortest_distance_to_path(G: nx.DiGraph, node: nx.nodes, path_nodes: list[str]) -> float:
    """
    Calculates the shortest travel time from a specific node to any node within a given path.

    Args:
        G (nx.DiGraph): The network graph.
        node (nx.nodes): The starting node object.
        path_nodes (list[str]): A list of node identifiers constituting the target path.

    Returns:
        float: The minimum travel time from the start node to the closest node in the path_nodes list.
               Returns infinity if no path exists.
    """
    min_distance = float("inf")
    for p in path_nodes:
        try:
            dist = nx.shortest_path_length(
                G, node, p, weight="travel_time"
            )  # default to djikstra with travel time as weight
            if dist < min_distance:
                min_distance = dist
        except nx.NetworkXNoPath:
            continue

    return min_distance


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
        eccentricity = 0
        for node in list(G.nodes):
            distance = shortest_distance_to_path(G, node, path)
            if distance > eccentricity:
                eccentricity = distance
        if eccentricity < min_eccentricity:
            min_eccentricity = eccentricity
            best_path = path

    if paths_evaluated == 0:
        print(f"Path exists between {start_route} and {end_route}, no paths returned K = {K}")
        return None

    return best_path
