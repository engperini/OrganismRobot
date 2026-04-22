from core.schemas import ExpressionState, InnerVoiceMessage


class BodyStateRenderer:
    def compose(
        self,
        expression: ExpressionState,
        voice: InnerVoiceMessage,
    ) -> dict:
        return {
            "expression": expression.model_dump(),
            "voice": voice.model_dump(),
        }
