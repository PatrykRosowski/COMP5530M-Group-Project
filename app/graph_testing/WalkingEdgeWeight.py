### --- Imports --- ###

import osmnx as ox
ox.settings.use_cache = False
import networkx as nx
import taxicab as tc

from math import sin, cos, sqrt, atan2, radians  # for Haversine distance
import time
import pickle

import folium
import requests
import polyline

AVG_WALKING_SPEED = 1.4 # metres per second



### --- Distance Retrieving Functions --- ###



## -- Boundary for osmnx.graph_from_bbox [NOT USED] -- ##


def get_coord_bounds(graph):
    north, south, east, west = (
        graph[0].Latitude,
        graph[0].Latitude,
        graph[0].Longitude,
        graph[0].Longitude,
    )

    for node in graph:

        if north < node.Latitude:
            north = node.Latitude
        if node.Latitude < south:
            south = node.Latitude

        if east < node.Longitude:
            east = node.Longitude
        if node.Longitude < west:
            west = node.Longitude

    padding = 0.01
    return north + padding, south - padding, east + padding, west - padding

## -- Haversine Distance between 2 coordinates -- ##

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

    dist = R * c * 1000 # converting from km to m
    return dist

# Inputs 2 nodes, returns Euclidian distance :

def euclidian_distance(node, target):

    # Inputs: AccessNode vertices
    # Outputs: distance between their coordinates in km

    dist = coord_to_km(
        node.get_Latitude(), node.get_Longitude(), target.get_Latitude(), target.get_Longitude()
    )
    return dist



##
## Option 1 - Use OpenStreetMap with NetworkX, and inbuilt pathfinding
##
## -- Walking Distance (via OpenStreetMaps) between 2 coordinates -- ##

def walking_route_osm(lat1, long1, lat2, long2):

    # Trying to use taxicab with OpenStreetMap:
    '''
    G = ox.graph_from_point((lat1, long1), dist=700, network_type="walk")

    start = (lat1, long1)
    end = (lat2, long2)
    try:
        route = tc.distance.shortest_path(G, start, end)
        print(route)
    except:
        raise TypeError(f"{start} and {end} nodes are causing issues with {G}")
    #tc.plot.plot_graph_route(G, route)

    return route.length, route.nodes, G  # meters
    #'''

    # Using in built functions and 'nearest_nodes' for node location:
    #'''
    G = ox.graph_from_point((lat1, long1), dist=1500, network_type="walk")

    start = ox.distance.nearest_nodes(G, long1, lat1)
    end = ox.distance.nearest_nodes(G, long2, lat2)

    try:
        path = nx.shortest_path(G, start, end, weight="length")
        dist = nx.shortest_path_length(G, start, end, weight="length")
    except nx.NetworkXNoPath:
        return None, None, G

    return dist, path, G
    #'''

# Plotting solution path :

def plot_route_osm(G, path):

    coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
    m = folium.Map(location=coords[0], zoom_start=15)

    # start point
    folium.Marker(coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    # end point
    folium.Marker(coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(m)

    # route line
    folium.PolyLine(coords, weight=5).add_to(m)
    print("Plotting map")
    m.save("app/graph_testing/route_map.html")

    return m



##
## Option 2 - Use Open_Source_Routing_Machine (built on OSM), accessing route from public server
##
## -- OSRM mapping -- ##


def walking_route_osrm(lat1, lon1, lat2, lon2):

    url = (
        f"http://router.project-osrm.org/route/v1/foot/"
        f"{lon1},{lat1};{lon2},{lat2}"
        "?overview=full&geometries=geojson"
    )

    r = requests.get(url)
    data = r.json()

    route = data["routes"][0]

    distance = route["distance"]      # meters
    duration = route["duration"]      # seconds
    path = route["geometry"]["coordinates"]

    return distance, duration, path

# Plotting solution path:

def plot_route_osrm(path):

    coords = [(lat, lon) for lon, lat in path]

    m = folium.Map(location=coords[0], zoom_start=16)

    folium.Marker(coords[0], tooltip="Start").add_to(m)
    folium.Marker(coords[-1], tooltip="End").add_to(m)

    folium.PolyLine(coords, weight=5).add_to(m)

    m.save("app/graph_testing/route_map_osrm.html")

    return m



##
## Option 3 - Use Valhalla routing from public server
##
## --  Valhalla mapping -- ##

def walking_route_valhalla(lat1, lon1, lat2, lon2):

    time.sleep(0.5)
    url = "https://valhalla1.openstreetmap.de/route"

    payload = {
        "locations": [
            {"lat": lat1, "lon": lon1},
            {"lat": lat2, "lon": lon2}
        ],
        "costing": "pedestrian",
        "directions_options": {"units": "meters"}
    }

    r = requests.post(url, json=payload)
    data = r.json()

    route = data["trip"]["legs"][0]

    distance = route["summary"]["length"] * 1000   # km → meters
    trav_time = route["summary"]["time"]               # seconds
    shape = route["shape"]                        # encoded polyline

    coords = polyline.decode(shape, precision=6)
    
    #print(f"{distance},{type(distance)} | {time},{type(time)} | {coords},{type(coords)}")
    return distance, trav_time, coords

# Plotting solution path

def plot_route_val(coords):

    m = folium.Map(location=coords[0], zoom_start=16)

    folium.Marker(coords[0], tooltip="Start").add_to(m)
    folium.Marker(coords[-1], tooltip="End").add_to(m)

    folium.PolyLine(coords, weight=5).add_to(m)
    m.save("app/graph_testing/route_map_val.html")

    return m



### --- Main --- ###


## -- Edge weight returning function -- ##

def return_walking_edge_weight(start_node, end_node):

    # Calculate straightline distance as a baseline maximum (under 500m)
    euc_dist = euclidian_distance(start_node, end_node)

    # lat1, long1 = start_node.Latitude, start_node.Longitude
    # lat2, long2 = end_node.Latitude, end_node.Longitude

    # If using Euclidian distance -
    walk_dist, time = 0, 0

    # If using OSM -
    # walk_dist, p, g = walking_route_osm(lat1, long1, lat2, long2) # path (p) and graph (g)

    # If using OSRM -
    # walk_dist, time, p = walking_route_osrm(lat1, long1, lat2, long2) # distance (d) time (t) and path (p)

    # If using Valhalla -
    # walk_dist, t, c = walking_route_valhalla(lat1, long1, lat2, long2) # time (t) and co-ords (c)

    weight = time
    if walk_dist < euc_dist: 
        # walking path is shorter than shortest (straightline) path - error
        weight = euc_dist * AVG_WALKING_SPEED


    # Uncomment to plot -

    #plot_route_osm(g, p)
    #ox.plot_graph_route(G, path) # use for osm plotting
    #plot_route_osrm(p)
    #plot_route_val(c)

    return weight



# graph = pickle.load(open("multimodal_graph.pkl", "rb"))

#start = time.time()

#lat1, lon1 = graph[8].Latitude, graph[8].Longitude
#lat2, lon2 = graph[9].Latitude, graph[9].Longitude
#distance, time_taken, route = walking_route_valhalla(lat1, lon1, 53.974988, -1.550100) #lat2, lon2)
#dist, path, G = get_walking_path_distance(lat1, lon1, lat2, lon2)

#end = time.time()
#print(f"Graph generated succesfully in time {end-start:.3f}")

#print("Distance:", distance, "meters")
#print("Time:", time_taken, "seconds")
#print("Route points:", route)
#print(graph[100].CommonName, ",", graph[101].CommonName) # verify nodes for visual debug

#print("Finished")