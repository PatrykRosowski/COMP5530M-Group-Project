import networkx as nx

# Constant that leads to bus graph graph ml file
BUS_GRAPH = "bus_graph.graphml"
BUS_NETWORK = nx.read_graphml(BUS_GRAPH)


# Return the travel time weight between two access nodes (bus transport)
def get_weight_bus(G, accessNode0, accessNode1):

    if G == None:
        G = BUS_NETWORK

    an0 = accessNode0 if isinstance(accessNode0, str) else accessNode0.ATCOCode
    an1 = accessNode1 if isinstance(accessNode1, str) else accessNode1.ATCOCode

    try:
        weight = G[an0][an1]["weight"]
        return weight
    except KeyError:
        pass  # No edge exists

    # If the entries are strings, pass straight
    try:
        weightedPath = nx.shortest_path_length(G, an0, an1, weight="weight")
        return weightedPath
    except:
        return float("inf")
