from camera_config import CAMERAS

# Shared in-memory store (imported by api & analytics)
camera_risk = {}
high_risk_zones = []

def init_risk_state():
    global camera_risk, high_risk_zones

    camera_risk.clear()
    high_risk_zones.clear()

    for cam in CAMERAS:
        camera_risk[cam["id"]] = {
            "risk": 0,
            "lat": cam["lat"],
            "lon": cam["lon"],
            "location": cam["location"]
        }

        high_risk_zones.append({
            "camera_id": cam["id"],
            "location": cam["location"],
            "lat": cam["lat"],
            "lon": cam["lon"],
            "risk": 0,
            "level": "LOW"
        })
