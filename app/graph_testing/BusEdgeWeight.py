import networkx as nx

# Constant that leads to bus graph graph ml file
BUS_GRAPH = "bus_graph.graphml"


# Return the travel time weight between two access nodes (bus transport)
def get_weight_bus(G, accessNode0, accessNode1):

    if G == None:
        G = nx.read_graphml(BUS_GRAPH)

    # If the entries are strings, pass straight
    try:
        if isinstance(accessNode0, str):
            weightedPath = nx.shortest_path_length(G, accessNode0, accessNode1, weight="weight")
        else:
            weightedPath = nx.shortest_path_length(G, accessNode0.ATCOCode, accessNode1.ATCOCode, weight="weight")

        return weightedPath
    except:
        return float('inf')
