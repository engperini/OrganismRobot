from core.schemas import ExpressionState


class ExpressionMapper:
    def map(
        self,
        mood: str | None,
        intent: str | None = None,
        risk_flags: list[str] | None = None,
        attention_target: str | None = None,
        urgency: float = 0.0,
        curiosity: float = 0.0,
        confidence: float = 0.5,
    ) -> ExpressionState:
        risk_flags = risk_flags or []
        mood = mood or "neutral"
        intent = (intent or "").lower()

        if "critical_error" in risk_flags:
            return ExpressionState(mood="alert", face_mode="alert")

        if "front_blocked" in risk_flags or urgency >= 0.7:
            return ExpressionState(mood="cautious", face_mode="cautious_focus")

        if mood == "sleepy":
            return ExpressionState(mood="sleepy", face_mode="sleepy")

        if mood == "bored":
            if curiosity >= 0.6:
                return ExpressionState(mood="bored", face_mode="bored_curious")
            return ExpressionState(mood="bored", face_mode="bored")

        if mood == "curious" or curiosity >= 0.7:
            if attention_target:
                return ExpressionState(mood="curious", face_mode="focused")
            return ExpressionState(mood="curious", face_mode="curious")

        if mood == "cautious":
            return ExpressionState(mood="cautious", face_mode="cautious_focus")

        if "inspect" in intent or "investigate" in intent:
            return ExpressionState(mood="curious", face_mode="focused")

        if "rest" in intent or "wait" in intent:
            return ExpressionState(mood="sleepy", face_mode="soft_idle")

        if confidence < 0.35:
            return ExpressionState(mood="uncertain", face_mode="uncertain")

        return ExpressionState(mood="neutral", face_mode="neutral")
