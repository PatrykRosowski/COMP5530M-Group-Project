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
    G: nx.DiGraph, start_route: str, end_route: str, K: int
) -> list[str] | None:
    """
    Computes a path that minimizes the maximum eccentricity (distance) from all other nodes
    in the graph to the path, chosen from the K shortest paths.
    
    This optimization utilizes a reversed graph view and multi-source Dijkstra's 
    algorithm to efficiently calculate shortest travel times from all nodes to the path 
    in a single traversal.

    Args:
        G (nx.DiGraph): The directed network graph.
        start_route (str): The starting node identifier.
        end_route (str): The ending node identifier.
        K (int): The number of shortest paths to evaluate.

    Returns:
        list[str] | None: The path (list of nodes) with the lowest eccentricity,
                          or None if no valid paths exist or are returned.
    """
    try:
        all_paths = nx.shortest_simple_paths(G, start_route, end_route, weight="travel_time")
        k_paths = list(islice(all_paths, K)) 
    except nx.NetworkXNoPath:
        print(f"No path found between {start_route} and {end_route}")
        return None

    if not k_paths:
        print(f"Path exists between {start_route} and {end_route}, no paths returned K = {K}")
        return None

    G_rev = G.reverse(copy=False)
    total_nodes = len(G)
    
    min_eccentricity = float("inf")
    best_path = None

    for path in k_paths:
        distances = nx.multi_source_dijkstra_path_length(
            G_rev, sources=set(path), weight="travel_time"
        )
        
        if len(distances) < total_nodes:
            eccentricity = float("inf")
        else:
            eccentricity = max(distances.values())

        if eccentricity < min_eccentricity:
            min_eccentricity = eccentricity
            best_path = path

    return best_path
