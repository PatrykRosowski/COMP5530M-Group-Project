import networkx as nx
import matplotlib.pyplot as plt
import requests
from pathlib import Path
from haversine import haversine, Unit
from GenerateBusAccessNodeGraph import get_bus_access_node_graph

# Graph format
# Node       {ATCOCode: int}
# Attributes {CommonName : string,
#             Street     : string,
#             Longitude  : int,
#             Latitude   : int}
#
# Weight: Distance in long and lat between nodes

# URL for getting routing time requests
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"
ROOT_DIR = Path(__file__).resolve().parent.parent


# Draw the network graph
def draw_networkx_graph(G, labels, edge_para="weight"):
    pos = nx.spring_layout(G)  # easier to understand graph layout (nodes repel each other)
    nx.draw_networkx_nodes(G, pos, node_size=30, alpha=0.5)
    nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=7)
    nx.draw_networkx_edges(G, pos=pos, alpha=0.5, width=0.5)
    edge_labels = nx.get_edge_attributes(G, edge_para)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5)

    plt.show()


# Returns the time taken to travel from the initial node to the target node
def get_weight(initialNode, targetNode):

    response = requests.post(
        f"{OSRM_URL}{initialNode.Longitude},{initialNode.Latitude};{targetNode.Longitude},{targetNode.Latitude}"
    )
    responseJson = response.json()
    return responseJson.get("routes")[0].get("duration")


# Returns the distance in kilometers using the haversine module
def get_distance_haversine(initialNode, targetNode):

    return round(
        haversine(
            (initialNode.get_Longitude(), initialNode.get_Latitude()),
            (targetNode.get_Longitude(), targetNode.get_Latitude()),
            unit=Unit.KILOMETERS,
        ),
        2,
    )


# Returns networkx bus access node graph with weights
def get_bus_graph_networkx():
    bus_graph = get_bus_access_node_graph()
    G = nx.DiGraph()
    labels = {}  # For adding custom labels to graph

    # Adding access nodes to networkx graph along with attributes
    for accessNode in bus_graph:
        G.add_node(
            accessNode.get_ATCOCode(),
            CommonName=accessNode.get_CommonName(),
            Street=accessNode.get_Street(),
            Longitude=accessNode.get_Longitude(),
            Latitude=accessNode.get_Latitude(),
        )
        labels[accessNode.get_ATCOCode()] = accessNode.get_CommonName()

    # Adding edges into networkx graph between access nodes
    for accessNode in bus_graph:
        # Add edge for all nearby neighbours
        for neighbour in accessNode.get_Nearby():
            G.add_edge(
                accessNode.get_ATCOCode(),
                neighbour.get_ATCOCode(),
                weight=get_weight(accessNode, neighbour),
            )

    # Drawing graph
    draw_networkx_graph(G, labels)

    # Save graph as graphml - ungku
    nx.write_graphml_lxml(G, "bus_graph.graphml")

    # Return graph as networkx format
    return G


def convert_bus_graph_time():
    G = get_bus_graph_networkx()

    ASSUMED_SPEED = 25.0  # in KPH
    DISTANCE_KEY = "weight"
    TIME_KEY = "travel_time"

    for u, v, data in G.edges(data=True):
        if DISTANCE_KEY in data:
            distance = float(data[DISTANCE_KEY])
            travel_time = round(((distance / ASSUMED_SPEED) * 3600), 2)  # convert to seconds
            data[TIME_KEY] = travel_time
        else:
            print(f"Edge ({u}, {v}) missing {DISTANCE_KEY} attribute.")

    return G


get_bus_graph_networkx()
