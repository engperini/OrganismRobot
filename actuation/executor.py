import time
from core.schemas import ExecutionResult
from actuation.action_router import ActionRouter
from actuation.expression_mapper import ExpressionMapper
from actuation.inner_voice import InnerVoice
from actuation.display_face_render import DisplayFaceRender
from actuation.body_state_renderer import BodyStateRenderer

class Executor:
    def __init__(self):
        self.router = ActionRouter()
        self.expression_mapper = ExpressionMapper()
        self.inner_voice = InnerVoice()
        self.face_renderer = DisplayFaceRender()
        self.body_renderer = BodyStateRenderer()

        self.last_render = {}
        self.last_result = None

    def run_plan(self, plan, world_state):
        started = time.time()
        completed = 0
        failed_action = None
        failure_reason = None

        plan_expression = getattr(plan, "expression", None) or {}

        expression = self.expression_mapper.map(
            mood=plan_expression.get("mood") or getattr(world_state, "mood", None),
            intent=getattr(plan, "memory_hint", None),
            risk_flags=getattr(world_state, "risk_flags", []),
            attention_target=plan_expression.get("attention_target") or getattr(world_state, "attention_target", None),
            urgency=(getattr(plan, "policy", {}) or {}).get("urgency", 0.0),
            curiosity=(getattr(plan, "policy", {}) or {}).get("curiosity", 0.0),
            confidence=(getattr(plan, "policy", {}) or {}).get("confidence", 0.5),
        )
        face_state = self.face_renderer.render(expression)
        inner_voice = self.inner_voice.speak(
            mood=expression.mood,
            risk_flags=getattr(world_state, "risk_flags", []),
            voice_hint=getattr(plan, "voice_hint", None),
        )

        motor_state = {}
        servo_state = {}

        for action in plan.actions:
            try:
                result = self.router.dispatch(action.tool, action.args)
                completed += 1

                if action.tool.startswith("motors."):
                    motor_state = result
                elif action.tool.startswith("pan_tilt."):
                    servo_state = result
            except Exception as exc:
                failed_action = action.tool
                failure_reason = str(exc)
                break

        self.last_render = self.body_renderer.compose(
            motor_state=motor_state,
            servo_state=servo_state,
            face_state=face_state,
            inner_voice={"text": inner_voice.text, "duration_s": inner_voice.duration_s},
        )

        status = "success" if failed_action is None else "partial_success"

        self.last_result = ExecutionResult(
            plan_id=plan.plan_id,
            status=status,
            completed_actions=completed,
            failed_action=failed_action,
            failure_reason=failure_reason,
            duration_s=time.time() - started,
        )
        return self.last_result
