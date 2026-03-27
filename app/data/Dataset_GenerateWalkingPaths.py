## -- Imports -- ##

from math import sin, cos, sqrt, atan2, radians  # for Haversine distance
from Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
from Dataset_MapBusAccessNodeGraph import plot_in_gmplot
from AccessNode import AccessNode

import time


# Important Definitions :

PLOT_WALK = 0


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

    dist = R * c * 1000 # converting from km to m
    return dist




## -- Function to generate walking paths given bus graph -- ##

WALKING_DIST_RADIUS = 500  # metres

def add_walking_paths(graph):

    # For loop comparing distance of every node
    for i in range(0, len(graph)):
        curNode = graph[i]

        for j in range(i, len(graph)):
            compNode = graph[j]
            
            straightline_dist = coord_to_km(curNode.Latitude, curNode.Longitude, compNode.Latitude, compNode.Longitude)
            
            if straightline_dist <= WALKING_DIST_RADIUS:
                
                # Note: straightline/euclidian distance is the furthest away/ worst case distance
                # i.e. any node outside WALKING_DIST_RADIUS "must" be further away
                # So here, taking the distance < 500m, add walking edges if they are within 500m staright-line distance

                AccessNode.addNearbyStop(curNode, (compNode, None, "walk", None)) # (Node, weight, mode, route)
                AccessNode.addNearbyStop(compNode, (curNode, None, "walk", None)) # (Node, weight, mode, route)
                # Need to make the path bi-directional

    return graph


## -- Main -- ##

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
