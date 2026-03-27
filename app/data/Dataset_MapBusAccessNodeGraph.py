### --- Imports --- ###

from Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph

import matplotlib.pyplot as plt
import gmplot
from gmplot.color import _HTML_COLOR_CODES as colours
import folium

import random


### --- Graph Colouring --- ###

ROUTES_VIS = 1  # Do not change.
# Note :
# ROUTES_VIS = 0 -> black edges for all bus routes
# ROUTES_VIS = 1 -> unique edge colour per bus route


# Shuffling a given dictionary :
def shuffle_dict(d: dict):
    return {k: d[k] for k in random.choices(list(d.keys()), k=len(d))}


# Dictionary of colours
colour_dict = {}

# Possible colours from gmplot.color, shuffled.
colours = shuffle_dict(colours)

# Obtaining possible colours as an iterable list
colour_list = list(colours.keys())

# Enumerating (possible) colours in colour_dict :
for i in range(1, len(colours)):
    colour_dict[i] = colour_list[i]


### --- Plotting Bus Map --- ###


## -- MatPlotLib Mapping -- ##


def plot_in_matplotlib(graph, vis=0):

    for accessNode in graph:
        # Plotting the individual graph node
        plt.plot(accessNode.get_Longitude(), accessNode.get_Latitude(), marker="o", markersize=6)
        plt.text(accessNode.get_Longitude(), accessNode.get_Latitude(), accessNode.get_CommonName())

        plt.xlabel("Longitude")
        plt.ylabel("Latitude")

        # Plotting edges to all nearby bus stops
        for nearbyNode in accessNode.get_Nearby():
            if vis == 1:
                plt.plot(
                    [accessNode.get_Longitude(), nearbyNode[0].get_Longitude()],
                    [accessNode.get_Latitude(), nearbyNode[0].get_Latitude()],
                    color=colour_dict[nearbyNode[2]],
                )
            else:
                plt.plot(
                    [accessNode.get_Longitude(), nearbyNode[0].get_Longitude()],
                    [accessNode.get_Latitude(), nearbyNode[0].get_Latitude()],
                )

    plt.show()


## -- GMPlot Mapping -- ##


def plot_in_gmplot(graph, graph_name, vis=0):

    gmap = gmplot.GoogleMapPlotter(54.05, -1.42, 12)

    for accessNode in graph:
        lat = accessNode.get_Latitude()
        lon = accessNode.get_Longitude()

        # Plot node as marker
        gmap.marker(lat, lon, title=accessNode.get_CommonName())

        # Draw edges to nearby nodes
        for nearbyNode in accessNode.get_Nearby():

            if vis == 1 and nearbyNode[1] == "bus":
                lat_list = [lat, nearbyNode[0].get_Latitude()]
                lon_list = [lon, nearbyNode[0].get_Longitude()]
                gmap.plot(lat_list, lon_list, edge_width=3, color=colour_dict[nearbyNode[2]])
            elif vis == 1 and nearbyNode[1] == "walk":
                lat_list = [lat, nearbyNode[0].get_Latitude()]
                lon_list = [lon, nearbyNode[0].get_Longitude()]
                gmap.plot(lat_list, lon_list, edge_width=1)
            else:
                lat_list = [lat, nearbyNode[0].get_Latitude()]
                lon_list = [lon, nearbyNode[0].get_Longitude()]
                gmap.plot(lat_list, lon_list, edge_width=2)

    # Output to HTML file
    gmap.draw(graph_name)


## -- Folium Mapping -- ##


def plot_in_folium(graph, vis=0):

    m = folium.Map(location=[54.05, -1.42], zoom_start=12)

    for accessNode in graph:
        lat = accessNode.get_Latitude()
        lon = accessNode.get_Longitude()

        folium.Marker([lat, lon], popup=accessNode.get_CommonName()).add_to(m)

        for nearbyNode in accessNode.get_Nearby():

            if vis == 1:
                folium.PolyLine(
                    [
                        [lat, lon],
                        [nearbyNode[0].get_Latitude(), nearbyNode[0].get_Longitude()],
                    ],
                    color=colour_dict[nearbyNode[2]],
                ).add_to(m)

            else:
                folium.PolyLine(
                    [
                        [lat, lon],
                        [nearbyNode[0].get_Latitude(), nearbyNode[0].get_Longitude()],
                    ]
                ).add_to(m)

    m.save("app/data/Bus_Route_Generation/Maps/folium_map.html")


def map_bus_access_node_graph(vis=1):

    # Obtaining AccessNodes
    graph = get_bus_access_node_graph(vis)

    # plot_in_matplotlib(graph, vis)

    plot_in_gmplot(graph, "app/data/Bus_Route_Generation/Maps/full_gmplot_bus_map.html", vis)

    # plot_in_folium(graph, vis)


### Main ###

# Runs mapping function, which calls graph generation function
# map_bus_access_node_graph(ROUTES_VIS) # Do not change.
