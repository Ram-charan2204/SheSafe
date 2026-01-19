from playsound import playsound
import os
import threading

class AlertSound:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.alerts = os.path.join(BASE_DIR, "alerts")

        self.sounds = {
            "isolated": os.path.join(self.alerts, "woman_isolated.mp3"),
            "surrounded": os.path.join(self.alerts, "woman_surrounded.mp3"),
            "high_risk": os.path.join(self.alerts, "high_risk.mp3"),
            "sos": os.path.join(self.alerts, "sos_gesture.mp3")
        }

    def play(self, key):
        if key in self.sounds:
            threading.Thread(
                target=playsound,
                args=(self.sounds[key],),
                daemon=True
            ).start()
