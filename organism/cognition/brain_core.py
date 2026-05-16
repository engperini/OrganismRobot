class BrainCore:
    def __init__(self):
        print("[brain] BrainCore initialized")

    def think(self, world, state, memory):
        camera = world.get("camera_summary")
        distance = world.get("distance_front_cm")
        runtime_mode = world.get("runtime_mode")

        if distance is not None and float(distance) < 20:
            intent = "safe_stop"
            mood = "alert"
            action = {"name": "motors.stop", "args": {}}

        elif camera and camera != "None":
            intent = "observe_scene"
            mood = "curious"
            action = {"name": "servos.random", "args": {}}

        else:
            intent = "search_for_input"
            mood = "bored"
            action = {"name": "servos.center", "args": {}}

        return {
            "intent": intent,
            "mood": mood,
            "action": action,
            "runtime_mode": runtime_mode,
            "energy": state.energy,
            "curiosity": state.curiosity,
            "memory_size": len(memory.items),
        }
