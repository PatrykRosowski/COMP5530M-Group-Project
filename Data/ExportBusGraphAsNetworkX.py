import networkx as nx
import matplotlib.pyplot as plt
import requests
from pathlib import Path
from GenerateBusAccessNodeGraph import get_bus_access_node_graph

## Graph format
# Node       {ATCOCode: int}
# Attributes {CommonName : string,
#             Street     : string,
#             Longitude  : int,
#             Latitude   : int}
#
# Weight: Distance in long and lat between nodes (Pythagoras)

## URL for getting routing time requests
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"
ROOT_DIR = Path(__file__).resolve().parent.parent
SAVE_FILE = ROOT_DIR / "Data" / "graph" / "BusGraph.graphml"

## Draw the network graph
def draw_networkx_graph(G):
    ax = plt.subplot()
    pos = nx.random_layout(G)
    nx.draw(G, pos, with_labels=True)
    
    weightLabels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weightLabels)

    plt.show()

## Return the weight of each edge between nodes, which uses distance and Pythagoras' Theorem
def get_weight(initialNode, targetNode):

    response = requests.post(f'{OSRM_URL}{initialNode.Longitude},{initialNode.Latitude};{targetNode.Longitude},{targetNode.Latitude}')
    responseJson = response.json()
    return responseJson.get('routes')[0].get('duration')

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
    draw_networkx_graph(G)

    ## Return graph as networkx format
    nx.write_graphml(G, SAVE_FILE)

get_bus_graph_networkx()