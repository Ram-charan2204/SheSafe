import cv2
import time

from modules.video_processing import VideoStream
from modules.yolo_detection import YOLOv11Detector
from modules.gender_classification import GenderClassifier
from modules.risk_analysis import RiskAnalyzer
from modules.alert_sound import AlertSound
from modules.sound_detection import SoundAnomalyDetector
from modules.alert_router import AlertRouter
from modules.alert_logger import AlertLogger


def main():
    # ---------------- CONFIG ----------------
    CAMERA_ID = "CAM_01"          # 🔥 UNIQUE ID PER CAMERA
    LATITUDE = 17.3850
    LONGITUDE = 78.4867

    # ---------------- INITIALIZATION ----------------
    video = VideoStream(0)
    detector = YOLOv11Detector("yolov8n.pt")
    gender_model = GenderClassifier()
    risk_analyzer = RiskAnalyzer()
    alert_sound = AlertSound()
    sound_detector = SoundAnomalyDetector()
    router = AlertRouter()
    logger = AlertLogger()

    sound_detector.start()

    prev_time = 0
    last_alert = None

    print("✅ SHE SAFE system running with camera prioritization")

    # ---------------- MAIN LOOP ----------------
    while True:
        frame = video.get_frame()
        if frame is None:
            break

        detections = detector.detect(frame)

        males, females = [], []
        male_count = female_count = 0

        # SOS placeholder (Stage 9)
        sos_gesture_detected = False

        # ---------------- PERSON PROCESSING ----------------
        for x1, y1, x2, y2, conf, crop in detections:
            gender = gender_model.predict(crop)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if gender == "Male":
                male_count += 1
                males.append((cx, cy))
                color = (255, 0, 0)
            elif gender == "Female":
                female_count += 1
                females.append((cx, cy))
                color = (0, 255, 255)
            else:
                color = (200, 200, 200)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, gender, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # ---------------- PRIORITY 1: SOS ----------------
        if sos_gesture_detected:
            alert_sound.play("sos")
            router.send_email("SOS Gesture Detected")
            logger.log(CAMERA_ID, "SOS_GESTURE", LATITUDE, LONGITUDE)

            cv2.putText(frame, "🚨 EMERGENCY: SOS GESTURE DETECTED",
                        (30, frame.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # ---------------- PRIORITY 2: SOUND + WOMAN ----------------
        elif sound_detector.detected() and len(females) >= 1:
            alert_sound.play("high_risk")
            router.send_email("High Risk Audio-Visual Alert")
            logger.log(CAMERA_ID, "HIGH_RISK_AUDIO", LATITUDE, LONGITUDE)

            cv2.putText(frame, "🚨 HIGH RISK: DISTRESS SOUND DETECTED",
                        (30, frame.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # ---------------- PRIORITY 3: VISION RISK ----------------
        else:
            alert = risk_analyzer.analyze(females, males)

            if alert and alert != last_alert:
                last_alert = alert

                if alert == "isolated":
                    alert_sound.play("isolated")
                    router.send_email("Woman Isolated")
                    logger.log(CAMERA_ID, "WOMAN_ISOLATED", LATITUDE, LONGITUDE)
                    msg = "🚨 RISK: Woman Isolated"

                elif alert == "surrounded":
                    alert_sound.play("surrounded")
                    router.send_email("Woman Surrounded by Men")
                    logger.log(CAMERA_ID, "WOMAN_SURROUNDED", LATITUDE, LONGITUDE)
                    msg = "🚨 RISK: Woman Surrounded by Men"

                cv2.putText(frame, msg,
                            (30, frame.shape[0] - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            if not alert:
                last_alert = None

        # ---------------- FPS & COUNTERS ----------------
        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time)) if prev_time else 0
        prev_time = curr_time

        cv2.putText(frame, f"Men: {male_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        cv2.putText(frame, f"Women: {female_count}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.putText(frame, f"FPS: {fps}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("SHE SAFE – Risk‑Aware Camera System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    print("🛑 SHE SAFE stopped")


if __name__ == "__main__":
    main()
