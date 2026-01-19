import cv2
import time

class VideoStream:
    def __init__(self, source=0):
        self.source = source
        self.cap = None
        self.open()

    def open(self):
        # 🔥 Laptop / USB camera
        if isinstance(self.source, int):
            self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        else:
            # 🔥 Mobile / IP camera (MJPEG)
            self.cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        if not self.cap.isOpened():
            raise Exception(f"❌ Cannot open video source: {self.source}")

    def get_frame(self):
        if not self.cap or not self.cap.isOpened():
            time.sleep(0.5)
            self.open()
            return None

        ret, frame = self.cap.read()
        if not ret:
            time.sleep(0.05)
            return None

        return frame

    def release(self):
        if self.cap:
            self.cap.release()
