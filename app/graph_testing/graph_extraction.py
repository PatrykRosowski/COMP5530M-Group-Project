import networkx as nx

# Constant that leads to bus graph graph ml file
BUS_GRAPH = "bus_graph.graphml"


# Return the travel time weight between two access nodes (bus transport)
def get_weight_bus(accessNode0, accessNode1):

    G = nx.read_graphml(BUS_GRAPH)

    # If the entries are strings, pass straight
    if isinstance(accessNode0, str):
        edgeAttributes = G.get_edge_data(accessNode0, accessNode1)
    else:
        edgeAttributes = G.get_edge_data(accessNode0.ATCOCode, accessNode1.ATCOCode)

    # If the edge exists
    if edgeAttributes != None:
        edgeWeight = edgeAttributes.get("weight", 0)
        return edgeWeight
    else:  # If the edge does not exist
        return None
