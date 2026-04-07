### Imports ###
from app.data.AccessNode import AccessNode
from app.data.GetAccessNodes import get_specific_stop_data
import json
import pickle


### --- File Extraction --- ###

def get_bus_access_node_graph(city):

    ## -- Bus Stops -- ##

    # Array of bus-stop codes
    busCodes = []

    with open(f"app/data_files/Datasets/{city}/AllBusStopData.json", "r") as f:
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
    with open(f"app/data_files/Datasets/{city}/AllRoutesData.json", "r") as g:

        fileData = json.load(g)

        for file in fileData:
            routesList.append(file)

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

if __name__ == "__main__":
    import sys

    sys.setrecursionlimit(100000)
    graph = get_bus_access_node_graph("Manchester")
    pickle.dump(graph, open("app/data_files/manchester_multimodal_graph.pkl", "wb"))
    print("File succeccfully run!")
