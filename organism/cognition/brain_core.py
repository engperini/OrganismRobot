class BrainCore:
    def __init__(self):
        print("[brain] BrainCore initialized")

    def think(self, world, state, memory):
        camera = world.get("camera_summary")

        if camera and camera != "None":
            intent = "observe_scene"
            mood = "curious"
        else:
            intent = "search_for_input"
            mood = "bored"

        return {
            "intent": intent,
            "mood": mood,
            "energy": state.energy,
            "curiosity": state.curiosity,
            "memory_size": len(memory.items),
        }
