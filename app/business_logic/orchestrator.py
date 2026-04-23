import networkx as nx
from flask import jsonify

from app.utils.graph_helpers import get_shape_for_stop_sequence
from app.algorithm_engine.path_finder_handler import path_finder

def route_calculation(start_node: list[float], end_node: list[float], K: int) -> tuple[tuple, int]:
 
    print('Doing route calculation....\n')
    G = nx.read_graphml("bus_graph.graphml")
    print(start_node)
    print(end_node)
    path_to_find = path_finder(start_node, end_node, K)
    print('Completed path finding....\n')
    print('Finding complete route....\n')
    frontend_response = get_shape_for_stop_sequence(G, path_to_find)
    print('Completed route finding....\n')
    return frontend_response
