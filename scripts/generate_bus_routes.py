import json
import requests
import polyline
import time
from datetime import datetime, timedelta

VALHALLA_URL = "http://localhost:8002/route"
MANCHESTER_ROUTES_PATH = "../ManchesterRoutes.json"
OUTPUT_PATH = "frontend/public/data/ManchesterRoutesWithRoads.json"
ROUTE_COLORS = ['#0891B2', '#2563EB', '#7C3AED', '#DB2777', '#EA580C', '#16A34A', '#DC2626']


def call_valhalla_route(locations):
    payload = {
        "locations": locations,
        "costing": "bus",
        "directions_options": {"units": "km"}
    }
    response = requests.post(VALHALLA_URL, data=json.dumps(payload), timeout=30)
    response.raise_for_status()
    data = response.json()
    return data


def get_route_coordinates(stops):
    if len(stops) < 2:
        return [[float(s["Latitude"]), float(s["Longitude"])] for s in stops]

    all_coords = []

    for i in range(len(stops) - 1):
        locations = [
            {"lat": float(stops[i]["Latitude"]), "lon": float(stops[i]["Longitude"]), "type": "break"},
            {"lat": float(stops[i + 1]["Latitude"]), "lon": float(stops[i + 1]["Longitude"]), "type": "break"}
        ]

        try:
            data = call_valhalla_route(locations)
            decoded = polyline.decode(data["trip"]["legs"][0]["shape"], 6)
            segment_coords = [[lat, lon] for lat, lon in decoded]

            if i > 0 and all_coords:
                all_coords.extend(segment_coords[1:])
            else:
                all_coords.extend(segment_coords)

        except Exception as e:
            print(f"    Warning: Valhalla failed for segment {i}, using straight line fallback")
            fallback = [
                [float(stops[i]["Latitude"]), float(stops[i]["Longitude"])],
                [float(stops[i + 1]["Latitude"]), float(stops[i + 1]["Longitude"])]
            ]
            if i > 0 and len(all_coords) > 0:
                all_coords.extend(fallback[1:])
            else:
                all_coords.extend(fallback)

    return all_coords


def main():
    print("Loading ManchesterRoutes.json...")
    with open(MANCHESTER_ROUTES_PATH, "r") as f:
        routes_data = json.load(f)

    total_routes = len(routes_data)
    print(f"Loaded {total_routes} routes\n")

    start_time = time.time()
    processed_routes = []

    for idx, route in enumerate(routes_data):
        route_name = route.get("RouteName", f"Route-{idx}")
        stops = route.get("Route", [])

        elapsed = time.time() - start_time
        avg_time_per_route = elapsed / max(idx, 1)
        remaining = total_routes - idx - 1
        eta_seconds = avg_time_per_route * remaining
        eta = str(timedelta(seconds=int(eta_seconds))) if remaining > 0 else "0s"

        progress = ((idx + 1) / total_routes) * 100
        print(f"[{idx + 1}/{total_routes}] ({progress:.1f}%) ETA: {eta} - Processing {route_name} ({len(stops)} stops)")

        coordinates = get_route_coordinates(stops)

        processed_routes.append({
            "id": f"L{idx + 1}",
            "name": route_name,
            "visible": True,
            "coordinates": coordinates
        })

    print(f"\nWriting output to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(processed_routes, f, indent=2)

    total_coords = sum(len(r["coordinates"]) for r in processed_routes)
    print(f"Done! Wrote {len(processed_routes)} routes with {total_coords} total coordinate points")


if __name__ == "__main__":
    main()