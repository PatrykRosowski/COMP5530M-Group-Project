import networkx as nx
from flask import jsonify

from app.algorithm_engine.path_finder import compute_least_eccentric_path
from app.utils.graph_helpers import calculate_path_latency, get_shape_for_stop_sequence
from app.business_logic.scenario_generator import (
    select_random_nodes,
    generate_network_config,
    generate_od_pairs,
)
from ..data.ExportBusGraphAsNetworkX import convert_bus_graph_time


def route_calculation() -> tuple[tuple, int]:
    """
    Main execution route for generating and optimizing bus line networks.

    This function orchestrates the generation of candidate routes using the MESP algorithm,
    creates network configurations, and evaluates them based on random OD pair latency.

    Configuration (Internal Constants):
        The following hardcoded variables within the function control the simulation:
        - num_lines (int): Number of lines to generate (set to 2).
        - N (int): Number of candidate routes to generate per line (set to 5).
        - X (float): Minimum distance in km for a route's start/end points (set to 0.5).
        - Y (float): Minimum distance in km for test OD pairs (set to 0.3).
        - K (int): Number of shortest paths to evaluate in Yen's algorithm (set to 5).
        - M (int): Number of random OD pairs to test per configuration (set to 10).

    Returns:
        list: A list containing the best network configuration (tuple)
              and its corresponding max latency (float).
    """
    G = convert_bus_graph_time()

    all_line_candidates = {}
    all_line_candidates["bus"] = []

    num_lines = 2
    N = 5
    X = 0.5
    Y = 0.3
    K = 5
    M = 10

    for line_index in range(num_lines):
        print(f"Generating {N} candidates for bus line {line_index + 1}")
        line_candidates = []

        for i in range(N):
            (A, B) = select_random_nodes(G, X)
            print(f"Node selected {A}, {B}")

            print(f"Computing MESP - round {i}")
            path = compute_least_eccentric_path(G, A, B, K)
            print(f"Complete round {i}")
            if path:
                line_candidates.append(path)
            else:
                print(f"compute_mesp found no path for candidate {i+1}")

        all_line_candidates["bus"].append(line_candidates)

    print("All line candidates generated")

    print("Generating network config")
    all_network_config = generate_network_config(all_line_candidates)
    print("Network config generation completed")
    best_latency = float("inf")
    best_config = None

    print("Testing OD pairs")
    for config in all_network_config:
        od_pairs = generate_od_pairs(G, config, M, Y)
        max_latency = 0

        if not od_pairs:
            max_latency = float("inf")  # if no od pairs found, config is untestable

        for origin, destination in od_pairs:
            try:
                path = nx.astar_path(G, origin, destination, weight="travel_time")
                latency = calculate_path_latency(G, path)
            except nx.NetworkXNoPath:
                latency = float("inf")  # no path thus impossible trip

            if latency > max_latency:
                max_latency = latency

            if max_latency == float("inf"):
                break

        if max_latency < best_latency:
            best_latency = max_latency
            best_config = config

    print("Complete")

    frontend_response = {
        'latency': best_latency,
        'lines': [],
        'stops': []
    }

    for path_of_nodes in best_config:
        geometry = get_shape_for_stop_sequence(G, path_of_nodes)
        frontend_response['lines'].append(geometry)

    unique_nodes = set(node for path in best_config for node in path)

    for node_id in unique_nodes:
        node_data = G.nodes[node_id]

        frontend_response['stops'].append({
            'id': node_id,
            'lat': node_data['Latitude'],
            'lon': node_data['Longitude'],
            'name': node_data['CommonName']
        })

    print("\n" + "="*30)
    print(f"FINAL CONFIGURATION (Latency: {best_latency})")
    for i, line_path in enumerate(best_config):
        print(f"\nBus Line {i + 1}:")
        print(f"  Stop Count: {len(line_path)}")
        print(f"  Stop IDs:   {line_path}")
        
        # Optional: Print names if available to make it readable
        names = [G.nodes[n].get('CommonName', 'Unknown') for n in line_path]
        print(f"  Stop Names: {names}")
    print("="*30 + "\n")

    return frontend_response


