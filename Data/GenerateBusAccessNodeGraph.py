from GetAccessNodes import get_bus_stop_data
from AccessNode import AccessNode

## The degree distance for nearby bus stops
DEGREE_DISTANCE = 0.003 ##~333m

def get_bus_access_node_graph():
    df_data = get_bus_stop_data()
    AccessNodeGraph = [AccessNode(data_row) for index, data_row in df_data.iterrows()]

    ## Returns true if the stop is nearby
    def isNearby(initialNode, targetNode):
        latitudeDifference = abs(initialNode.get_Latitude() - targetNode.get_Latitude())

        if latitudeDifference <= DEGREE_DISTANCE:
            longitudeDifference = abs(initialNode.get_Longitude() - targetNode.get_Longitude())

            if longitudeDifference <= DEGREE_DISTANCE:
                return True

        return False

    ## Generating arrays of all nearby stops for each stop
    for accessNode in AccessNodeGraph:
        nearbyStops = [node for node in AccessNodeGraph if (isNearby(accessNode, node))]
        for stop in nearbyStops:
            accessNode.addNearbyStop(stop)
    
    return AccessNodeGraph

get_bus_access_node_graph()
