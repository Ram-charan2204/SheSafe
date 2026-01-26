import cv2
import mediapipe as mp
import math

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if not result.multi_hand_landmarks:
            return None

        for hand in result.multi_hand_landmarks:
            lm = hand.landmark

            thumb_tip = lm[self.mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = lm[self.mp_hands.HandLandmark.THUMB_IP]
            thumb_mcp = lm[self.mp_hands.HandLandmark.THUMB_MCP]
            index_mcp = lm[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
            ring_mcp = lm[self.mp_hands.HandLandmark.RING_FINGER_MCP]
            pinky_mcp = lm[self.mp_hands.HandLandmark.PINKY_MCP]

            palm_x = (index_mcp.x + ring_mcp.x + pinky_mcp.x) / 3
            palm_y = (index_mcp.y + ring_mcp.y + pinky_mcp.y) / 3

            dist = math.sqrt(
                (thumb_tip.x - palm_x) ** 2 +
                (thumb_tip.y - palm_y) ** 2
            )

            # ✔ TUCK THUMB
            if thumb_tip.y > index_mcp.y and dist < 0.12:
                return "TUCK_THUMB"

            # ✔ TRAP THUMB
            if thumb_tip.y < thumb_mcp.y and dist < 0.18:
                return "TRAP_THUMB"

        return None
