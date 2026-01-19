import csv
import os
import time
from datetime import datetime

class AlertLogger:
    def __init__(self):
        self.file = "alert_logs.csv"
        self.last_alert = {}

        if not os.path.exists(self.file):
            with open(self.file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "camera_id", "alert_type", "latitude", "longitude"
                ])

    def should_log(self, cam_id, alert, cooldown=10):
        now = time.time()
        key = f"{cam_id}:{alert}"
        if key not in self.last_alert or now - self.last_alert[key] > cooldown:
            self.last_alert[key] = now
            return True
        return False

    def log(self, camera_id, alert_type, lat, lon):
        with open(self.file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                camera_id,
                alert_type,
                lat,
                lon
            ])
