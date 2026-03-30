import networkx as nx
import os
from path_finder import compute_least_eccentric_path
from ..data.ExportBusGraphAsNetworkX import get_bus_graph_networkx

BUS_GRAPH = "bus_graph.graphml"


# Function wrapper for path_finder compute_least_eccentric_path function.
# Function checks if the bus graph exists. If not, create it.
# Extract the graph from this function and pass to the path finder.
def path_finder(start_route: nx.nodes, end_route: nx.nodes, K: int):

    # If the bus graph doesnt exist, create it by calling function
    if not os.path.exists(BUS_GRAPH):
        print("Bus graph does not exist")
        get_bus_graph_networkx()

    # Get the networkx graph from the bus graph file
    G = nx.read_graphml(BUS_GRAPH)

    # Call the compute function
    paths = compute_least_eccentric_path(G, start_route, end_route, K)

    return paths
