import cv2
import time
import threading
import os
import subprocess
from flask import Flask, Response

from modules.video_processing import VideoStream
from modules.yolo_v8_detection import YOLOv8Detector
from modules.gender_classification import GenderClassifier
from modules.alert_sound import AlertSound
from modules.alert_logger import AlertLogger
from modules.alert_router import AlertRouter
from modules.hand_gesture import HandGestureDetector
from modules.risk_analysis import RiskAnalyzer
from modules.sound_detection import SoundAnomalyDetector

from camera_config import CAMERAS
from stats_store import stats, stats_lock, camera_heartbeat, heartbeat_lock
from api import register_api_routes
from generate_initial_hotspot_map import generate_initial_hotspot_map
from init_risk_state import init_risk_state

# ================= CLEAN START =================
for f in [
    "alert_logs.csv",
    "camera_priority.csv",
    "hotspot_priority.csv",
    "crime_hotspot_map.html"
]:
    if os.path.exists(f):
        os.remove(f)

# ================= FLASK =================
app = Flask(__name__)
register_api_routes(app)

latest_frames = {}
frame_lock = threading.Lock()

# ================= ASYNC HELPERS =================
def async_alert(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()

# ================= AUDIO PRIORITY CONTROLLER =================
audio_lock = threading.Lock()
current_audio_level = None

ALERT_PRIORITY = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

def reset_audio_level():
    global current_audio_level
    current_audio_level = None

def play_priority_sound(sound_player, sound_key, level):
    global current_audio_level

    with audio_lock:
        if (
            current_audio_level is None or
            ALERT_PRIORITY[level] > ALERT_PRIORITY.get(current_audio_level, 0)
        ):
            current_audio_level = level
            sound_player.play(sound_key)
            threading.Timer(3, reset_audio_level).start()

# ================= CAMERA WORKER =================
def camera_worker(camera):
    cam_id = camera["id"]

    try:
        video = VideoStream(camera["source"])
    except Exception as e:
        print(f"❌ {cam_id} failed:", e)
        return

    detector = YOLOv8Detector("yolov8n.pt")
    gender_model = GenderClassifier()
    gesture = HandGestureDetector()
    risk = RiskAnalyzer()
    sound = SoundAnomalyDetector()

    alert_sound = AlertSound()
    logger = AlertLogger()
    mailer = AlertRouter()

    sound.start()
    last_gesture = None

    print(f"🎥 Camera started: {cam_id}")

    while True:
        frame = video.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        with heartbeat_lock:
            camera_heartbeat[cam_id] = time.time()

        detections = detector.detect(frame)
        males, females = [], []

        # ---------- PERSON + GENDER ----------
        for x1, y1, x2, y2, conf, crop in detections:
            if crop.shape[0] < 80 or crop.shape[1] < 80:
                continue

            gender = gender_model.predict(crop)
            cx, cy = (x1 + x2)//2, (y1 + y2)//2

            if gender == "Male":
                males.append((cx, cy))
                color = (255, 0, 0)
            else:
                females.append((cx, cy))
                color = (0, 255, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, gender, (x1, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # ---------- RISK ANALYSIS ----------
        risk_event = risk.analyze(females, males)

        if risk_event:
            alert_key = f"WOMAN_{risk_event}"

            if logger.should_log(cam_id, alert_key, cooldown=8):
                level = "LOW" if risk_event == "ISOLATED" else "MEDIUM"

                play_priority_sound(
                    alert_sound,
                    "isolated" if level == "LOW" else "surrounded",
                    level
                )

                async_alert(mailer.send_email, alert_key)

                logger.log(
                    cam_id,
                    alert_key,
                    camera["lat"],
                    camera["lon"],
                    severity=level,
                    risk=1 if level == "LOW" else 3
                )

        # ---------- HELP GESTURE (EDGE TRIGGERED) ----------
        gesture_label = gesture.detect(frame)

        if gesture_label in ("TUCK_THUMB", "TRAP_THUMB"):
            if last_gesture != gesture_label:
                if logger.should_log(cam_id, gesture_label, cooldown=10):
                    play_priority_sound(alert_sound, "sos", "HIGH")
                    async_alert(mailer.send_email, gesture_label)

                    logger.log(
                        cam_id,
                        gesture_label,
                        camera["lat"],
                        camera["lon"],
                        severity="HIGH",
                        risk=5
                    )

                last_gesture = gesture_label

            cv2.putText(
                frame,
                f"HELP GESTURE: {gesture_label}",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )
        else:
            last_gesture = None

        # ---------- SOUND ANOMALY ----------
        if sound.detected():
            if logger.should_log(cam_id, "HIGH_RISK_AUDIO", cooldown=10):
                play_priority_sound(alert_sound, "high_risk", "HIGH")
                async_alert(mailer.send_email, "HIGH_RISK_AUDIO")

                logger.log(
                    cam_id,
                    "HIGH_RISK_AUDIO",
                    camera["lat"],
                    camera["lon"],
                    severity="HIGH",
                    risk=5
                )

        with frame_lock:
            latest_frames[cam_id] = frame.copy()

        with stats_lock:
            stats["persons"] = len(males) + len(females)
            stats["women"] = len(females)

# ================= STREAM =================
def generate_frames(cam_id):
    while True:
        with frame_lock:
            frame = latest_frames.get(cam_id)

        if frame is None:
            time.sleep(0.05)
            continue

        ret, buf = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buf.tobytes() +
            b"\r\n"
        )

@app.route("/video/<cam_id>")
def video_cam(cam_id):
    return Response(
        generate_frames(cam_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ================= HOTSPOT WORKER =================
def camera_risk_worker():
    while True:
        subprocess.run(["python", "compute_camera_risk.py"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        subprocess.run(["python", "generate_hotspot_map.py"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        time.sleep(30)

# ================= ENTRY =================
if __name__ == "__main__":
    init_risk_state()
    generate_initial_hotspot_map()

    for cam in CAMERAS:
        threading.Thread(
            target=camera_worker,
            args=(cam,),
            daemon=True
        ).start()

    threading.Thread(
        target=camera_risk_worker,
        daemon=True
    ).start()

    app.run(host="0.0.0.0", port=5000, threaded=True)
