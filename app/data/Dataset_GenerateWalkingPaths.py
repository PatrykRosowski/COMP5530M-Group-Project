## -- Imports -- ##

from math import sin, cos, sqrt, atan2, radians # for Haversine distance
from Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
from Dataset_MapBusAccessNodeGraph import plot_in_gmplot
from AccessNode import AccessNode

# Important Definitions :

WALKING_DIST_RADIUS = 0.5 #km
PLOT_WALK = 0


## -- Haversine Distance between 2 coordinates -- ##

def coord_to_km(lat1, long1, lat2, long2):

    R = 6373.0 # approx radius of Earth in km

    La1 = radians(lat1)
    Lo1 = radians(long1)
    La2 = radians(lat2)
    Lo2 = radians(long2)

    lat_diff = abs(La2 - La1)
    lon_diff = abs(Lo2 - Lo1)

    a = sin(lat_diff / 2)**2 + cos(La1) * cos(La2) * sin(lon_diff / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = R * c
    return dist
    

## -- Function to generate walking paths given bus graph -- ##

def add_walking_paths(graph):
    
    # For loop comparing distance of every node
    for i in range(0, len(graph)):
        curNode = graph[i]

        for j in range(i, len(graph)):
            compNode = graph[j]

            dist = coord_to_km(curNode.get_Latitude(), curNode.get_Longitude(),
                               compNode.get_Latitude(), compNode.get_Longitude())

            if dist <= WALKING_DIST_RADIUS:
                AccessNode.addNearbyStop( curNode, (compNode, 'walk', None) )
                AccessNode.addNearbyStop( compNode, (curNode, 'walk', None) )
                # Need to make the path bi-directional

    return graph


## -- Main -- ##

# Runs mapping function, which calls graph generation function
graph = get_bus_access_node_graph()
for node in graph:
    node.Nearby = [] # Removes all existing bus edges

graph = add_walking_paths(graph) # Adds walking path edges
if PLOT_WALK == 1:
    plot_in_gmplot(graph, "./Maps/walking_paths_map.html")
