#
# Script for getting weighted shortest path
#


### --- Imports --- ###


from app.data.AccessNode import AccessNode
from app.graph_testing.WalkingEdgeWeight import euclidian_distance
from app.graph_testing.WalkingEdgeWeight import return_walking_edge_weight
from app.graph_testing.BusEdgeWeight import get_weight_bus
from app.data.Dataset_GenerateBusAccessNodeGraph import get_bus_access_node_graph
from app.data.Dataset_GenerateWalkingPaths import add_walking_paths

from math import sin, cos, sqrt, atan2, radians  # for Haversine distance
import pickle
import random
import gmplot
import time
import networkx as nx
import heapq
import itertools
from functools import lru_cache

# Constant that leads to bus graph graph ml file
BUS_GRAPH = "bus_graph.graphml"
BUS_NETWORK = nx.read_graphml(BUS_GRAPH)

# Cache
walking_weight_cache = {}
bus_weight_cache = {}

### --- Functions --- ###


# Path-Cost function :


def generate_random_endstops(AccessNode_graph):

    nodes_list = random.sample(AccessNode_graph, 2)
    return nodes_list


@lru_cache(maxsize=None)
def cached_path_cost(edge_weight, cur_mode, cur_route, prev_mode, prev_route, node_mode_num):
    # Reconstruct nodeData (had to be deconstructed as it's not hashable)
    nodeData = (None, cur_mode, cur_route)

    if prev_mode is None:
        return path_cost(edge_weight, nodeData, None, node_mode_num)
    else:
        prev_mode_tuple = (prev_mode, prev_route)
        return path_cost(edge_weight, nodeData, prev_mode_tuple, node_mode_num)


def path_cost(edge_weight, nodeData, prev_mode, node_mode_num):

    ## -- Verifying parameters -- ##

    # Note: prev_mode = (mode, route) or (mode, None)
    valid_mode = ["bus", "tram", "walk", None]
    cur_mode = nodeData[1:]
    if cur_mode[0] not in valid_mode:
        raise ValueError(
            f"'{cur_mode}' is an incorrect mode of transport. (use 'bus', 'tram' or 'walk')"
        )

    ## -- Cost Function -- ##

    PunishmentMultiplyer = {
        "bus": 1,
        "tram": 1,
        "walk": 2,
        "change": 50,  # waiting-time penalty for a new bus
    }
    Bus_Waiting_Cost = 30  # waiting-time for a bus

    Mode_Change_Punisher = 150

    ## -- Combinations of changing transport modes -- ##

    edge_weight = edge_weight * (
        Mode_Change_Punisher**node_mode_num
    )  # Exponential cost for new modes

    if prev_mode == None:  # First choice from starting node

        if cur_mode[0] == "bus":  # Takes a bus from starting node

            # New value = Waiting for bus cost + travelling to next stop cost
            return Bus_Waiting_Cost + edge_weight * PunishmentMultiplyer["bus"]

        else:  # Walks to a nearby bus stop first

            # Passenger directly walks to a different stop, no waiting time incurred
            return edge_weight * PunishmentMultiplyer["walk"]

    if prev_mode[0] == "bus" and cur_mode[0] == "bus":

        if prev_mode[1] == cur_mode[1]:

            # Passenger continues on same bus
            return edge_weight * PunishmentMultiplyer["bus"]

        else:

            # Indicates passenger is changing busses from same stop
            # New value = Change of busses cost + travelling to next stop cost
            return (
                Bus_Waiting_Cost * PunishmentMultiplyer["change"]
                + edge_weight * PunishmentMultiplyer["bus"]
            )

    if prev_mode[0] == "bus" and cur_mode[0] == "walk":

        # Passenger has gotten down from a bus, and is walking to a new stop (no waiting time)
        return edge_weight * PunishmentMultiplyer["walk"]

    if prev_mode[0] == "walk" and cur_mode[0] == "bus":

        # Indicates passenger previously walked to current stop (cost already
        # accounted for) and must wait for and take a new bus
        # New value = Waiting for bus cost + travelling to next stop cost
        return (
            Bus_Waiting_Cost * PunishmentMultiplyer["change"]
            + edge_weight * PunishmentMultiplyer["bus"]
        )

    if prev_mode[0] == "walk" and cur_mode[0] == "walk":

        # Restrict passengers from consecutively walking (over 500m)
        # return float("inf")
        return edge_weight * PunishmentMultiplyer["walk"]

    ## -- End of Function -- ##


def get_weight(G, start_node, end_node, mode):

    if mode == "walk":
        key = start_node, end_node

        if key not in walking_weight_cache:
            weight = return_walking_edge_weight(start_node, end_node)
            walking_weight_cache[key] = weight
            walking_weight_cache[(end_node, start_node)] = weight
        else:
            weight = walking_weight_cache[key]

    elif mode == "bus":
        key = (start_node, end_node)

        if key not in bus_weight_cache:
            weight = get_weight_bus(G, start_node, end_node)
            bus_weight_cache[key] = weight
        else:
            weight = bus_weight_cache[key]

    else:
        raise ValueError(f"Unknown mode: '{mode}', {type(mode)}")

    return weight


### --- Shortest-Path Simulation (A-star Search) --- ###

# Note: Big help from
# https://www.datacamp.com/tutorial/a-star-algorithm


class AStarNode:
    def __init__(self):
        self.node = None  # AccessNode in reference
        self.g = float("inf")  # Actual cost from start
        self.h = 0  # Estimated cost (from heuristic)
        self.f = float("inf")  # Total estimated cost
        self.parent = None  # For back-tracking
        self.edge_weight = None  # Storing edge when back-tracking
        self.mode = None  # For tracking the mode of transport
        self.mode_num = 0  # For tracking how many busses/walks have been taken


def Shortest_Path_Simulation(graph, start, dest, edge_weight_dict={}, show_progress=False):

    # Note: edge_weight_dict format = { (startNode, endNode, transportMode) : weight_value }

    G = BUS_NETWORK
    dest.lat = dest.get_Latitude()
    dest.lon = dest.get_Longitude()

    ## -- Implements A* search -- ##

    # Heuristic = Euclidian distance:
    g = {}
    f = {}
    h = {}
    parent = {}
    mode_used = {}
    edge_used = {}
    precomputed_nearby = {}
    edge_weight_node = {}
    mode_num = {}
    for node in graph:

        node.lat = node.get_Latitude()
        node.lon = node.get_Longitude()
        dist = euclidian_distance(node, dest)
        h[node] = dist  # estimated cost is pre-defined

        # Initialising other values for A* search for all nodes
        g[node] = float("inf")
        f[node] = float("inf")
        parent[node] = None
        mode_used[node] = None  # stored as (mode, bus_route) or (mode,)
        edge_used[node] = None

        edge_weight_node[node] = None
        mode_num[node] = 0

        # Precompute nearby lists
        precomputed_nearby[node] = node.Nearby

    ## -- Start of A* -- ##

    queue = []  # Priority Queue
    counter = itertools.count()
    visited_nodes = set()  # Stores nodes with guaranteed shortest path found

    # For storing computed weights:
    # edge_weight_dict = {} # Format = { (startNode, endNode, transportMode) : weight_value }

    # Initialising starting node
    g[start] = 0
    f[start] = g[start] + h[start]
    parent[start] = None
    mode_num[start] = 0
    edge_weight_node[start] = 0

    heapq.heappush(queue, (f[start], next(counter), start))

    count = [0, 0]

    while queue != []:

        # Sorting priority queue and selecting lowest cost node
        _, _, curNode = heapq.heappop(queue)

        if curNode in visited_nodes:
            continue

        count[0] += 1

        ## -- Checking if destination has been reached -- ##

        if curNode == dest:

            # print(f"\nnumber of modes taken = {curNode.mode_num}")
            # Backtracking from destination to obtain path from start
            path_array = [(dest, "Journey Complete!")]
            backtracking_node = dest
            total_time = 0

            while backtracking_node is not None:
                # (parent_node, edge_weight_travelled, mode_of_travel)
                total_time += edge_weight_node[backtracking_node]
                path_array.insert(
                    0,
                    (
                        parent[backtracking_node],
                        edge_used[backtracking_node],
                        mode_used[backtracking_node],
                    ),
                )
                backtracking_node = parent[backtracking_node]

            return path_array[1:], total_time, f[dest]

        # Now visited, optimal cost from start node to current node is guaranteed
        # Moving current node from queue to visited_nodes
        visited_nodes.add(curNode)

        ## -- Checking all neighbouring nodes -- ##

        nodeOptions = precomputed_nearby[curNode]
        for nodeData in nodeOptions:

            count[1] += 1
            newNode = nodeData[0]

            if newNode in visited_nodes:
                continue  # skip nodes already evaluated

            mode = nodeData[1]
            key = (curNode, newNode, mode)

            # Since node is unevaluated, calculate the edge weight
            if key in edge_weight_dict:
                edge_weight = edge_weight_dict[key]
            else:
                edge_weight = get_weight(G, curNode, newNode, mode)
                edge_weight_dict[key] = edge_weight
                if mode == "walk":
                    edge_weight_dict[(newNode, curNode, mode)] = edge_weight

            # Calculating tentative g score: Cost till previous node + (edge-weight x cost_function)
            if mode_used[curNode] is None:
                proposed_g = g[curNode] + cached_path_cost(
                    edge_weight,
                    nodeData[1],
                    nodeData[2],
                    None,
                    None,
                    mode_num[curNode],  # mode  # route
                )
            else:
                prev_mode, prev_route = mode_used[curNode]
                proposed_g = g[curNode] + cached_path_cost(
                    edge_weight,
                    nodeData[1],
                    nodeData[2],
                    prev_mode,
                    prev_route,
                    mode_num[curNode],  # mode  # route
                )

            heapq.heappush(queue, (f[newNode], next(counter), newNode))

            # Node is already in priority queue, verify whether proposed value is optimal (lower)
            if proposed_g >= g[newNode]:
                continue  # do not update less-efficient paths

            # Current node is new or has best/better path from the start node.

            ## -- Updating cost values -- ##

            g[newNode] = proposed_g  # curNode.g + path_cost(edge_weight, nodeData, curNode.mode)
            # print()
            f[newNode] = g[newNode] + h[newNode]
            parent[newNode] = curNode
            mode_used[newNode] = nodeData[
                1:
            ]  # also update mode used along this edge (including bus_route)
            edge_weight_node[newNode] = edge_weight

            if mode_used[curNode] == None:
                mode_num[newNode] = 1
            elif mode_used[curNode] == "walk":
                mode_num[newNode] = mode_num[curNode] + 1
            elif mode_used[curNode] == "bus" and edge_used[curNode] != edge_used[newNode]:
                mode_num[newNode] = mode_num[curNode] + 1
            else:
                mode_num[newNode] = mode_num[curNode]

    return (
        Exception("Failure, could not compute path from start to end."),
        float("inf"),
        float("inf"),
    )

    ## -- End of Function -- ##


### --- Main --- ###

if __name__ == "__main__":

    graph = get_bus_access_node_graph("Manchester")
    graph = add_walking_paths(graph)
    # graph = pickle.load(open("app/data_files/harrogate_multimodal_graph.pkl", "rb"))

    # Input ATCO code or Common Name of bus stop :

    #'''
    START_NODE = "1800NE07821"
    END_NODE = "1800NF10241"

    start_ind = None
    end_ind = None

    for node in graph:

        if node.ATCOCode == START_NODE or node.CommonName == START_NODE:
            start_ind = graph.index(node)

        if node.ATCOCode == END_NODE or node.CommonName == END_NODE:
            end_ind = graph.index(node)

    # OR input index of nodes -
    # start_ind = 213
    # end_ind = 579

    print(start_ind, end_ind)
    #'''

    # Using A* and obtaining optimal path + cost

    start_time = time.time()

    # Using randomly chosen points :
    nodes = generate_random_endstops(graph)
    start_ind, end_ind = graph.index(nodes[0]), graph.index(nodes[1])

    # Running A* and obtaining solution :
    solution_path, total_weights, total_cost = Shortest_Path_Simulation(
        graph, graph[start_ind], graph[end_ind], show_progress=False
    )

    end_time = time.time()
    print(f"\n\nGraph generated succesfully in time {end_time-start_time:.3f}\n")

    ## -- Print statements (for debugging) -- ##

    print(
        f"Journey from node {graph[start_ind].get_ATCOCode()} ({graph[start_ind].CommonName}) ",
        end="",
    )
    print(f"to node {graph[end_ind].get_ATCOCode()} ({graph[end_ind].CommonName})")
    print(f"Total Cost of journey = {total_cost}\n")
    print(f"Total weight = {total_weights}")
    count = 0
    for node in solution_path:
        count += 1
        print(f"{count}. {node[0].get_ATCOCode()}: mode = {node[1:]}")
    print()

    ## -- Plotting the solution -- ##

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

            if (
                i > 0
                and sol_array[i - 1][2][0] == "bus"
                and sol_array[i - 1][2][1] not in used_routes
            ):
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

    # Plotting solution in gmplot
    plot_solution(solution_path, f"app/graph_testing/solutions/{start_ind}-to-{end_ind}_sol.html")
