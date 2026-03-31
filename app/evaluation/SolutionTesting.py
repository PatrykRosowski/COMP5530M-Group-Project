## -- Imports -- ##

import pickle
import time
import sys
import os
import gmplot
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.AccessNode import AccessNode
from app.data.Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
from app.data.Dataset_GenerateWalkingPaths import add_walking_paths
# from data.Dataset_MapBusAccessNodeGraph import plot_in_gmplot
from app.utils.heatmap_controller import get_heatmap_pairs
from app.graph_testing.Graph_PathFinder import Shortest_Path_Simulation #, PrintCost()


## -- Functions -- ##

def add_heatmap_points_to_graph(graph, points):
    
    coord_pair_index = 0
    ArrayOfAccessNodePairs = []

    for coord_pair in points:

        coord_pair_index += 1
        start_node_coords, end_node_coords = coord_pair[0], coord_pair[1]
        
        start_node = AccessNode({
            'ATCOCode': f"000X{coord_pair_index}",
            'Latitude': start_node_coords[0],
            'Longitude': start_node_coords[1],
            'CommonName': f"Start Node no.{coord_pair_index}",
            'Street': ''
        })

        end_node = AccessNode({
            'ATCOCode': f"111X{coord_pair_index}",
            'Latitude': end_node_coords[0],
            'Longitude': end_node_coords[1],
            'CommonName': f"End Node no.{coord_pair_index}",
            'Street': ''
        })

        graph.append(start_node)
        graph.append(end_node)
        ArrayOfAccessNodePairs.append( (start_node, end_node) )

    return graph, ArrayOfAccessNodePairs


def plot_solution(sol_array, name):

        # sol_array[i] = (parent_node, edge_weight_travelled, mode_of_travel)
        colours = ["blue", "orange", "green", "red", "purple", "yellow", "pink", "white"]
        used_routes = []
        gmap = gmplot.GoogleMapPlotter(54.05, -1.42, 12)

        first = True  # Flag variable keeping track of whether on starting node
        i = 0  # Keep track of position in solution array

        for node in sol_array:
            lat = node[0].get_Latitude()
            lon = node[0].get_Longitude()

            if i > 0 and sol_array[i - 1][2][0] == "bus" and sol_array[i - 1][2][1] not in used_routes:
                used_routes.append(sol_array[i - 1][2][1])

            # Plot node as marker
            gmap.marker(lat, lon, title=node[0].get_CommonName())

            if first == False:
                lat2 = sol_array[i - 1][0].get_Latitude()
                lon2 = sol_array[i - 1][0].get_Longitude()

                if sol_array[i - 1][2][0] == "bus":
                    # Colourful edge for bus
                    gmap.plot(
                        [lat, lat2],
                        [lon, lon2],
                        edge_width=6,
                        color=colours[used_routes.index(sol_array[i - 1][2][1])],
                    )
                else:
                    # Black edge for walking path
                    gmap.plot([lat, lat2], [lon, lon2], edge_width=3)

            first = False  # After running once, start node computed. Turn flag variable off.
            i += 1  # Update index of current node

        # Output to HTML file
        gmap.draw(name)

## -- Main -- ##

if __name__ == '__main__':

    # Number of (start, end) pairs
    NUM_START_END_PAIRS = 3


    run_start = time.time()
    print()
    print("===================================")
    print("Running solution testing script ...")
    print("===================================\n")

    start = time.time()
    graph = get_bus_access_node_graph("Manchester") # Obtains all bus vertices
    # graph = pickle.load(open("app/data_files/manchester_multimodal_graph.pkl", "rb"))
    end = time.time()
    print(f"Bus graph generated in time {end-start:.2f} seconds.\n")

    start = time.time()
    heatmap_points = get_heatmap_pairs(NUM_START_END_PAIRS) # number of (start, end) pairs
    end = time.time()
    print(f"Heatmap co-ordinates obtained in time {end-start:.2f} seconds.\n")

    start = time.time()
    graph, testing_points = add_heatmap_points_to_graph(graph, heatmap_points) # Adds heatmap points as AccessNodes
    end = time.time()
    print(f"Heatmap points added in time {end-start:.2f} seconds.\n")

    start = time.time()
    graph = add_walking_paths(graph) # Generates walking edges using Euclidian distance
    end = time.time()
    print(f"Walking paths generated in time {end-start:.2f} seconds.\n")

    start = time.time()
    solution_stats = {} # { 1: (path, cost), 2: (path, cost), ... }
    time_arr = []
    edge_weight_dict = {} # Stores computed edge weights (to speed calculations)
    index = 0
    print("Journeys computed:")
    for pair in testing_points:
        stime = time.time()
        index += 1
        solution_path, total_cost = Shortest_Path_Simulation(graph, pair[0], pair[1], edge_weight_dict)
        solution_stats[index] = (solution_path, total_cost)
        print(f"{index}.. ", end='')
        etime = time.time()
        time_arr.append(f"{etime-stime:.2f}")
    end = time.time()
    print(f"\nTesting complete (for {NUM_START_END_PAIRS} journeys) in time {end-start:.2f} seconds.")
    print(f"Timings for each file: {time_arr}\n")


    print("\nSolutions:")
    for i in solution_stats:
        print(solution_stats[i][1],', ', end='')

    run_end = time.time()
    print("\n\n\n====================================================")
    print(f"Script successfully executed in time: {run_end-run_start:.2f} seconds.")
    print("====================================================\n")

    count = 0
    for path in solution_stats:
         count+=1
         plot_solution(solution_stats[path][0], f"app/evaluation/solutions/file_num_{count}.html")

    ## -- End of script -- ##