from flask import Blueprint, jsonify, Response, request
import json

from app.business_logic.orchestrator import route_calculation

api_bp = Blueprint("api", __name__)


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
