import networkx as nx
import os
import osmnx as ox
import random
from app.algorithm_engine.path_finder import compute_least_eccentric_path
from app.data.ExportBusGraphAsNetworkX import get_bus_graph_networkx
from math import radians, sin, cos, sqrt, atan2

BUS_GRAPH = "bus_graph.graphml"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def nearest_node(G, lat, lon):
    return min(G.nodes, key=lambda n: haversine(
        lat, lon, G.nodes[n]['Latitude'], G.nodes[n]['Longitude']
    ))

# Function wrapper for path_finder compute_least_eccentric_path function.
# Function checks if the bus graph exists. If not, create it.
# Extract the graph from this function and pass to the path finder.
def path_finder(start_route: float, end_route: float, K: int):

    # If the bus graph doesnt exist, create it by calling function
    if not os.path.exists(BUS_GRAPH):
        print("Bus graph does not exist")
        get_bus_graph_networkx()

    # Get the networkx graph from the bus graph file
    G = nx.read_graphml(BUS_GRAPH)

    A_nearest = nearest_node(G, start_route[0], start_route[1])
    B_nearest = nearest_node(G, end_route[0], end_route[1])
    
    # Call the compute function
    paths = compute_least_eccentric_path(G, A_nearest, B_nearest, 1)

    return paths
