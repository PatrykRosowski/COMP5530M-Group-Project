from GenerateBusAccessNodeGraph import get_bus_access_node_graph
import matplotlib.pyplot as plt


# Plotting a map of the whole graph including edges
def map_bus_access_node_graph():
    graph = get_bus_access_node_graph()

    for accessNode in graph:
        # Plotting the individual graph node
        plt.plot(accessNode.get_Latitude(), accessNode.get_Longitude(), marker="o", markersize=6)
        plt.text(accessNode.get_Latitude(), accessNode.get_Longitude(), accessNode.get_CommonName())

        # Plotting edges to all nearby bus stops
        for nearbyNode in accessNode.get_Nearby():
            plt.plot(
                [accessNode.get_Latitude(), nearbyNode.get_Latitude()],
                [accessNode.get_Longitude(), nearbyNode.get_Longitude()],
            )

    plt.show()


map_bus_access_node_graph()
