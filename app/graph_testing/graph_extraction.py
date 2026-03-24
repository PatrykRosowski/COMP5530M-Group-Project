import networkx as nx

# Constant that leads to bus graph graph ml file
BUS_GRAPH = "bus_graph.graphml"


# Return the travel time weight between two access nodes (bus transport)
def get_weight_bus(accessNode0, accessNode1):

    G = nx.read_graphml(BUS_GRAPH)

    edgeAttributes = G.get_edge_data(accessNode0.ATCOCode, accessNode1.ATCOCode)
    edgeWeight = edgeAttributes.get("weight", 0)

    return edgeWeight
