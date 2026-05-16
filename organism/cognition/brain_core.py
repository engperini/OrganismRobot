class BrainCore:
    def __init__(self):
        print("[brain] BrainCore initialized")

    def _camera_description(self, world):
        camera = world.get("camera_summary") or {}
        llm = camera.get("llm_description") or {}
        return llm.get("description")

    def think(self, world, state, memory):
        runtime_mode = world.get("runtime_mode")
        distance = world.get("distance_front_cm")
        description = self._camera_description(world)

        repeated = memory.repeated_scene()
        safe_stop = distance is not None and float(distance) < 20
        saw_scene = bool(description)

        state.update(
            repeated=repeated,
            safe_stop=safe_stop,
            saw_scene=saw_scene,
        )

        if safe_stop:
            intent = "safe_stop"
            mood = "alert"
            inner_voice = "Tem algo perto demais. Vou parar."
            action = {"name": "motors.stop", "args": {}}

        elif repeated and runtime_mode == "pc_simulation":
            intent = "change_visual_attention"
            mood = "bored"
            inner_voice = "Estou vendo a mesma coisa. Vou mudar o olhar."
            action = {"name": "servos.random", "args": {}}

        elif repeated and runtime_mode == "raspberry_hardware":
            intent = "change_perspective"
            mood = "curious"
            inner_voice = "Essa visão repetiu. Vou mudar minha perspectiva."
            action = {"name": "motors.turn_left", "args": {"duration": 0.7}}

        elif saw_scene:
            intent = "observe_scene"
            mood = "curious"
            inner_voice = "Isso chamou minha atenção."
            action = {"name": "servos.random", "args": {}}

        else:
            intent = "search_for_input"
            mood = "bored"
            inner_voice = "Minha percepção está fraca. Vou centralizar."
            action = {"name": "servos.center", "args": {}}

        return {
            "intent": intent,
            "mood": mood,
            "inner_voice": inner_voice,
            "action": action,
            "runtime_mode": runtime_mode,
            "scene_repeated": repeated,
            "description": description,
            "state": state.as_dict(),
            "memory_size": len(memory.items),
        }
