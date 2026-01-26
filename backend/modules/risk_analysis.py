import time
import math

class RiskAnalyzer:
    def __init__(self):
        self.isolation_start = None
        self.surround_start = None

        self.ISOLATION_TIME = 1
        self.SURROUND_TIME = 1
        self.DIST_THRESHOLD = 150

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def analyze(self, females, males):
        now = time.time()

        if len(females) == 1 and len(males) == 0:
            self.isolation_start = self.isolation_start or now
            if now - self.isolation_start > self.ISOLATION_TIME:
                return "ISOLATED"
        else:
            self.isolation_start = None

        if len(females) >= 1 and len(males) >= 3:
            for f in females:
                close = sum(1 for m in males if self._dist(f, m) < self.DIST_THRESHOLD)
                if close >= 3:
                    self.surround_start = self.surround_start or now
                    if now - self.surround_start > self.SURROUND_TIME:
                        return "SURROUNDED"
        else:
            self.surround_start = None

        return None
