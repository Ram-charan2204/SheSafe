import cv2

net = cv2.dnn.readNetFromCaffe(
    "models/gender/gender_deploy.prototxt",
    "models/gender/gender_net.caffemodel"
)

print("✅ Gender model loaded successfully")
