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