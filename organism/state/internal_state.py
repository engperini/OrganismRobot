class InternalState:
    def __init__(self):
        self.curiosity = 0.5
        self.boredom = 0.0
        self.energy = 1.0
        self.mood = "neutral"

    def as_dict(self):
        return {
            "curiosity": self.curiosity,
            "boredom": self.boredom,
            "energy": self.energy,
            "mood": self.mood,
        }
