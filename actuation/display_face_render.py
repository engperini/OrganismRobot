from core.logging import get_logger
from core.schemas import ExpressionState

logger = get_logger("display_face")


class DisplayFaceRender:
    def __init__(self) -> None:
        self.current = ExpressionState(mood="neutral", face_mode="neutral")

    def render(self, expression: ExpressionState) -> ExpressionState:
        self.current = expression
        logger.info(
            "face -> mood=%s face_mode=%s",
            expression.mood,
            expression.face_mode,
        )
        return self.current

    def get_current(self) -> ExpressionState:
        return self.current
