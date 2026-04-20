## -- Imports and Functions -- ##

import networkx as nx
import matplotlib.pyplot as plt

def draw_networkx_graph(G, labels, edge_para="weight"):
    pos = nx.spring_layout(G)  # easier to understand graph layout (nodes repel each other)
    nx.draw_networkx_nodes(G, pos, node_size=30, alpha=0.5)
    nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=7)
    nx.draw_networkx_edges(G, pos=pos, alpha=0.5, width=0.5)
    edge_labels = nx.get_edge_attributes(G, edge_para)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5)

    plt.show()

def AccessNode_to_NetworkX(graph):

    G = nx.DiGraph()
    labels = {}  # For adding custom labels to graph

    # Adding access nodes to networkx graph along with attributes
    for accessNode in graph:
        G.add_node(
            accessNode.get_ATCOCode(),
            CommonName=accessNode.get_CommonName(),
            Street=accessNode.get_Street(),
            Longitude=accessNode.get_Longitude(),
            Latitude=accessNode.get_Latitude(),
        )
        labels[accessNode.get_ATCOCode()] = accessNode.get_CommonName()

    # Adding edges into networkx graph between access nodes
    for accessNode in graph:
        # Add edge for all nearby neighbours
        for neighbour in accessNode.get_Nearby():
            G.add_edge(
                accessNode.get_ATCOCode(),
                neighbour[0].get_ATCOCode(),
                weight=1,
            )

    # Save graph as graphml - ungku
    # nx.write_graphml_lxml(G, "bus_graph.graphml")#

    # Plot the directed graph -
    #import matplotlib.pyplot as plt
    #plt.figure()
    #nx.draw_networkx(G)
    # draw_networkx_graph(G, '')

    # Return graph as networkx format
    return G


## -- Statistics Functions -- ##


def sec_to_hmsms(seconds):

    # input : (int) seconds
    # output : (str) hour-minute-second-milisecond

    s, ms = divmod(seconds, 1)
    s = int(s)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    ms = ms * 10
    return f"{h}h {m}m {s}s {ms:.1f}ms"


def average_travel_time(solution_stats_arr):

    edgeweight_array = [solution_stats_arr[i][1] for i in solution_stats_arr]

    total_tt = 0
    num_paths = len(edgeweight_array)
    
    for weight in edgeweight_array:

        #if weight == float('inf'):
        #    num_paths -= 1
        #else:
        total_tt += weight

    mean_tt = total_tt / num_paths
    
    edgeweight_array.sort()
    if num_paths%2 == 1:
        median_tt = edgeweight_array[ num_paths//2 + 1 ]
    else:
        w1 = edgeweight_array[ num_paths//2 ]
        w2 = edgeweight_array[ num_paths//2 + 1 ]
        median_tt = (w1 + w2)/2

    return mean_tt, median_tt # :.3f


def number_of_busses_taken(modeInfo_array):

    bus_number = 0
    prev_edge = None

    for edge in modeInfo_array:

        if edge[2][0] == 'walk':
            pass
        elif edge[2][0] == 'bus':
            if prev_edge[2][0] == 'walk':
                bus_number += 1
            elif prev_edge[2][0] == 'bus' and prev_edge[2][1] != edge[2][1]:
                bus_number += 1
            else:
                pass
        else:
            break

        prev_edge = edge

    return bus_number # int


def mean_busses_taken(solution_stats_arr):

    solutionPath_array = [solution_stats_arr[i][0] for i in solution_stats_arr]
    num_paths = len(solutionPath_array)

    total_bus_num = 0
    for route_list in solutionPath_array:
        total_bus_num += number_of_busses_taken(route_list)

    avg_bus_num = total_bus_num / num_paths
    return avg_bus_num # :.1f


def best_and_worst_avg_travel_time(solution_stats_arr):

    edgeweight_array = [solution_stats_arr[i][1] for i in solution_stats_arr]
    edgeweight_array.sort()
    
    num_of_paths = len(solution_stats_arr)
    ten_percent_size = num_of_paths // 10
    if ten_percent_size == 0:
        ten_percent_size = 1
    ninety_percent_size = num_of_paths - ten_percent_size

    lower_sum = 0
    for weight in edgeweight_array[:ten_percent_size]:
        lower_sum += weight
    lower_avg = lower_sum / ten_percent_size

    upper_sum = 0
    for weight in edgeweight_array[ninety_percent_size:]:
        upper_sum += weight
    upper_avg = upper_sum / ten_percent_size

    best_case = edgeweight_array[0]
    worst_case = edgeweight_array[-1]

    return best_case, lower_avg, worst_case, upper_avg # :.3f


def compare_graph_stats(old_solutions, new_solutions, len_test_points):

    compare_array = [0, 0, 0] # old_better, new_better, same_weight
    
    for journey in range(1, len_test_points+1):
        oldg_weight = old_solutions[journey][1]
        newg_weight = new_solutions[journey][1]
        if oldg_weight > newg_weight:
            compare_array[0] += 1
        elif oldg_weight < newg_weight:
            compare_array[1] += 1
        else:
            compare_array[2] += 1

    return compare_array # list(int, int, int)


def vertices_and_edges(graph, nx_bool = False):

    if nx_bool == False:
        G = AccessNode_to_NetworkX(graph)
    else:
        G = graph

    num_vertices = G.number_of_nodes()
    num_edges = G.number_of_edges()

    return num_vertices, num_edges


def average_degree(graph):

    degree_sum = 0
    total_vertices = len(graph)

    for node in graph:

        degree_sum += len( [neighbour for neighbour in node.Nearby if neighbour[1] == "bus"] )

    avg_degree = degree_sum / total_vertices
    return avg_degree # :.3f


def degree_centrality(graph, nx_bool = False):

    if nx_bool == False:
        G = AccessNode_to_NetworkX(graph)
    else:
        G = graph

    deg_cent_arr = nx.degree_centrality(G)
    # return deg_cent_arr

    highest_deg_cent = max(deg_cent_arr.values())
    top_10_percent = highest_deg_cent * 0.9

    num_high_deg_cent = 0
    for node in deg_cent_arr:
        if deg_cent_arr[node] >= top_10_percent:
            num_high_deg_cent += 1

    return highest_deg_cent, num_high_deg_cent


def vertex_connectivity(graph, nx_bool = False):

    if nx_bool == False:
        G = AccessNode_to_NetworkX(graph)
    else:
        G = graph
    
    return nx.edge_connectivity(G)



def get_dict_max(dic):
    return dic[max(dic, key=dic.get)]


def eccentricity(graph, nx_bool = False):

    if nx_bool == False:
        G = AccessNode_to_NetworkX(graph)
    else:
        G = graph

    #nodes_eccen = dict(nx.eccentricity(G))
    shortest_dist_dic = dict(nx.shortest_path_length(G))
    
    vertex_eccen = []
    for jour in shortest_dist_dic:
       vertex_eccen.append(get_dict_max(shortest_dist_dic[jour]))
       #if vertex_eccen[-1] == 2:
           #print(shortest_dist_dic[jour])

    num_of_zero = vertex_eccen.count(0)
    for i in range(num_of_zero):
       vertex_eccen.remove(0)

    #print(vertex_eccen)
    #indices = [i for i, x in enumerate(vertex_eccen) if x == 1]
    #print(nodes_eccen)


    diameter = max(vertex_eccen)
    radius = min(vertex_eccen)
    return radius, diameter



def get_all_graph_statistics(graph, nx_bool = False):

    if nx_bool == False:
        G = AccessNode_to_NetworkX(graph)
    else:
        G = graph

    max_degree_centrality, num_highest_degree_centrality = degree_centrality(graph, False)

    # connectivity_num = vertex_connectivity(graph, False)

    radius, diameter = eccentricity(graph, False)

    nodes, edges = vertices_and_edges(graph, False)

    avg_degree = average_degree(graph)

    return max_degree_centrality, num_highest_degree_centrality, radius, diameter, nodes, edges, avg_degree


    
def get_all_solution_statistics(solution_stats_arr):
    
    mean_travel_time, median_travel_time = average_travel_time(solution_stats_arr)

    avg_busses_taken = mean_busses_taken(solution_stats_arr)

    best_time, best_avg, worst_time, worst_avg = best_and_worst_avg_travel_time(solution_stats_arr)

    return mean_travel_time, median_travel_time, avg_busses_taken, best_time, best_avg, worst_time, worst_avg


def print_all_statistics(solution_stats_arr, graph_type = ""):

    mean_travel_time, median_travel_time = average_travel_time(solution_stats_arr)

    avg_busses_taken = mean_busses_taken(solution_stats_arr)

    best_time, best_avg, worst_time, worst_avg = best_and_worst_avg_travel_time(solution_stats_arr)

    graph_type_str = "FOR GRAPH " + graph_type
    print(f"\n\nSTATISTICS of the PATHS COMPUTED for {len(solution_stats_arr)} JOURNEYS {graph_type_str}:\n")

    print(f"-> Average travel time among all journeys = {sec_to_hmsms(mean_travel_time)} [{mean_travel_time:.3f} seconds]")
    print(f"-> Average number of busses for a journey = {avg_busses_taken:.1f} busses per journey\n")

    print(f"-> Best Case Analysis -")
    print(f"---> Shortest journey time = {sec_to_hmsms(best_time)} [{best_time:.3f} seconds]")
    print(f"---> Average journey time for shortest 10% of journeys = {sec_to_hmsms(best_avg)} [{best_avg:.3f} seconds]\n")

    print(f"-> Worst Case Analysis -")
    print(f"---> Longest journey time = {sec_to_hmsms(worst_time)} [{worst_time:.3f} seconds]")
    print(f"---> Average journey time for longest 10% of journeys = {sec_to_hmsms(worst_avg)} [{worst_avg:.3f} seconds]\n")

    return