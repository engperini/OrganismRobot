class InternalState:
    def __init__(self):
        self.curiosity = 0.5
        self.boredom = 0.0
        self.energy = 1.0
        self.mood = "neutral"

    def update(self, repeated=False, safe_stop=False, saw_scene=False):
        self.energy = max(0.0, self.energy - 0.01)

        if safe_stop:
            self.mood = "alert"
            self.boredom = max(0.0, self.boredom - 0.05)
            return

        if repeated:
            self.boredom = min(1.0, self.boredom + 0.15)
            self.curiosity = min(1.0, self.curiosity + 0.08)
            self.mood = "bored"
            return

        if saw_scene:
            self.boredom = max(0.0, self.boredom - 0.05)
            self.curiosity = min(1.0, self.curiosity + 0.03)
            self.mood = "curious"
            return

        self.boredom = min(1.0, self.boredom + 0.05)
        self.mood = "neutral"

    def as_dict(self):
        return {
            "curiosity": self.curiosity,
            "boredom": self.boredom,
            "energy": self.energy,
            "mood": self.mood,
        }
