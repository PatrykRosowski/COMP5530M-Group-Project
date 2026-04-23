## -- Imports -- ##

import pickle
import time
import sys
import os
import gmplot
import shutil
from gmplot.color import _HTML_COLOR_CODES as COLOURS

start_time = time.time()

from app.data.AccessNode import AccessNode
from app.data.Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
from app.data.Dataset_GenerateBusAccessNodeGraph import get_bus_route_json
from app.data.Dataset_GenerateBusAccessNodeGraph import remove_bus_route
from app.data.Dataset_GenerateBusAccessNodeGraph import add_bus_route
from app.data.Dataset_GenerateWalkingPaths import add_walking_paths
from app.data.Dataset_MapBusAccessNodeGraph import plot_in_gmplot
from app.utils.heatmap_controller import get_heatmap_pairs
from app.graph_testing.Graph_PathFinder import Shortest_Path_Simulation
from app.evaluation.SolutionEvaluation import print_all_statistics
from app.evaluation.SolutionEvaluation import sec_to_hmsms
from app.evaluation.SolutionEvaluation import compare_graph_stats
from app.evaluation.SolutionEvaluation import get_all_graph_statistics
from app.evaluation.SolutionEvaluation import get_all_solution_statistics

end_time = time.time()
print(f"\n\nImports successfully processed in time {end_time-start_time:.2f} seconds.\n")


## -- Functions -- ##


def my_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def add_heatmap_points_to_graph(graph, points):

    coord_pair_index = 0
    ArrayOfAccessNodePairs = []

    for coord_pair in points:
        coord_pair_index += 1
        start_node_coords, end_node_coords = coord_pair[0], coord_pair[1]

        start_node = AccessNode(
            {
                "ATCOCode": f"000X{coord_pair_index}",
                "Latitude": start_node_coords[0],
                "Longitude": start_node_coords[1],
                "CommonName": f"Start Node no.{coord_pair_index}",
                "Street": "",
            }
        )

        end_node = AccessNode(
            {
                "ATCOCode": f"111X{coord_pair_index}",
                "Latitude": end_node_coords[0],
                "Longitude": end_node_coords[1],
                "CommonName": f"End Node no.{coord_pair_index}",
                "Street": "",
            }
        )

        graph.append(start_node)
        graph.append(end_node)
        ArrayOfAccessNodePairs.append((start_node, end_node))

    return graph, ArrayOfAccessNodePairs


def plot_eval_solution(sol_array, name, city):

    # sol_array[i] = (parent_node, edge_weight_travelled, mode_of_travel)
    full_colours = list(COLOURS.keys())
    colours = [
        "blue",
        "orange",
        "green",
        "red",
        "purple",
        "yellow",
        "pink",
        "brown",
        "white",
    ]  # , "cyan", "lime", "navy", "gold", "maroon"]
    for col in full_colours:
        if col not in colours:
            colours.append(col)

    used_routes = []
    if city == "Harrogate":
        gmap = gmplot.GoogleMapPlotter(54.05, -1.42, 12)
    if city == "Manchester":
        gmap = gmplot.GoogleMapPlotter(53.53, -2.26, 10)

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


def evaluate_graph(graph, graph_name_string):

    graph_stats_array = get_all_graph_statistics(graph)

    graph_stats_json = {
        'graph': str('"')+graph_name_string+str('"'),
        'number of vertices': graph_stats_array[4],
        'number of edges': graph_stats_array[5],
        'average degree (number of busses passing through stop)': f"{graph_stats_array[6]:.2f}",
        #'graph radius (minimum eccentricity)': f"{graph_stats_array[2]} nodes",
        'graph diameter (maximum eccentricity)': f"{graph_stats_array[3]} nodes", # Used for MESP
        'maximum degree centrality': f"{graph_stats_array[0]:.6f}",
        'number of nodes with 90%+ of max degree centrality': graph_stats_array[1],
        # -- cannot use -- 'journeys_computed': len(oldg_solutions),
        # -- cannot use -- 'mean travel time': f"{oldg_solution_stats_array[0]:.3f} seconds",
        # -- cannot use -- 'median travel time': f"{oldg_solution_stats_array[1]:.3f} seconds",
        # -- cannot use -- 'average number of busses per journey': f"{oldg_solution_stats_array[2]:.1f} per trip",
        # -- cannot use -- 'shortest journey time': f"{oldg_solution_stats_array[3]:.3f} seconds",
        # -- cannot use -- 'average time of shortest 10% of journeys': f"{oldg_solution_stats_array[4]:.3f} seconds",
        # -- cannot use -- 'longest journey time': f"{oldg_solution_stats_array[5]:.3f} seconds",
        # -- cannot use -- 'average time of longest 10% of journeys': f"{oldg_solution_stats_array[6]:.3f} seconds"
    }

    return graph_stats_json


def run_full_evaluation(
    num_of_HM_pairs,
    network_json_stops,
    old_network_json_routes,
    new_network_json_routes,
):

    old_graph = get_bus_access_node_graph(network_json_stops, old_network_json_routes)
    new_graph = get_bus_access_node_graph(network_json_stops, new_network_json_routes)

    oldg_graph_stats_array = get_all_graph_statistics(old_graph)  # [:20]) # graph-based metrics
    newg_graph_stats_array = get_all_graph_statistics(new_graph)  # graph-based metrics

    heatmap_points = get_heatmap_pairs(num_of_HM_pairs)

    testing_points = [[], []]
    old_graph, testing_points[0] = add_heatmap_points_to_graph(old_graph, heatmap_points)
    new_graph, testing_points[1] = add_heatmap_points_to_graph(new_graph, heatmap_points)

    old_graph = add_walking_paths(old_graph)
    new_graph = add_walking_paths(new_graph)

    oldg_edge_weight_dict, newg_edge_weight_dict = {}, {}

    oldg_solutions, newg_solutions = {}, {}  # solution path, weight, cost

    index = 0
    for point in range(len(testing_points[0])):

        oldg_pair = testing_points[0][point]
        newg_pair = testing_points[1][point]
        index += 1

        o_solution_path, o_total_weight, o_total_cost = Shortest_Path_Simulation(
            old_graph, oldg_pair[0], oldg_pair[1], oldg_edge_weight_dict
        )

        n_solution_path, n_total_weight, n_total_cost = Shortest_Path_Simulation(
            new_graph, newg_pair[0], newg_pair[1], newg_edge_weight_dict
        )

        oldg_solutions[index] = (o_solution_path, o_total_weight, o_total_cost)
        newg_solutions[index] = (n_solution_path, n_total_weight, n_total_cost)

        # my_print(str(index) + ".. ")

    compare_array = compare_graph_stats(
        oldg_solutions, newg_solutions, min(len(testing_points[0]), len(testing_points[1]))
    )

    # Printing Solutions :
    # count = 0
    # for i in oldg_solutions:
    #     count+=1
    #     print(f"File {count}: weight = {oldg_solutions[i][1]:.2f}, path-cost = {oldg_solutions[i][2]:.4f}")
    # print()
    # count = 0
    # for j in newg_solutions:
    #     count+=1
    #     print(f"File {count}: weight = {newg_solutions[j][1]:.2f}, path-cost = {newg_solutions[j][2]:.4f}")
    # print()

    oldg_delete = [
        journey
        for journey in oldg_solutions
        if oldg_solutions[journey][1] == float("inf") or oldg_solutions[journey][1] == 0
    ]
    for journey in oldg_delete:
        del oldg_solutions[journey]

    newg_delete = [
        journey
        for journey in newg_solutions
        if newg_solutions[journey][1] == float("inf") or newg_solutions[journey][1] == 0
    ]
    for journey in newg_delete:
        del newg_solutions[journey]

    oldg_solution_stats_array = get_all_solution_statistics(
        oldg_solutions
    )  # solution-based metrics
    newg_solution_stats_array = get_all_solution_statistics(
        newg_solutions
    )  # solution-based metrics

    old_graph_stats_json = {
        'graph name': str('"')+'Existing Bus Network'+str('"'),
        'number of vertices': f"{oldg_graph_stats_array[4]:,}",
        'number of edges': f"{oldg_graph_stats_array[5]:,}",
        'average degree (number of busses passing through stop)': f"{oldg_graph_stats_array[6]:.2f}",
        #'graph radius (minimum eccentricity)': f"{oldg_graph_stats_array[2]} nodes",
        'graph diameter (maximum eccentricity)': f"{oldg_graph_stats_array[3]} nodes",
        'maximum degree centrality': f"{oldg_graph_stats_array[0]:.6f}",
        'number of nodes with 90%+ of max degree centrality': oldg_graph_stats_array[1],
        'journeys_computed': len(oldg_solutions),
        'mean travel time': f"{oldg_solution_stats_array[0]:,.3f} seconds",
        'median travel time': f"{oldg_solution_stats_array[1]:,.3f} seconds",
        'average number of busses per journey': f"{oldg_solution_stats_array[2]:.1f} per trip",
        'shortest journey time': f"{oldg_solution_stats_array[3]:,.3f} seconds",
        'average time of shortest 10% of journeys': f"{oldg_solution_stats_array[4]:,.3f} seconds",
        'longest journey time': f"{oldg_solution_stats_array[5]:,.3f} seconds",
        'average time of longest 10% of journeys': f"{oldg_solution_stats_array[6]:,.3f} seconds"
    }

    new_graph_stats_json = {
        'graph name': str('"')+'Newly Proposed Bus Network'+str('"'),
        'number of vertices': f"{newg_graph_stats_array[4]:,}",
        'number of edges': f"{newg_graph_stats_array[5]:,}",
        'average degree (number of busses passing through stop)': f"{newg_graph_stats_array[6]:.2f}",
        #'graph radius (minimum eccentricity)': f"{newg_graph_stats_array[2]} nodes",
        'graph diameter (maximum eccentricity)': f"{newg_graph_stats_array[3]} nodes",
        'maximum degree centrality': f"{newg_graph_stats_array[0]:.6f}",
        'number of nodes with 90%+ of max degree centrality': newg_graph_stats_array[1],
        'journeys_computed': len(newg_solutions),
        'mean travel time': f"{newg_solution_stats_array[0]:,.3f} seconds",
        'median travel time': f"{newg_solution_stats_array[1]:,.3f} seconds",
        'average number of busses per journey': f"{newg_solution_stats_array[2]:.1f} per trip",
        'shortest journey time': f"{newg_solution_stats_array[3]:,.3f} seconds",
        'average time of shortest 10% of journeys': f"{newg_solution_stats_array[4]:,.3f} seconds",
        'longest journey time': f"{newg_solution_stats_array[5]:,.3f} seconds",
        'average time of longest 10% of journeys': f"{newg_solution_stats_array[6]:,.3f} seconds"
    }

    total_journeys = sum(compare_array)
    comparing_stats_json = {
        "total journeys computed": total_journeys,
        "number of better journeys in old network": compare_array[0],
        "percentage better journeys in old network": f"{((compare_array[0]/total_journeys)*100):.2f}%",
        "number of better journeys in new network": compare_array[1],
        "number of better journeys in new network": f"{((compare_array[1]/total_journeys)*100):.2f}%",
        "number of equally efficient journies": compare_array[2],
        "number of journeys with same efficiency": f"{((compare_array[2]/total_journeys)*100):.2f}%",
    }

    output_json = {
        "old_graph_stats": old_graph_stats_json,
        "new_graph_stats": new_graph_stats_json,
        "comparing_stats": comparing_stats_json,
    }

    # Printing json output :
    for i in output_json:
        print(f"\n\x7b\n{i} :")
        for j in output_json[i]:
            print(f"\t\x7b {j}: {output_json[i][j]} \x7d")
        print("}")

    return output_json


## -- Main -- ##

"""
if __name__ == "__main__":


    ## -- Initialisation -- ##

    # Number of (start, end) pairs
    NUM_START_END_PAIRS = 20

    dir = "app/evaluation/solutions"
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    run_start = time.time()
    print("===================================")
    print("Running solution testing script ...")
    print("===================================\n")


    ## -- Obtaining Bus Graphs -- ##

    # Existing bus graph -
    start = time.time()
    graph = get_bus_access_node_graph(
        "app/data_files/Datasets/Manchester/AllBusStopData.json",
        "app/data_files/Datasets/Manchester/AllRoutesData.json"
    )  # Obtains all bus vertices
    # graph = pickle.load(open("app/data_files/manchester_multimodal_graph.pkl", "rb"))
    end = time.time()
    print(f"Bus graph generated in time {end-start:.2f} seconds.\n")

    # Newly proposed bus graph -
    # Space for getting the newly proposed bus graph


    ## -- Obtaining Heatmap Points -- ##

    start = time.time()
    heatmap_points = get_heatmap_pairs(NUM_START_END_PAIRS)  # number of (start, end) pairs
    end = time.time()
    print(f"Heatmap co-ordinates obtained in time {end-start:.2f} seconds.\n")

    start = time.time()
    graph, testing_points = add_heatmap_points_to_graph(graph, heatmap_points)  # Adds heatmap points as AccessNodes
    end = time.time()
    print(f"Heatmap points added in time {end-start:.2f} seconds.\n")


    ## -- Adding Walking Paths to all Nodes -- ##

    start = time.time()
    graph = add_walking_paths(graph)  # Generates walking edges using Euclidian distance
    end = time.time()
    print(f"Walking paths generated in time {end-start:.2f} seconds.\n")


    # Displaying graph :
    plot_in_gmplot(graph, "app/evaluation/solutions/graph_with_hm_points.html")
    print("Full map of bus stops and heatmap points connected by bus routes and walking paths generated in app/evaluation/solutions.\n")


    ## -- Running (custom) A* and Storing Output Data -- ##

    start = time.time()

    # Dictionary that stores output of running A*
    solution_stats = {}  # { 1: (path, weight, cost), 2: (path, weight, cost), ... }

    time_arr = []
    edge_weight_dict = {}  # Stores computed edge weights (to speed calculations)
    index = 0
    print("Computing journeys:")
    for pair in testing_points:
        stime = time.time()
        index += 1
        solution_path, total_weight, total_cost = Shortest_Path_Simulation(
            graph, pair[0], pair[1], edge_weight_dict, show_progress=False
        )
        solution_stats[index] = (solution_path, total_weight, total_cost)

        my_print(str(index) + ".. ")

        etime = time.time()
        time_arr.append(f"{etime-stime:.2f}")
    end = time.time()
    print(f"\nTesting complete (for {NUM_START_END_PAIRS} journeys) in time {end-start:.2f} seconds.\n")
    print(f"Timings for each file: {time_arr}\n")


    ## -- Displaying Solution Outputs -- ##

    print("\nSolutions:")
    count = 0
    num_of_inf = 0
    for i in solution_stats:
        count += 1
        # print(f"File {count}: weight = {solution_stats[i][1]:.2f}, path-cost = {solution_stats[i][2]:.4f}")
        if solution_stats[i][1] == float("inf"):
            num_of_inf += 1
    print(f"\nNumber of failed journeys = {num_of_inf}/{NUM_START_END_PAIRS}")

    run_end = time.time()
    print("\n\n\n====================================================")
    print(f"Script successfully executed in time: {run_end-run_start:.2f} seconds.")
    print("====================================================\n")


    ## -- Plotting Solutions in app/evaluation/solutions -- ##

    count = 0
    for path in solution_stats:
        count += 1
        try:
            plot_eval_solution(
                solution_stats[path][0],
                f"app/evaluation/solutions/file_num_{count}.html",
                "Manchester",
            )
        except:
            # print(f"Exception occured, couldn't generate for file {count}")
            pass


    ## -- Outputting Solution Statistics -- ##


    # filtered_solution_stats = {}
    # print(f"Ignoring files: ", end = '')
    # for i in solution_stats:
    #     if solution_stats[i][1] != float('inf') and solution_stats[i][1] != 0:
    #         filtered_solution_stats[i] = solution_stats[i] #{i: solution_stats[i] for i in solution_stats.keys() and solution_stats[i][1] != float('inf')}
    #     else:
    #         print(f"{i} ", end = '')
    
    # print_all_statistics(filtered_solution_stats, "'Existing Bus Network'")
    # # Space for printing stats of proposed bus network


    ## -- End of script -- ##
#"""

if __name__ == "__main__":
    manchesterRoutesOriginal = get_bus_route_json("Manchester")  # Get original bus routes.
    manchesterRoutesEdited = get_bus_route_json("Manchester")  # Edit original bus routes.
    manchesterRoutesEdited = remove_bus_route(manchesterRoutesEdited, "Pregenerated-0")
    run_full_evaluation(
        30,
        "app/data_files/Datasets/Manchester/AllBusStopData.json",
        manchesterRoutesOriginal,
        manchesterRoutesEdited,
    )

    # Runtime of entire script
    end_time = time.time()
    print(f"\nEntire script run in total time {sec_to_hmsms(end_time - start_time)}\n\n")
