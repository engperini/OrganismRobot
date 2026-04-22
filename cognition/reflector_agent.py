from core.schemas import Reflection

class ReflectorAgent:
    def run(self, world_state, thought, plan, result) -> Reflection:
        lesson = None
        novelty_score = 0.1

        if world_state.front_distance_cm is not None and world_state.front_distance_cm < 20:
            lesson = "Head-first inspection is safer than forward motion near obstacles."
            novelty_score = 0.3

        if world_state.last_error:
            lesson = "Critical errors should immediately shift the organism into safe_stop."
            novelty_score = 0.6

        return Reflection(
            episode_summary=f"intent={thought.intent}; result={result.status}; actions={result.completed_actions}",
            lesson=lesson,
            store_structured=True,
            novelty_score=novelty_score,
            policy_feedback={
                "context_signature": f"mode={world_state.mode}",
                "action_signature": thought.intent,
                "score_delta": 0.1 if result.status == "success" else -0.1,
            },
        )
