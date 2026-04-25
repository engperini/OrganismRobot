from collections import deque


class ShortTermMemory:
    def __init__(self, size=50):
        self.buffer = deque(maxlen=size)

    def add(self, item):
        self.buffer.append(item)

    def recent(self, limit=5):
        if limit <= 0:
            return []
        return list(self.buffer)[-limit:]

    def size(self):
        return len(self.buffer)
