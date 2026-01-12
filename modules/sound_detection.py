import sounddevice as sd
import numpy as np
import time

class SoundAnomalyDetector:
    def __init__(self):
        self.THRESHOLD = 0.03
        self.last = 0
        self.triggered = False

    def _callback(self, indata, frames, time_info, status):
        volume = np.linalg.norm(indata) / frames
        if volume > self.THRESHOLD:
            now = time.time()
            if now - self.last > 1.5:
                self.triggered = True
                self.last = now

    def start(self):
        self.stream = sd.InputStream(channels=1, callback=self._callback)
        self.stream.start()

    def detected(self):
        if self.triggered:
            self.triggered = False
            return True
        return False
