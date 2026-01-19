import threading
import time

stats = {
    "persons": 0,
    "women": 0
}

stats_lock = threading.Lock()

camera_heartbeat = {}
heartbeat_lock = threading.Lock()
