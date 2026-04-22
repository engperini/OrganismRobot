from core.schemas import ExpressionState

class DisplayFaceRender:
    def __init__(self):
        self.last_expression = ExpressionState()

    def render(self, expression: ExpressionState):
        self.last_expression = expression
        return {
            "mood": expression.mood,
            "face_mode": expression.face_mode,
        }
