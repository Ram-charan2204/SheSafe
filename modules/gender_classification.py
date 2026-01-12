import cv2
import os

class GenderClassifier:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        proto = os.path.join(BASE_DIR, "models", "gender", "gender_deploy.prototxt")
        model = os.path.join(BASE_DIR, "models", "gender", "gender_net.caffemodel")

        self.net = cv2.dnn.readNetFromCaffe(proto, model)
        self.labels = ["Male", "Female"]

    def predict(self, img):
        if img is None or img.size == 0:
            return "Unknown"

        blob = cv2.dnn.blobFromImage(
            img, 1.0, (227, 227),
            (78.4263, 87.7689, 114.8958),
            swapRB=False
        )
        self.net.setInput(blob)
        preds = self.net.forward()
        return self.labels[preds[0].argmax()]
