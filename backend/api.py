import csv
import time
from flask import jsonify, send_file
from camera_config import CAMERAS
from stats_store import stats, stats_lock, camera_heartbeat, heartbeat_lock

# ---------------- CAMERA STATUS ----------------
def get_camera_status(cam_id):
    with heartbeat_lock:
        last = camera_heartbeat.get(cam_id)

    if last is None:
        return "INACTIVE"

    delta = time.time() - last
    if delta < 2:
        return "ACTIVE"
    elif delta < 5:
        return "DEGRADED"
    else:
        return "INACTIVE"

# ---------------- ROUTES ----------------
def register_api_routes(app):

    # ===== DASHBOARD STATS =====
    @app.route("/api/stats")
    def get_stats():
        with stats_lock:
            return jsonify(stats)

    # ===== CAMERAS =====
    @app.route("/api/cameras")
    def get_cameras():
        return jsonify([
            {
                "id": cam["id"],
                "location": cam["location"],
                "lat": cam["lat"],
                "lon": cam["lon"],
                "status": get_camera_status(cam["id"]),
                "risk": 0
            }
            for cam in CAMERAS
        ])

    # ===== ALERTS =====
    @app.route("/api/alerts")
    def get_alerts():
        alerts = []
        try:
            with open("alert_logs.csv", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    alerts.append({
                        "camera": row["camera_id"],
                        "message": row["alert_type"],
                        "time": row["timestamp"],
                        "severity": (
                            "HIGH" if "surrounded" in row["alert_type"].lower()
                            else "MEDIUM" if "isolated" in row["alert_type"].lower()
                            else "LOW"
                        )
                    })
        except FileNotFoundError:
            pass

        alerts.reverse()
        return jsonify(alerts[:50])

    # ===== HOTSPOT MAP =====
    @app.route("/api/hotspots/map")
    def hotspot_map():
        return send_file("crime_hotspot_map.html")

    # ===== HOTSPOT LIST (🔥 MISSING FIX) =====
    @app.route("/api/hotspots")
    def hotspot_list():
        hotspots = []
        try:
            with open("hotspot_priority.csv", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    hotspots.append({
                        "lat": row["lat_bucket"],
                        "lon": row["lon_bucket"],
                        "risk": float(row["total_risk"]),
                        "alerts": int(row["alert_count"])
                    })
        except FileNotFoundError:
            pass

        hotspots.sort(key=lambda x: x["risk"], reverse=True)
        return jsonify(hotspots)
