from ultralytics import YOLO

class YOLOv8Detector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.person_class_id = 0  # person class

    def detect(self, frame):
        results = self.model(frame, stream=True, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == self.person_class_id:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    crop = frame[y1:y2, x1:x2]
                    detections.append((x1, y1, x2, y2, conf, crop))

        return detections
