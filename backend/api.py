import csv
import time
from flask import jsonify, send_file, Response
from camera_config import CAMERAS
from stats_store import stats, stats_lock, camera_heartbeat, heartbeat_lock
from init_risk_state import camera_risk, high_risk_zones
import os
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
                        "severity": row["severity"]   # ✅ TRUST BACKEND
                    })
        except FileNotFoundError:
            pass

        alerts.reverse()
        return jsonify(alerts[:50])


    # ===== HOTSPOT MAP =====
    @app.route("/api/hotspots/map")
    def hotspot_map():
        map_path = "crime_hotspot_map.html"

        if not os.path.exists(map_path):
            return Response(
                """
                <html>
                <head>
                    <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        background: #0f172a;
                        color: #e5e7eb;
                    }
                    .box {
                        text-align: center;
                        padding: 24px;
                        border: 1px dashed #64748b;
                        border-radius: 12px;
                    }
                    </style>
                </head>
                <body>
                    <div class="box">
                    <h2>📍 Hotspot Map Not Ready</h2>
                    <p>Waiting for alerts & analytics…</p>
                    </div>
                </body>
                </html>
                """,
                status=200,
                mimetype="text/html"
            )

        return send_file(map_path)

    # ===== HOTSPOT LIST (🔥 MISSING FIX) =====
    @app.route("/api/hotspots")
    def hotspots():
        hotspots = []
        try:
            with open("hotspot_priority.csv", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    hotspots.append({
                        "lat": float(row["lat_bucket"]),
                        "lon": float(row["lon_bucket"]),
                        "risk": float(row["total_risk"]),
                        "alerts": int(row["alert_count"])
                    })
        except FileNotFoundError:
            pass

        return jsonify(hotspots)

