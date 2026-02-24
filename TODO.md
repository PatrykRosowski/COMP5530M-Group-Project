# TODO

## Functions implementations
- [x] main
- [x] select_random_nodes
- [x] compute_mesp
- [x] shortest_distance_to_path
- [x] generate_network_configuration
- [x] generate_od_pairs
- [/] get_nodes_covered_by_config
- [x] edge_cost_fn
- [/] estimate_cost_fn (no need since graph edge is converted to travel time)

## Problems
- [] no path found in compute_mesp for some streets
    - since we've not implemented any walking graph, some origin-destination pairs might not be connected
    - some 'street section' of stops is disconnected thus no path between origin and destination pair

- [] priority fix - some path does not go through the intended bus stops
    - could be that during the bus graph generation that it disregard the directions of the bus stops
    - let say Stop A and B are on the opposite road but the graph       generation still take it as a neighbor since it within the threshold radius? (could be fixed by swapping the distance function with the routing engine taking care of the distance - Stop A and B are technically not near to each other since bus needs to take a longer route to travel to it). 
    - the assumption of distance using coordinates might cause the routing engine to have problems