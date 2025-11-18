from flask import Flask
from app import app

from Data.ExportBusGraphAsNetworkX import convert_bus_graph_time

import networkx as nx
from . import utils
from . import line_generator

@app.route('/')
def index():
    return "Server is running"

@app.route('/main')
def main():
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
    all_line_candidates['bus'] = [] # assume only single mode of transport

    num_lines = 2
    N = 5
    X = 0.5 
    Y = 0.3 
    K = 5 
    M = 10 

    for line_index in range(num_lines):
        print(f'Generating {N} candidates for bus line {line_index + 1}')
        line_candidates = []

        for i in range(N):
            (A, B) = line_generator.select_random_nodes(G, X)
            print(f'Node selected {A}, {B}')

            print(f'Computing MESP - round {i}')
            path = line_generator.compute_mesp(G, A, B, K)
            print(f'Complete round {i}')
            if path:
                line_candidates.append(path)
            else:
                print(f'compute_mesp found no path for candidate {i+1}')

        all_line_candidates['bus'].append(line_candidates)

    print('All line candidates generated')

    print('Generating network config')
    all_network_config = line_generator.generate_network_config(all_line_candidates)
    print('Network config generation completed')
    best_latency = float('inf')
    best_config = None

    print('Testing OD pairs')
    for config in all_network_config:
        od_pairs = line_generator.generate_od_pairs(G, config, M, Y)
        max_latency = 0

        if not od_pairs:
            max_latency = float('inf') # if no od pairs found, config is untestable

        for origin, destination in od_pairs:
            try:
                path = nx.astar_path(G, origin, destination, weight='travel_time')
                latency = utils.calculate_path_latency(G, path)
            except nx.NetworkXNoPath:
                latency = float('inf') # no path thus impossible trip

            if latency > max_latency:
                max_latency = latency

            if max_latency == float('inf'):
                break

        if max_latency < best_latency:
            best_latency = max_latency
            best_config = config

    print('Complete')

    return [best_config, best_latency]
