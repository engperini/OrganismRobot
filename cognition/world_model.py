from core.schemas import WorldState

class WorldModel:
    def __init__(self):
        self.state = WorldState()

    def update_from_perception(self, perception):
        self.state.front_distance_cm = perception.get("distance")
