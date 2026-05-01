from flask import Blueprint, jsonify, Response, request
from flask_cors import cross_origin, CORS
import json

from app.business_logic.orchestrator import route_calculation
from app.evaluation.SolutionTesting import run_full_evaluation
from app.data.Dataset_GenerateBusAccessNodeGraph import get_bus_route_json
from app.data.Dataset_GenerateBusAccessNodeGraph import add_bus_route
from app.data.GetAccessNodes import get_specific_stop_data

api_bp = Blueprint("api", __name__)
CORS(api_bp)


class DebugEncoder(json.JSONEncoder):
    def default(self, obj):
        if callable(obj):
            print(f"🚨 FOUND THE CULPRIT! It is this function: {obj}")
            print(f"🚨 Function name: {getattr(obj, '__name__', 'Unknown')}")
        return super().default(obj)


@api_bp.route("/", methods=["GET"])
def index():
    return "Server is running"


@api_bp.route("/generate-line", methods=["POST", "GET"])
def main():
    data = request.get_json()

    point_a = data["point_a"]
    point_b = data["point_b"]
    print(point_a['lat'])
    print(point_a['lng'])
    print(point_b['lat'])
    print(point_b['lng'])

    route_shape = route_calculation([point_a['lat'], point_a['lng']], [point_b['lat'], point_b['lng']], 1)

    return jsonify(route_shape), 200


@api_bp.route("/routes", methods=["GET"])
def get_routes():
    try:
        with open("ManchesterRoutesWithRoads.json", "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "Routes file not found. Run scripts/generate_bus_routes.py first."}), 404


@api_bp.route("/evaluation-stats", methods=["POST"])
@cross_origin()
def get_evaluation_stats():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400
            
        print(f"DEBUG: Received evaluation request with {len(data.get('activeRoutes', []))} routes")
        active_routes_info = data.get("activeRoutes", [])
        
        # Extract names of active and visible routes
        # We use the 'name' field from frontend which maps to 'RouteName' in our backend data
        active_route_names = {r["name"] for r in active_routes_info if r.get("visible", True)}
        
        # Get original and edited routes for comparison
        all_routes = get_bus_route_json("Manchester")
        # For simplicity, we compare all routes (as "old") vs selected routes (as "new")
        # Or if we want to just evaluate the selected ones, we can use filtered for both or adjust pipeline
        filtered_routes = [r for r in all_routes if r["RouteName"] in active_route_names]
        filtered_routes_name = [r["RouteName"] for r in filtered_routes]
        
        # Add any new routes to the all_routes json.
        new_routes_name = [r for r in active_route_names if r not in filtered_routes_name]
        new_routes = [r for r in active_routes_info if r["name"] in new_routes_name]
        # Add the new routes to the all_routes file.
        for route in new_routes:
            busStopList = []
            for i in range(len(route["node_ids"])):
                atcoCode = route["node_ids"][i]
                # Get bus stop data.
                busStopData = get_specific_stop_data([atcoCode])
                busStopList.append({"ATCOCode": str(atcoCode),
                                    "Latitude": busStopData.Latitude.values[0],
                                    "Longitude": busStopData.Longitude.values[0]})
            # Add the route.
            all_routes = add_bus_route(all_routes, route["name"], busStopList)

        # If no routes are active, we might want to return empty or error
        if not filtered_routes:
             return jsonify({"error": "No active routes selected"}), 400

        print(f"Length of routes being passed: {len(all_routes)}")
        # Run the full evaluation pipeline (using a small number of pairs for speed in demo)
        eval_result = run_full_evaluation(
            num_of_HM_pairs=300, # Reduced for responsiveness
            network_json_stops="app/data_files/Datasets/Manchester/AllBusStopData.json",
            old_network_json_routes=all_routes,
            new_network_json_routes=all_routes,
        )
        
        stats = eval_result["new_graph_stats"]
        
        # Map the results to the frontend's expected keys
        # The SolutionTesting script formats these as strings with units (e.g., "1,234.567 seconds")
        # We remove the decimal point and everything after it for "seconds" strings.
        return jsonify({
            "average_time": stats.get("mean travel time", "").split('.')[0] + " seconds" if "." in stats.get("mean travel time", "") else stats.get("mean travel time"),
            "average_num_bus": stats.get("average number of busses per journey"),
            "shortest_journey_time": stats.get("shortest journey time", "").split('.')[0] + " seconds" if "." in stats.get("shortest journey time", "") else stats.get("shortest journey time"),
            "avg_journey_time_shortest_10": stats.get("average time of shortest 10% of journeys", "").split('.')[0] + " seconds" if "." in stats.get("average time of shortest 10% of journeys", "") else stats.get("average time of shortest 10% of journeys"),
            "longest_journey_time": stats.get("longest journey time", "").split('.')[0] + " seconds" if "." in stats.get("longest journey time", "") else stats.get("longest journey time"),
            "avg_journey_time_longest_10": stats.get("average time of longest 10% of journeys", "").split('.')[0] + " seconds" if "." in stats.get("average time of longest 10% of journeys", "") else stats.get("average time of longest 10% of journeys"),
        }), 200
        
    except Exception as e:
        print(f"Evaluation Error: {e}")
        return jsonify({"error": str(e)}), 500
