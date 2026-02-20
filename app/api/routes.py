from flask import Blueprint, jsonify, Response
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
    data = route_calculation()

    try:
        json_output = json.dumps(data, cls=DebugEncoder)
        return Response(json_output, mimetype='application/json')
    except TypeError as e:
        print(f"JSON Error detected: {e}")
        return jsonify({"error": str(e)})
