import networkx as nx
import matplotlib.pyplot as plt
import math
from GenerateBusAccessNodeGraph import get_bus_access_node_graph

## Graph format
# Node       {ATCOCode: int}
# Attributes {CommonName : string,
#             Street     : string,
#             Longitude  : int,
#             Latitude   : int}
#
# Weight: Distance in long and lat between nodes (Pythagoras)

## Draw the network graph
def draw_networkx_graph(G):
    ax = plt.subplot()
    nx.draw(G, with_labels=True)

    plt.show()

## Return the weight of each edge between nodes, which uses distance and Pythagoras' Theorem
def get_weight(initialNode, targetNode):
    latitudeSquared = (initialNode.get_Latitude() - targetNode.get_Latitude()) ** 2
    longitudeSquared = (initialNode.get_Longitude() - targetNode.get_Longitude()) ** 2

    return math.sqrt(latitudeSquared + longitudeSquared) # Pythagoras' Theorem

## Returns networkx bus access node graph with weights
def get_bus_graph_networkx():
    bus_graph = get_bus_access_node_graph()
    G = nx.DiGraph()

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
                       neighbour.get_ATCOCode(),
                       weight=get_weight(accessNode, neighbour))
            
    ## Drawing graph
    #draw_networkx_graph(G)

    ## Return graph as networkx format
    return G


get_bus_graph_networkx()