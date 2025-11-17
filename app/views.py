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
    G = convert_bus_graph_time()

    all_line_candidates = {}
    all_line_candidates['bus'] = [] # assume only single mode of transport

    num_lines = 2 # num of lines to generate
    N = 5 # num of candidate route per line
    X = 0.5 # min distance (kilometers)
    Y = 0.3 # min threshold for valid o-d pairs (kilometers)
    K = 5 # k value for yen's shortest path
    M = 10 # num of o-d pairs to test per config

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

        for origin, destination in od_pairs:
            path = nx.astar_path(G, origin, destination, weight='travel_time')
            latency = utils.calculate_path_latency(G, path)

        if latency > max_latency:
            max_latency = latency

        if max_latency < best_latency:
            best_latency = max_latency
            best_config = config
    print('Complete')

    return [best_config, best_latency]
