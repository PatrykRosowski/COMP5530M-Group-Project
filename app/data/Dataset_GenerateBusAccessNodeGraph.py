### Imports ###


from AccessNode import AccessNode

from GetAccessNodes import get_bus_stop_data
from GetAccessNodes import get_street_data
from GetAccessNodes import get_specific_stop_data

import json
import pandas as pd



### File Extraction ###


## Bus Stops ##

# List of bus-stop codes :
busCodes = []

with open("AllBusStopData.json", "r") as f:
    fileData = json.load(f)
    
    for file in fileData:
        for data in file:

            # Extracting common names from files
            stopName = data["StopPointRef"]
            if stopName not in busCodes:
                busCodes.append(stopName)

        #break # Uncomment to only view 1st file bus stops

# Extracting AccessNode data from ATCO Codes
busData = get_specific_stop_data(busCodes)


## Bus Routes ##

# List of consecuti
ve routes :
routesList = []
with open("AllRoutesData.json", "r") as g:
    fileData = json.load(g)
    
    for file in fileData:
        routesList.append(file)

        #break # Uncomment to only view 1st file bus routes



### Populating AccessNode Graph ###


# Note: vis is inputted in the map generation script        
def get_bus_access_node_graph(vis = 0):

    df_data = busData  # pandas dataframe of AccessNode data

    # Array of all AccessNode objects :
    AccessNodeGraph = [AccessNode(data_row) for index, data_row in df_data.iterrows()]
    
    # Stores {ATCO_Code: AccessNode_Object} :
    CodeToNode = { AccessNode.get_ATCOCode(ANode):ANode for ANode in AccessNodeGraph }
    # This is because AccessNode.addNearbyStop inputs AccessNode objects

    # Generating arrays of all nearby stops for each stop
    cur_file = 0 # stores unique bus route as integer
    
    for bus_route in routesList:
        cur_file += 1
        
        for journey in bus_route:

            # Consecutive bus stops (as ATCO codes)
            start = journey["Start"]
            end = journey["End"]

            # ATCO Code -> AccessNode object
            curNode = CodeToNode[start]

            # vis=1 makes multicolour edges (encodes colours to integers (cur_file))
            if vis == 1:
                AccessNode.addNearbyStop(curNode, (CodeToNode[end], cur_file))
            else:
                AccessNode.addNearbyStop(curNode,CodeToNode[end])
    

    return AccessNodeGraph



### Main ###

# get_bus_access_node_graph()
