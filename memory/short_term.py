from collections import deque

class ShortTermMemory:
    def __init__(self, size=50):
        self.buffer = deque(maxlen=size)

    def add(self, item):
        self.buffer.append(item)
