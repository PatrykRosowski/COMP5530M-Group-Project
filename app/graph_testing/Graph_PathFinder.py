#
# Script for getting weighted shortest path
#


### --- Imports --- ###


from AccessNode import AccessNode
from WalkingEdgeWeight import euclidian_distance
from WalkingEdgeWeight import return_walking_edge_weight
# from graph_extraction import get_weight_bus

from math import sin, cos, sqrt, atan2, radians  # for Haversine distance
import pickle
import random
import gmplot
import time


### --- Functions --- ###


# Path-Cost function :


def generate_random_endstops(AccessNode_graph):

    nodes_list = random.sample(AccessNode_graph, 2)
    return nodes_list


def path_cost(edge_weight, nodeData, prev_mode):

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
        "walk": 10,
        "change": 3,  # waiting-time penalty for a new bus
    }
    Bus_Waiting_Cost = 20  # waiting-time for a bus

    ## -- Combinations of changing transport modes -- ##

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
        return float("inf")

    ## -- End of Function -- ##


def get_weight(start_node, end_node, mode):

    if mode == "walk":
        weight = return_walking_edge_weight(start_node, end_node)
        # weight = 1
    if mode == "bus":
        # weight = get_weight_bus(start_node, end_node)
        weight = 200

    return weight



### --- Shortest-Path Simulation (A-star Search) --- ###

# Note: Big help from
# https://www.datacamp.com/tutorial/a-star-algorithm


class AStarNode:
    def __init__(self):
        self.node = None        # AccessNode in reference
        self.g = float("inf")   # Actual cost from start
        self.h = 0              # Estimated cost (from heuristic)
        self.f = float("inf")   # Total estimated cost
        self.parent = None      # For back-tracking
        self.parent.edge = None # Storing edge when back-tracking
        self.mode = None        # For tracking the mode of transport


def Shortest_Path_Sim(graph, start, dest, edge_weight_dict = {}):

    ## -- Implements A* search -- ##

    # Heuristic = Euclidian distance:
    h = {}
    for node in graph:

        h[node] = euclidian_distance(node, dest)
        node.h = h[node]  # estimated cost is pre-defined

        # Initialising other values for A* search for all nodes
        node.g = float("inf")
        node.f = float("inf")
        node.parent = None
        node.mode = None  # stored as (mode, bus_route) or (mode,)
        node.edge = None

    ## -- Start of A* -- ##

    queue = [start]  # Priority Queue
    visited_nodes = []  # Stores nodes with guaranteed shortest path found
    # For storing computed weights:
    # edge_weight_dict = {} # Format = { (startNode, endNode, transportMode) : weight_value }

    # Initialising starting node
    start.g = 0
    start.f = start.g + start.h
    start.parent = None


    count = [0, 0]

    while queue != []:

        # Sorting priority queue and selecting lowest cost node
        queue.sort(key=lambda x: x.f)  # sorting by total estimated cost
        curNode = queue[0]

        count[0] += 1

        ## -- Checking if destination has been reached -- ##

        if curNode == dest:

            # Backtracking from destination to obtain path from start
            path_array = [(dest, "Journey Complete!")]
            backtracking_node = dest

            while backtracking_node is not None:
                # (parent_node, edge_weight_travelled, mode_of_travel)
                path_array.insert(0, (backtracking_node.parent, backtracking_node.edge, backtracking_node.mode))
                backtracking_node = backtracking_node.parent

            return path_array[1:], dest.f

        # Now visited, optimal cost from start node to current node is guaranteed
        # Moving current node from queue to visited_nodes
        visited_nodes.append(curNode)
        queue.remove(curNode)

        ## -- Checking all neighbouring nodes -- ##

        nodeOptions = curNode.Nearby
        for nodeData in nodeOptions:

            count[1] += 1
            new_node = nodeData[0]

            if new_node in visited_nodes:
                continue  # skip nodes already evaluated

            # Since node is unevaluated, calculate the edge weight
            if (curNode, new_node, nodeData[1]) in edge_weight_dict.keys():
                edge_weight = edge_weight_dict[(curNode, new_node, nodeData[1])]
            else:
                edge_weight = get_weight(curNode, new_node, nodeData[1])
                edge_weight_dict[(curNode, new_node, nodeData[1])] = edge_weight

            # Calculating tentative g score: Cost till previous node + (edge-weight x cost_function)
            proposed_g = curNode.g + path_cost(edge_weight, nodeData, curNode.mode)

            if new_node not in queue:
                queue.append(new_node)  # adding previously unseen nodes to the priority queue

            # Node is already in priority queue, verify whether proposed value is optimal (lower)
            elif proposed_g >= new_node.g:
                continue  # do not update less-efficient paths

            # Current node is new or has best/better path from the start node.

            ## -- Updating cost values -- ##

            new_node.g = curNode.g + path_cost(edge_weight, nodeData, curNode.mode)
            new_node.f = new_node.g + new_node.h
            new_node.parent = curNode
            new_node.mode = nodeData[1:]  # also update mode used along this edge (including bus_route)
            new_node.edge = edge_weight

            print(".",end='')

        print(f"{count},,",end='')

    return Exception("Failure, could not compute path from start to end."), float("inf")


    ## -- End of Function -- ##



### --- Main --- ###

# graph = get_multimodal_graph()
graph = pickle.load(open("multimodal_graph.pkl", "rb"))

# Input ATCO code or Common Name of bus stop :

START_NODE = '3200YNA96823'
END_NODE = '450051367'

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


# Using A* and obtaining optimal path + cost

start_time = time.time()

# Using randomly chosen points :
nodes = generate_random_endstops(graph)
start_ind, end_ind = graph.index(nodes[0]), graph.index(nodes[1])

# Running A* and obtaining solution :
solution_path, total_cost = Shortest_Path_Sim(graph, graph[start_ind], graph[end_ind])

end_time = time.time()
print(f"\n\nGraph generated succesfully in time {end_time-start_time:.3f}\n")

## -- Print statements (for debugging) -- ##

print(f"Journey from node {graph[start_ind].get_ATCOCode()} ({graph[start_ind].CommonName}) ",end='')
print(f"to node {graph[end_ind].get_ATCOCode()} ({graph[end_ind].CommonName})")
print(f"Total Cost of journey = {total_cost}")
count = 0
for node in solution_path:
    count += 1
    print(f"{count}. {node[0].get_ATCOCode()}: mode = {node[1:]}")



## -- Plotting the solution -- ##


def plot_solution(sol_array, name):

    # sol_array[i] = (parent_node, edge_weight_travelled, mode_of_travel)
    colours = ["blue", "orange", "green", "red", "purple"]
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


# Plotting solution in gmplot
# plot_solution(solution_path, f"app/graph_testing/solutions/{start_ind}-to-{end_ind}_sol.html")
