import time

class Watchdog:
    def __init__(self):
        self.last_tick = time.time()

    def tick(self):
        self.last_tick = time.time()

    def seconds_since_tick(self) -> float:
        return time.time() - self.last_tick
