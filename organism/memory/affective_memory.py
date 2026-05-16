class AffectiveMemory:
    def __init__(self):
        self.items = []

    def remember(self, item):
        self.items.append(item)

        if len(self.items) > 50:
            self.items = self.items[-50:]

    def recent(self, limit=5):
        return self.items[-limit:]
