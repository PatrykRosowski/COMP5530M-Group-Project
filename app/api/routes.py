from flask import Blueprint, jsonify

from app.business_logic.orchestrator import route_calculation

api_bp = Blueprint("api", __name__)


@api_bp.route("/", methods=["GET"])
def index():
    return "Server is running"


@api_bp.route("/generate-line", methods=["POST", "GET"])
def main():
    return jsonify(route_calculation())
