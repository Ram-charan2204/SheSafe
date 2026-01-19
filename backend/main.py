import cv2
import time
import threading
import subprocess
import os
from flask import Flask, Response

from modules.video_processing import VideoStream
from modules.yolo_v8_detection import YOLOv8Detector
from modules.gender_classification import GenderClassifier
from modules.risk_analysis import RiskAnalyzer
from modules.alert_sound import AlertSound
from modules.alert_logger import AlertLogger

from camera_config import CAMERAS
from stats_store import stats, stats_lock, camera_heartbeat, heartbeat_lock
from api import register_api_routes

# ================================
# CLEAN START – WIPE GENERATED FILES
# ================================
GENERATED_FILES = [
    "alert_logs.csv",
    "camera_priority.csv",
    "hotspot_priority.csv",
    "crime_hotspot_map.html"
]

for file in GENERATED_FILES:
    try:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleared: {file}")
    except Exception as e:
        print(f"⚠️ Could not delete {file}: {e}")

# ================================
# FLASK APP
# ================================
app = Flask(__name__)
register_api_routes(app)

latest_frames = {}
frame_lock = threading.Lock()

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

# ---------------- CAMERA WORKER ----------------
def camera_worker(camera):
    cam_id = camera["id"]

    try:
        video = VideoStream(camera["source"])
    except Exception as e:
        print(f"❌ {cam_id} failed to start: {e}")
        return

    detector = YOLOv8Detector("yolov8n.pt")
    gender_model = GenderClassifier()
    risk_analyzer = RiskAnalyzer()
    alert_sound = AlertSound()
    logger = AlertLogger()

    print(f"🎥 Started camera: {cam_id}")

    while True:
        frame = video.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        # 📱 Mobile portrait fix
        if cam_id.startswith("CAM-MOB"):
            h, w = frame.shape[:2]
            if w > h:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # ❤️ Heartbeat
        with heartbeat_lock:
            camera_heartbeat[cam_id] = time.time()

        detections = detector.detect(frame)
        males, females = [], []

        for x1, y1, x2, y2, conf, crop in detections:
            gender = gender_model.predict(crop)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if gender == "Male":
                males.append((cx, cy))
                color = (255, 0, 0)
            else:
                females.append((cx, cy))
                color = (0, 255, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                gender,
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

        alert = risk_analyzer.analyze(females, males)
        if alert:
            alert_sound.play(alert)
            logger.log(cam_id, alert, camera["lat"], camera["lon"])

        with frame_lock:
            latest_frames[cam_id] = frame.copy()

        with stats_lock:
            stats["persons"] = len(males) + len(females)
            stats["women"] = len(females)

# ---------------- STREAM PER CAMERA ----------------
def generate_frames(cam_id):
    while True:
        with frame_lock:
            frame = latest_frames.get(cam_id)

        if frame is None:
            time.sleep(0.05)
            continue

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

@app.route("/video/<cam_id>")
def video_cam(cam_id):
    return Response(
        generate_frames(cam_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ---------------- VIDEO WALL ----------------
@app.route("/video")
def video_wall():
    from camera_config import CAMERAS

    def status_color(status):
        return {
            "ACTIVE": "#22c55e",
            "DEGRADED": "#facc15",
            "INACTIVE": "#ef4444"
        }.get(status, "#64748b")

    html = """
    <html>
    <head>
        <title>Live Cameras</title>
        <style>
            body {
                margin: 0;
                background: #020617;
                font-family: Inter, Arial, sans-serif;
                color: #e5e7eb;
            }
            h1 {
                padding: 16px 20px;
                font-size: 20px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 360px));
                gap: 20px;
                padding: 20px;
                justify-content: center;
            }
            .card {
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 14px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 300px;
            }
            .feed {
                flex: 1;
                background: black;
            }
            .feed img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .offline {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #94a3b8;
                font-size: 14px;
            }
            .info {
                padding: 10px 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #020617;
                border-top: 1px solid #1f2937;
                font-size: 13px;
            }
            .status {
                padding: 3px 10px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 600;
            }
            .location {
                font-size: 11px;
                color: #9ca3af;
                margin-top: 4px;
            }
        </style>
    </head>
    <body>
        <h1>Live Cameras</h1>
        <div class="grid">
    """

    for cam in CAMERAS:
        status = get_camera_status(cam["id"])
        color = status_color(status)

        html += f"""
        <div class="card">
            <div class="feed">
        """

        if status == "ACTIVE":
            html += f"""<img src="/video/{cam['id']}">"""
        else:
            html += """<div class="offline">Camera Offline</div>"""

        html += f"""
            </div>
            <div class="info">
                <div>
                    <div>{cam['id']}</div>
                    <div class="location">{cam['location']}</div>
                </div>
                <div class="status" style="background:{color}">
                    {status}
                </div>
            </div>
        </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return html

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    for cam in CAMERAS:
        threading.Thread(
            target=camera_worker,
            args=(cam,),
            daemon=True
        ).start()

    app.run(host="0.0.0.0", port=5000, threaded=True)
