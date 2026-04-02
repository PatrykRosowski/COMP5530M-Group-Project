## -- Imports -- ##

from math import sin, cos, sqrt, atan2, radians  # for Haversine distance
from app.data.AccessNode import AccessNode

import time


# Important Definitions :

PLOT_WALK = 0
DEGREE_DIFF = 0.03
CLOSEST_NODES = 18


## -- Haversine Distance between 2 coordinates -- ##


def coord_to_km(lat1, long1, lat2, long2):

    R = 6373.0  # approx radius of Earth in km

    La1 = radians(lat1)
    Lo1 = radians(long1)
    La2 = radians(lat2)
    Lo2 = radians(long2)

    lat_diff = abs(La2 - La1)
    lon_diff = abs(Lo2 - Lo1)

    a = sin(lat_diff / 2) ** 2 + cos(La1) * cos(La2) * sin(lon_diff / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = R * c * 1000  # converting from km to m
    return dist


## -- Function to generate walking paths given bus graph -- ##

WALKING_DIST_RADIUS = 5000  # metres


def add_walking_paths(graph):

    # Pre-extract coordinates to avoid long methods calls in loops
    coords = [(node.Latitude, node.Longitude) for node in graph]

    # For loop comparing distance of every node
    for i in range(0, len(graph)):
        curNode = graph[i]
        curLat, curLon = coords[i]
        walkCandidates = []

        for j in range(len(graph)):
            compNode = graph[j]
            compLat, compLon = coords[j]

            # Quick calculation to elimnate far away nodes
            if abs(curLat - compLat) > DEGREE_DIFF:
                continue

            if abs(curLon - compLon) > DEGREE_DIFF:
                continue

            straightline_dist = coord_to_km(curLat, curLon, compLat, compLon)

            if straightline_dist <= WALKING_DIST_RADIUS:
                walkCandidates.append((straightline_dist, graph[j]))

        # Sort candidates by walking distance
        walkCandidates.sort(key=lambda x: x[0])

        # Keep only CLOSEST_NODES walking neighbours
        walkCandidates = walkCandidates[:CLOSEST_NODES]

        # Adding bi-directional walking candidates
        for dist, compNode in walkCandidates:
            curNode.addNearbyStop((compNode, "walk", None))
            compNode.addNearbyStop((compNode, "walk", None))

    return graph


## -- Main -- ##


if __name__ == "__main__":

    from Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
    from Dataset_MapBusAccessNodeGraph import plot_in_gmplot

    # Runs mapping function, which calls graph generation function
    graph = get_bus_access_node_graph()
    for node in graph:
        node.Nearby = []  # Removes all existing bus edges

    start = time.time()
    graph = add_walking_paths(graph)  # Adds walking path edges
    end = time.time()
    # print(f"Walking paths succesfully added in time {end-start:.3f}")

    if PLOT_WALK == 1:
        plot_in_gmplot(graph, "apps/data/Walking_Path_Generation/Maps/walking_paths_map.html")
