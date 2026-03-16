#
# Script for getting weighted shortest path
#


### --- Imports --- ###


from AccessNode import AccessNode

from math import sin, cos, sqrt, atan2, radians  # for Haversine distance
import pickle
import random
import gmplot


### --- Functions --- ###


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

    dist = R * c
    return dist


# Inputs 2 nodes, returns Euclidian distance :


def inter_node_distance(node, target):

    # Inputs: AccessNode vertices
    # Outputs: distance between their coordinates in km

    dist = coord_to_km(
        node.get_Latitude(), node.get_Longitude(), target.get_Latitude(), target.get_Longitude()
    )
    return dist


# Path-Cost function :


def path_cost(edge_weight, node, prev_mode):

    ## -- Verifying parameters -- ##

    # Note: prev_mode = (mode, route) or (mode, None)
    valid_mode = ["bus", "tram", "walk", None]
    cur_mode = node[1:]
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


def generate_random_endstops(AccessNode_graph):

    nodes_list = random.sample(AccessNode_graph, 2)
    return nodes_list


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
        self.mode = None  # For tracking the mode of transport


def Shortest_Path_Sim(graph, start, dest):

    ## -- Implements A* search -- ##

    # Heuristic = Euclidian distance:
    h = {}
    for node in graph:

        h[node] = inter_node_distance(node, dest)
        node.h = h[node]  # estimated cost is pre-defined

        # Initialising other values for A* search for all nodes
        node.g = float("inf")
        node.f = float("inf")
        node.parent = None
        node.mode = None  # stored as (mode, bus_route) or (mode,)

    ## -- Start of A* -- ##

    queue = [start]  # Priority Queue
    visited_nodes = []  # Stores nodes with guaranteed shortest path found

    # Initialising starting node
    start.g = 0
    start.f = start.g + start.h
    start.parent = None

    while queue != []:

        # Sorting priority queue and selecting lowest cost node
        queue.sort(key=lambda x: x.f)  # sorting by total estimated cost
        curNode = queue[0]

        ## -- Checking if destination has been reached -- ##

        if curNode == dest:

            # Backtracking from destination to obtain path from start
            path_array = [(dest, "Journey Complete!")]
            backtracking_node = dest

            while backtracking_node is not None:
                path_array.insert(0, (backtracking_node.parent, backtracking_node.mode))
                backtracking_node = backtracking_node.parent

            return path_array[1:], dest.f

        # Now visited, optimal cost from start node to current node is guaranteed
        # Moving current node from queue to visited_nodes
        visited_nodes.append(curNode)
        queue.remove(curNode)

        ## -- Checking all neighbouring nodes -- ##

        nodeOptions = curNode.Nearby
        for node in nodeOptions:

            if node[0] in visited_nodes:
                continue  # skip nodes already evaluated

            # Calculating tentative g score: Cost till previous node + (edge-weight x cost_function)
            proposed_g = curNode.g + path_cost(1, node, curNode.mode)

            if node[0] not in queue:
                queue.append(node[0])  # adding previously unseen nodes to the priority queue

            # Node is already in priority queue, verify whether proposed value is optimal (lower)
            elif proposed_g >= node[0].g:
                continue  # do not update less-efficient paths

            # Current node is new or has best/better path from the start node.

            ## -- Updating cost values -- ##

            node[0].g = curNode.g + path_cost(1, node, curNode.mode)
            node[0].f = node[0].g + node[0].h
            node[0].parent = curNode
            node[0].mode = node[1:]  # also update mode used along this edge (including bus_route)

    return Exception("Failure, could not compute path from start to end."), float("inf")

    ## -- End of Function -- ##


### --- Main --- ###

# graph = get_multimodal_graph()
graph = pickle.load(open("multimodal_graph.pkl", "rb"))

# Input ATCO code or Common Name of bus stop :

START_NODE = "Granby Corner"
END_NODE = "Army Foundation College"

start_ind = None
end_ind = None

for node in graph:

    if node.ATCOCode == START_NODE or node.CommonName == START_NODE:
        start_ind = graph.index(node)

    if node.ATCOCode == END_NODE or node.CommonName == END_NODE:
        end_ind = graph.index(node)

# OR input index of nodes -
start_ind = 213
end_ind = 579


# Using A* and obtaining optimal path + cost

# Using randomly chosen points :
# nodes = generate_random_endstops(graph)
# start_ind, end_ind = graph.index(nodes[0]), graph.index(nodes[1])
# solution_path, total_cost = Shortest_Path_Sim(graph, nodes[0], nodes[1])

# Using custom chosen points :
solution_path, total_cost = Shortest_Path_Sim(graph, graph[start_ind], graph[end_ind])


## -- Print statements (for debugging) -- ##

# print(f"Total Cost = {total_cost}")
# print(f"Start node = {graph[0].get_ATCOCode()}")
# print(f"Destination node = {graph[-1].get_ATCOCode()}")
# count = 0
# for node in solution_path:
#     count += 1
#     print(count, node[0].get_ATCOCode(), node[1:])


## -- Plotting the solution -- ##


def plot_solution(sol_array, name):

    colours = ["blue", "orange", "green", "red", "purple"]
    used_routes = []
    gmap = gmplot.GoogleMapPlotter(54.05, -1.42, 12)

    first = True  # Flag variable keeping track of whether on starting node
    i = 0  # Keep track of position in solution array

    for node in sol_array:
        lat = node[0].get_Latitude()
        lon = node[0].get_Longitude()

        if i > 0 and sol_array[i - 1][1][0] == "bus" and sol_array[i - 1][1][1] not in used_routes:
            used_routes.append(sol_array[i - 1][1][1])

        # Plot node as marker
        gmap.marker(lat, lon, title=node[0].get_CommonName())

        if first == False:
            lat2 = sol_array[i - 1][0].get_Latitude()
            lon2 = sol_array[i - 1][0].get_Longitude()

            if sol_array[i - 1][1][0] == "bus":
                # Colourful edge for bus
                gmap.plot(
                    [lat, lat2],
                    [lon, lon2],
                    edge_width=6,
                    color=colours[used_routes.index(sol_array[i - 1][1][1])],
                )
            else:
                # Black edge for walking path
                gmap.plot([lat, lat2], [lon, lon2], edge_width=3)

        first = False  # After running once, start node computed. Turn flag variable off.
        i += 1  # Update index of current node

    # Output to HTML file
    gmap.draw(name)


# Plotting solution in gmplot
plot_solution(solution_path, f"solutions/{start_ind}-to-{end_ind}_sol.html")
