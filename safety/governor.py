class SafetyGovernor:
    def allow(self, world_state):
        if world_state.front_distance_cm and world_state.front_distance_cm < 20:
            return False
        return True
