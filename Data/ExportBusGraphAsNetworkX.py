import networkx as nx
import matplotlib.pyplot as plt
from GenerateBusAccessNodeGraph import get_bus_access_node_graph

## Graph format
# Node       {ATCOCode: int}
# Attributes {CommonName : string,
#             Street     : string,
#             Longitude  : int,
#             Latitude   : int}

def draw_networkx_graph(G):
    ax = plt.subplot()
    nx.draw(G, with_labels=True)

    plt.show()

def get_bus_graph_networkx():
    bus_graph = get_bus_access_node_graph()
    G = nx.Graph()

    ## Adding access nodes to networkx graph along with attributes
    for accessNode in bus_graph:
        G.add_node(accessNode.get_ATCOCode(),
                   CommonName = accessNode.get_CommonName(),
                   Street     = accessNode.get_Street(),
                   Longitude  = accessNode.get_Longitude(),
                   Latitude   = accessNode.get_Latitude())
        
    ## Adding edges into networkx graph between access nodes
    for accessNode in bus_graph:
        ## Add edge for all nearby neighbours
        for neighbour in accessNode.get_Nearby():
            G.add_edge(accessNode.get_ATCOCode(),
                       neighbour.get_ATCOCode())
            
    ## Drawing graph
    draw_networkx_graph(G)

    ## Return graph as networkx format
    return G


get_bus_graph_networkx()