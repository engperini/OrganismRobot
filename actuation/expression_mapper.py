from core.schemas import ExpressionState, WorldState


class ExpressionMapper:
    def map_from_world_state(
        self,
        world_state: WorldState,
        expression_hint: dict | None = None,
    ) -> ExpressionState:
        if expression_hint:
            return ExpressionState(
                mood=expression_hint.get("mood", world_state.mood or "neutral"),
                face_mode=expression_hint.get("face_mode", "neutral"),
            )

        if world_state.mode == "safe_stop":
            return ExpressionState(mood="sleepy", face_mode="sleepy")

        mood = world_state.mood or "neutral"

        if mood == "curious":
            return ExpressionState(mood="curious", face_mode="curious")
        if mood == "bored":
            return ExpressionState(mood="bored", face_mode="bored")
        if mood == "sleepy":
            return ExpressionState(mood="sleepy", face_mode="sleepy")

        return ExpressionState(mood="neutral", face_mode="neutral")
