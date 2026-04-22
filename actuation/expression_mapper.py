from core.schemas import ExpressionState

class ExpressionMapper:
    def map(self, mood: str | None, intent: str | None, risk_flags: list[str] | None = None) -> ExpressionState:
        risk_flags = risk_flags or []

        if "critical_error" in risk_flags:
            return ExpressionState(mood="alert", face_mode="alert")

        if mood == "sleepy":
            return ExpressionState(mood="sleepy", face_mode="sleepy")

        if mood == "bored":
            return ExpressionState(mood="bored", face_mode="bored")

        if mood == "curious" or intent in {"explore", "inspect", "investigate"}:
            return ExpressionState(mood="curious", face_mode="curious")

        return ExpressionState(mood="neutral", face_mode="neutral")
