import time

from actuation.action_router import ActionRouter
from actuation.body_state_renderer import BodyStateRenderer
from actuation.display_face_render import DisplayFaceRender
from actuation.expression_mapper import ExpressionMapper
from actuation.inner_voice import InnerVoice
from core.logging import get_logger
from core.schemas import ExecutablePlan, ExecutionResult, WorldState

logger = get_logger("executor")


class Executor:
    def __init__(
        self,
        action_router: ActionRouter,
        face_renderer: DisplayFaceRender,
        inner_voice: InnerVoice,
        expression_mapper: ExpressionMapper,
        body_state_renderer: BodyStateRenderer,
    ) -> None:
        self.action_router = action_router
        self.face_renderer = face_renderer
        self.inner_voice = inner_voice
        self.expression_mapper = expression_mapper
        self.body_state_renderer = body_state_renderer
        self.last_render_payload: dict | None = None

    def run_plan(self, plan: ExecutablePlan, world_state: WorldState) -> ExecutionResult:
        started = time.perf_counter()
        completed = 0

        try:
            expression = self.expression_mapper.map_from_world_state(
                world_state=world_state,
                expression_hint=plan.expression,
            )
            voice = self.inner_voice.render_message(
                world_state=world_state,
                voice_hint=plan.voice_hint,
            )

            self.face_renderer.render(expression)
            self.last_render_payload = self.body_state_renderer.compose(expression, voice)

            for action in plan.actions:
                self.action_router.dispatch(action.tool, action.args)
                completed += 1

            elapsed = time.perf_counter() - started
            logger.info("plan %s executed with %s actions", plan.plan_id, completed)
            return ExecutionResult(
                plan_id=plan.plan_id,
                status="success",
                completed_actions=completed,
                duration_s=elapsed,
            )

        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - started
            logger.exception("plan %s failed: %s", plan.plan_id, exc)
            return ExecutionResult(
                plan_id=plan.plan_id,
                status="failed",
                completed_actions=completed,
                failed_action=None,
                failure_reason=str(exc),
                duration_s=elapsed,
            )
