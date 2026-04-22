from core.schemas import WorldState, Perception, RawSensorSnapshot

class WorldModel:
    def __init__(self):
        self.state = WorldState()

    def update(self, snapshot: RawSensorSnapshot, perception: Perception) -> WorldState:
        motors_state = "stopped"
        if snapshot.left_motor_state != "stop" or snapshot.right_motor_state != "stop":
            motors_state = "moving"

        mood = self.state.mood
        if self.state.mode == "idle":
            mood = "bored"
        if self.state.mode == "explore":
            mood = "curious"
        if snapshot.battery_pct is not None and snapshot.battery_pct < 20:
            mood = "sleepy"

        self.state = self.state.copy(update={
            "front_distance_cm": snapshot.distance_front_cm,
            "servo_pan_deg": snapshot.servo_pan_deg,
            "servo_tilt_deg": snapshot.servo_tilt_deg,
            "battery_pct": snapshot.battery_pct,
            "last_error": snapshot.last_error,
            "risk_flags": perception.risk_flags,
            "motors_state": motors_state,
            "mood": mood,
            "attention_target": perception.attention_candidates[0] if perception.attention_candidates else None,
        })
        return self.state
