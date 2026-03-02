import networkx as nx
import matplotlib.pyplot as plt
import requests
from pathlib import Path
from haversine import haversine, Unit
from GenerateBusAccessNodeGraph import get_bus_access_node_graph
from Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph as D_get_bus_access_node_graph
from scipy.spatial import Delaunay
import gmplot
import osmnx as ox
from pyrosm import OSM
import gc
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from tqdm.contrib.concurrent import thread_map
import os

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
GRAPH_PATH = Path(__file__).parent / "bus_graph.graphml"

# Constant parameters
REGION_MAP = str(Path(__file__).parent / "roads_only.osm.pbf")
MINIMUM_DISTANCE = 100


# Draw the network graph
def draw_networkx_graph(G, labels, edge_para="weight"):
    pos = nx.spring_layout(G)  # easier to understand graph layout (nodes repel each other)
    nx.draw_networkx_nodes(G, pos, node_size=30, alpha=0.5)
    nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=7)
    nx.draw_networkx_edges(G, pos=pos, alpha=0.5, width=0.5)
    edge_labels = nx.get_edge_attributes(G, edge_para)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5)

    plt.show()


# Map the network graph onto a real map
def map_networkx_graph_(G, labels, edge_para="weight"):
    gmap = gmplot.GoogleMapPlotter(53.9921, 1.5418, 13)

    # Lists for passing onto Google Maps
    latitude_list = []
    longitude_list = []

    # Retrieving Latitude and Longitude data from graph
    for accessNode, data in G.nodes(data=True):
        latitude_list.append(data.get("Latitude"))
        longitude_list.append(data.get("Longitude"))

        # Plot any edges of this accessNode
        for source, target, weight in G.out_edges(accessNode, data="weight"):
            sourceLatitude = G.nodes[source]["Latitude"]
            sourceLongitude = G.nodes[source]["Longitude"]

            targetLatitude = G.nodes[target]["Latitude"]
            targetLongitude = G.nodes[target]["Longitude"]

            # Check the distance of the two nodes, if the distance is too short, dont add the edge
            distance = get_distance_haversize_long_lat(
                [sourceLongitude, sourceLatitude], [targetLongitude, targetLatitude]
            )

            # Add the edge if larger than the minimum distance
            if distance > MINIMUM_DISTANCE:
                gmap.plot([sourceLatitude, targetLatitude], [sourceLongitude, targetLongitude])

                # Plotting the edge weight label
                mid_latitude = (sourceLatitude + targetLatitude) / 2
                mid_longitude = (sourceLongitude + targetLongitude) / 2
                # Make the marker closer to the source point
                qrt_latitude = (sourceLatitude + mid_latitude) / 2
                qrt_longitude = (sourceLongitude + mid_longitude) / 2

                gmap.marker(
                    qrt_latitude,
                    qrt_longitude,
                    title=f"{weight:2f} seconds",
                )

    # Scatter points onto Google Maps
    gmap.scatter(latitude_list, longitude_list)

    # Creating the Google Maps HTML
    gmap.draw("map.html")


# Returns the time taken to travel from the initial node to the target node
def add_weighted_edge(initialNode, targetNode, speedGraph, G, initialOSMNode, targetOSMNode):

    # Get the travel time in seconds using networkx
    travelTime = nx.shortest_path_length(
        speedGraph, initialOSMNode, targetOSMNode, weight="travel_time"
    )

    # Add the edge to the graph
    G.add_edge(
        initialNode.get_ATCOCode(),
        targetNode.get_ATCOCode(),
        weight=travelTime,
    )


# Returns a custom map from OpenStreetMap of England, consisting of all roads
def get_graph_from_pbf():

    # Get regional PBF graph data
    pbf = OSM(REGION_MAP)

    # Extract network with bus gates included
    nodes, edges = pbf.get_network(
        network_type="driving",
        nodes=True,
        extra_attributes=["psv", "bus", "access", "maxspeed"],
    )

    # Filter roads and bus-specific areas
    bus_edges = edges[
        (edges["access"] != "no")
        | (edges["bus"].isin(["yes", "designated"]))
        | (edges["psv"].isin(["yes", "designated"]))
    ].copy()

    # Remove unnecessary attributes
    edges["geometry"] = None
    keep_cols = ["u", "v", "key", "length", "highway", "geometry", "oneway", "maxspeed"]
    bus_edges = bus_edges[[c for c in bus_edges.columns if c in keep_cols]]

    # Delete old edges
    del edges
    gc.collect()

    print("Got to here")
    # Convert to networkx graph with bus edges
    networkxGraph = pbf.to_graph(nodes, bus_edges, graph_type="networkx", osmnx_compatible=True)

    print("Adding edge speeds")
    # Use OSMnx to add speeds and travel times
    networkxGraph = ox.add_edge_speeds(networkxGraph)
    networkxGraph = ox.add_edge_travel_times(networkxGraph)

    # Return graph
    return networkxGraph


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


# Returns the distance in meters using the haversine module
def get_distance_haversize_long_lat(initialNode, targetNode):
    # Nodes are 1-dimensional array [Longitude, Latitude]

    return round(
        haversine(
            (initialNode[0], initialNode[1]),
            [targetNode[0], targetNode[1]],
            unit=Unit.METERS,  # Return in meters
        ),
        2,
    )


# Returns networkx bus access node graph with weights
def get_bus_graph_networkx_with_triangulation(): # Altered name to preserve function
    bus_graph = get_bus_access_node_graph()
    G = nx.DiGraph()
    labels = {}  # For adding custom labels to graph
    coords = []

    # Getting graph for calculating driving speeds
    print("Getting speed graph")
    speedGraph = get_graph_from_pbf()
    print("Speed graph got")

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
        coords.append([accessNode.get_Longitude(), accessNode.get_Latitude()])

    # Finding edges through Delaunay Triangulation
    startNodes = []
    endNodes = []
    accessNodeInitialNearest = []
    accessNodeTargetNearest = []
    delaunay = Delaunay(coords)
    print(len(delaunay.simplices))
    total = len(delaunay.simplices)
    currentSimplice = 0
    for tri in delaunay.simplices:
        # Printing off current progress
        percentage = round((currentSimplice / total) * 100)
        currentSimplice += 1
        print(f"{currentSimplice}/{total}   {percentage}")

        accessNode0Coords = delaunay.points[tri[0]]
        accessNode1Coords = delaunay.points[tri[1]]
        accessNode2Coords = delaunay.points[tri[2]]

        accessNode0 = None
        accessNode1 = None
        accessNode2 = None

        for accessNode in bus_graph:
            # Check if access node is inside the triangulation
            if (
                accessNode.get_Longitude() == accessNode0Coords[0]
                and accessNode.get_Latitude() == accessNode0Coords[1]
            ):
                accessNode0 = accessNode
            elif (
                accessNode.get_Longitude() == accessNode1Coords[0]
                and accessNode.get_Latitude() == accessNode1Coords[1]
            ):
                accessNode1 = accessNode
            elif (
                accessNode.get_Longitude() == accessNode2Coords[0]
                and accessNode.get_Latitude() == accessNode2Coords[1]
            ):
                accessNode2 = accessNode

        # If there is a triangulation, add the edges
        if accessNode0 is not None and accessNode1 is not None and accessNode2 is not None:
            # Using paralellism and mutliprocessing to speed up the getting weight process
            startNodes.extend(
                [accessNode0, accessNode1, accessNode0, accessNode1, accessNode2, accessNode2]
            )
            endNodes.extend(
                [accessNode1, accessNode2, accessNode2, accessNode0, accessNode1, accessNode0]
            )

            # Find nearest nodes to our G node coordinates
            # accessOSMNode0 = ox.distance.nearest_nodes(speedGraph, X=accessNode0.get_Longitude(), Y=accessNode0.get_Latitude())
            # accessOSMNode1 = ox.distance.nearest_nodes(speedGraph, X=accessNode1.get_Longitude(), Y=accessNode1.get_Latitude())
            # accessOSMNode2 = ox.distance.nearest_nodes(speedGraph, X=accessNode2.get_Longitude(), Y=accessNode2.get_Latitude())

            # accessNodeInitialNearest.extend([accessOSMNode0, accessOSMNode1, accessOSMNode0, accessOSMNode1, accessOSMNode2, accessOSMNode2])
            # accessNodeTargetNearest.extend([accessOSMNode1, accessOSMNode2, accessOSMNode2, accessOSMNode0, accessOSMNode1, accessOSMNode0])

    startNodeLong = [node.get_Longitude() for node in startNodes]
    startNodeLat = [node.get_Latitude() for node in startNodes]
    endNodeLong = [node.get_Longitude() for node in endNodes]
    endNodeLat = [node.get_Latitude() for node in endNodes]

    # Batch processing the nearest nodes in one call start and end
    startNodeOSM = ox.nearest_nodes(speedGraph, X=startNodeLong, Y=startNodeLat)
    endNodeOSM = ox.nearest_nodes(speedGraph, X=endNodeLong, Y=endNodeLat)

    cores = max(1, os.cpu_count() // 2)
    thread_map(
        add_weighted_edge,
        startNodes,
        endNodes,
        repeat(speedGraph),
        repeat(G),
        startNodeOSM,
        endNodeOSM,
        chunksize=1,
        total=len(startNodes),
        max_workers=cores,
        bar_format="{n_fmt}/{total_fmt} {percentage:3.0f}%",
        dynamic_ncols=True,
    )

    # Adding edges into networkx graph between access nodes
    # for accessNode in bus_graph:
    #     # Add edge for all nearby neighbours
    #     for neighbour in accessNode.get_Nearby():
    #         G.add_edge(
    #             accessNode.get_ATCOCode(),
    #             neighbour.get_ATCOCode(),
    #             weight=get_weight(accessNode, neighbour),
    #         )

    # Drawing graph
    # draw_networkx_graph(G, labels)

    # Mapping graph
    map_networkx_graph_(G, labels)

    # Save graph as graphml - ungku
    nx.write_graphml_lxml(G, str(GRAPH_PATH))

    # Return graph as networkx format
    return G



### Start of added code ###

# Returns full connected networkx bus AccessNode graph of all possible bus stops (via NaPTAN) with weights
def get_fully_connected_bus_graph_networkx():
    bus_graph = get_bus_access_node_graph() # From initial GenerateBusAccessNodeGraph.py
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


# Returns networkx bus AccessNode graph of all dataset stops and routes with weights
def get_dataset_bus_graph_networkx():
    bus_graph = D_get_bus_access_node_graph() # From Dataset_GenerateBusAccessNodeGraph.py incororating XML data
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


# Combining both functions within one call :
def get_bus_graph_networkx(dataset = 0): # Main function to call

    if dataset == 0:
        G = get_fully_connected_bus_graph_networkx()
    if dataset == 1:
        G = get_dataset_bus_graph_networkx()
    else:
        print("Incorrect parameter value")

    return G


### End of added code ###



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

if __name__ == "__main__":
    get_bus_graph_networkx_with_triangulation(1)
