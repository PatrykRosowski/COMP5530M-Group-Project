### --- Imports --- ###

from app.data.AccessNode import AccessNode
from app.data.GetAccessNodes import get_specific_stop_data
import json
import pickle

### Constants ###
SAVE_JSON = "ManchesterRoutes.json"

### --- File Extraction --- ###


def get_bus_access_node_graph(stop_json_filepath, route_json_filepath):

    ## -- Bus Stops -- ##

    # Array of bus-stop codes
    busCodes = []

    with open(stop_json_filepath, "r") as f:
        fileData = json.load(f)

        for file in fileData:
            for data in file:

                # Extracting common names from files
                stopName = data["StopPointRef"]
                if stopName not in busCodes:
                    busCodes.append(stopName)

            # break # Uncomment to only view 1st file bus stops

    # Extracting AccessNode data from ATCO Codes
    busData = get_specific_stop_data(busCodes)

    ## -- Bus Routes -- ##

    # List of consecutive routes :
    routesList = []
    with open(route_json_filepath, "r") as g:

        fileData = json.load(g)

        first_file = True
        for file in fileData:
            routesList.append(file)

            if first_file == False:
                for prev_route in routesList[:-1]:
                    if routesList[-1] == prev_route:
                        routesList.remove(prev_route)

            first_file = False
            # break # Uncomment to only view 1st file bus routes

    ## -- Populating AccessNode Graph -- ##

    df_data = busData  # pandas dataframe of AccessNode data

    # Array of all AccessNode objects :
    AccessNodeGraph = [AccessNode(data_row) for index, data_row in df_data.iterrows()]

    # Stores {ATCO_Code: AccessNode_Object} :
    CodeToNode = {AccessNode.get_ATCOCode(ANode): ANode for ANode in AccessNodeGraph}
    # This is because AccessNode.addNearbyStop inputs AccessNode objects

    # Generating arrays of all nearby stops for each stop
    bus_route_num = 0  # stores unique bus route as integer

    for bus_route in routesList:
        bus_route_num += 1

        for journey in bus_route:

            # Consecutive bus stops (as ATCO codes)
            start = journey["Start"]
            end = journey["End"]

            # ATCO Code -> AccessNode object
            curNode = CodeToNode[start]

            AccessNode.addNearbyStop(
                curNode, (CodeToNode[end], "bus", bus_route_num)
            )  # (Node, mode, route)

    return AccessNodeGraph


### Main ###
def get_bus_route_json(city, save=False, returnRoutes=True):
    """
    Generates a JSON of all pregenerated routes. Can save to a file and/or return the routes.

    Args:
        save (bool): If True, save to a file.
        returnRoutes (bool): If True, return the JSON structure.

    Returns:
        routes (Dictionary):
            [routeName : string,
            route:
                [ATCOCode : string,
                Longitude : float,
                Latitude : float]]
    """

    busStops = []
    with open(f"app/data_files/Datasets/{city}/AllBusStopData.json", "r") as f:
        fileData = json.load(f)

        # Add each bus stop as a dictionary for cross join
        for row in fileData:
            for busStop in row:
                # Assign each bus stop to JSON dictionary
                busStopDict = {}
                busStopDict["ATCOCode"] = busStop["StopPointRef"]
                busStopDict["Latitude"] = busStop["Location"][1]

                busStopDict["Longitude"] = busStop["Location"][0]

                ## Assign bus stop to route
                busStops.append(busStopDict)

    # Create a lookup dictionary.
    busStop_lookup = {stop["ATCOCode"]: stop for stop in busStops}

    routes = []
    route_signatures = set()  # Used to ensure there are no duplicates
    with open(f"app/data_files/Datasets/{city}/AllRoutesData.json", "r") as f:
        fileData = json.load(f)

        # Add each route as a dictionary into routes array
        i = 0
        for route in fileData:
            routeDict = {}
            routeDict["RouteName"] = f"Pregenerated-{i}"
            routeDict["Route"] = []
            i += 1
            for busStop in route:
                # If ATCOCode already in route, break the loop as route is repeating.
                if any(stop["ATCOCode"] == busStop["Start"] for stop in routeDict["Route"]):
                    break

                # Extract bus data from busStops array
                extractedBusStop = busStop_lookup.get(busStop["Start"])
                if extractedBusStop:
                    routeDict["Route"].append(extractedBusStop)
                else:
                    pass

            signature = tuple(stop["ATCOCode"] for stop in routeDict["Route"])

            if signature not in route_signatures:
                routes.append(routeDict)
                route_signatures.add(signature)
            else:
                continue

    # Save array of JSON routes as a JSON file
    if save:
        with open(SAVE_JSON, "w", encoding="utf-8") as f:
            json.dump(routes, f)
            print("Save Successful")

    # Return array of JSON routes.
    if returnRoutes:
        return routes


if __name__ == "__main__":
    import sys

    sys.setrecursionlimit(100000)
    graph = get_bus_access_node_graph("Manchester")
    pickle.dump(graph, open("app/data_files/manchester_multimodal_graph.pkl", "wb"))
    print("File succeccfully run!")
