from GetAccessNodes import get_bus_stop_data
from GetTestData import get_test_data
from AccessNode import AccessNode

## The degree distance for nearby bus stops
DEGREE_DISTANCE = 0.003 ##~333m increments
## The number of the minimum bus stop edges for each bus stop
MIN_NEARBY_STOPS = 4

## Returns true if the target node is nearby the target node, depending on the iteration
def addIfNearby(initialNode, targetNode, increment):
    latitudeDifference = abs(initialNode.get_Latitude() - targetNode.get_Latitude())
    
    # if (initialNode.get_ATCOCode() == 450025317):
    #     print()
    #     print(initialNode.get_Latitude())
    #     print(targetNode.get_Latitude())
    #     print(latitudeDifference)
    #     print(targetNode.get_CommonName())

    if (latitudeDifference <= DEGREE_DISTANCE * increment):
        longitudeDifference = abs(initialNode.get_Longitude() - targetNode.get_Longitude())

        # if (initialNode.get_ATCOCode() == 450025317):
        #     print()
        #     print(longitudeDifference)
        #     print(targetNode.get_CommonName())

        if (longitudeDifference <= DEGREE_DISTANCE * increment):
            
            ## Add to nearby + add itself to nearby's list
            initialNode.addNearbyStop(targetNode)
            targetNode.addNearbyStop(initialNode) ## Bi-directional

    return False

## Returns completed bus access node graph
def get_bus_access_node_graph():
    #df_data = get_bus_stop_data() ## For the full graph
    df_data = get_test_data() ## For testing
    AccessNodeGraph = [AccessNode(data_row) for index, data_row in df_data.iterrows()]

    ## Generating arrays of all nearby stops for each stop
    for accessNode in AccessNodeGraph:
        for increment in range(1, 60):

            ## Adding all nearby nodes
            for node in AccessNodeGraph:
                ## Don't want each node adding itself
                if node != accessNode:
                    addIfNearby(accessNode, node, increment)

            if len(accessNode.get_Nearby()) >= MIN_NEARBY_STOPS:
                break
    
    return AccessNodeGraph

get_bus_access_node_graph()
