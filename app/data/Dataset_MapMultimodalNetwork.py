## -- Imports -- ##

from app.data.AccessNode import AccessNode
from app.data.Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
from app.data.Dataset_GenerateWalkingPaths import add_walking_paths
from app.data.Dataset_MapBusAccessNodeGraph import plot_in_gmplot


## -- Obtains graph of BUS ROUTES and WALKING PATHS -- ##


def get_multimodal_graph(plot=0):

    graph = get_bus_access_node_graph()

    graph = add_walking_paths(graph)

    if plot == 1:
        plot_in_gmplot(graph, "app/data/Maps/Mapsmultimodal_network.html", vis=1)

    return graph


### --- Main --- ###

graph = get_multimodal_graph()


# Converting AccessNode graph to pickle file :
WANT_PICKLE = 1
if WANT_PICKLE == True:
    import sys

    sys.setrecursionlimit(5000)
    import pickle

    #pickle.dump(graph, open("multimodal_graph.pkl", "wb"))
    pickle.dump(graph, open("app/data_files/multimodal_graph.pkl", "wb"))


### --- Other Functions --- ###


# Debug function to view AcessNode.Nearby Data :


def print_all_connection_data(graph, limit=-1):

    count = 0
    for node in graph:

        count += 1
        if count == limit:
            break

        connected_nodes = node.Nearby
        replace = []

        for i in connected_nodes:
            j = (i[0].get_ATCOCode(),) + i[1:]
            replace.append(j)

        for j in replace:
            connected_nodes.append(j)
        print(replace)


# print_all_connection_data(graph, 10)


## -- MatPlotLib Mapping -- ##

# Note :
# This section allows for the bus routes and
# walking paths to be togglable when viewed.

import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from gmplot.color import _HTML_COLOR_CODES as colours

# Getting ductionary of colours
import random


def shuffle_dict(d: dict):
    return {k: d[k] for k in random.choices(list(d.keys()), k=len(d))}


colour_dict = {}
colours = shuffle_dict(colours)
colour_list = list(colours.keys())
num_col = 21
for i in range(1, len(colours)):
    colour_dict[i] = colour_list[i]


def plot_in_matplotlib(graph, vis=0):

    fig, ax = plt.subplots()

    bus_lines = []
    walk_lines = []

    for accessNode in graph:

        ax.plot(accessNode.get_Longitude(), accessNode.get_Latitude(), marker="o", markersize=6)

        ax.text(
            accessNode.get_Longitude(),
            accessNode.get_Latitude(),
            accessNode.get_CommonName(),
            fontsize=5,
        )

        for nearbyNode in accessNode.get_Nearby():

            if nearbyNode[1] == "bus":
                (line,) = ax.plot(
                    [accessNode.get_Longitude(), nearbyNode[0].get_Longitude()],
                    [accessNode.get_Latitude(), nearbyNode[0].get_Latitude()],
                    color=colour_dict[nearbyNode[2]],
                    linewidth=4,
                )
                bus_lines.append(line)

            if nearbyNode[1] == "walk":
                (line,) = ax.plot(
                    [accessNode.get_Longitude(), nearbyNode[0].get_Longitude()],
                    [accessNode.get_Latitude(), nearbyNode[0].get_Latitude()],
                    color="black",
                    linewidth=1,
                )
                walk_lines.append(line)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Checkbox area
    rax = ax.inset_axes([0.02, 0.02, 0.15, 0.15])
    check = CheckButtons(rax, ["Bus", "Walk"], [True, True])

    def toggle(label):
        if label == "Bus":
            for line in bus_lines:
                line.set_visible(not line.get_visible())

        elif label == "Walk":
            for line in walk_lines:
                line.set_visible(not line.get_visible())

        plt.draw()

    check.on_clicked(toggle)

    plt.show()

    # import pickle
    # pickle.dump(fig, open('TogglableMultimodalGraph.fig.pickle', 'wb'))


# plot_in_matplotlib(graph)
