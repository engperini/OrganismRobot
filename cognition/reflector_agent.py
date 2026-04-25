from collections import Counter

from core.schemas import Reflection


class ReflectorAgent:
    def run(self, world_state, thought, plan, result, recent_context=None) -> Reflection:
        recent_context = recent_context or []

        recent_intent_types = [
            item.get("intent_type")
            for item in recent_context
            if isinstance(item, dict) and item.get("intent_type")
        ]

        counter = Counter(recent_intent_types)
        current_intent_type = getattr(thought, "intent_type", None)

        repetition_detected = False
        suggested_next_focus = None
        suggested_mood_shift = None
        avoid_next_intent_type = None
        reflection_hint = None

        if current_intent_type and counter.get(current_intent_type, 0) >= 3:
            repetition_detected = True
            avoid_next_intent_type = current_intent_type
            suggested_next_focus = "quiet observation or different attention target"
            suggested_mood_shift = "bored"
            reflection_hint = (
                f"The organism repeated intent_type '{current_intent_type}' several times "
                "without clear new information. Reduce repetition, lower urgency, and consider "
                "quiet observation, rest, or shifting attention."
            )

        lesson = None
        novelty_score = 0.1

        if world_state.front_distance_cm is not None and world_state.front_distance_cm < 20:
            lesson = "Head-first inspection is safer than forward motion near obstacles."
            novelty_score = 0.3

        if world_state.last_error:
            lesson = "Critical errors should immediately shift the organism into safe_stop."
            novelty_score = 0.6

        if repetition_detected:
            novelty_score = max(novelty_score, 0.2)

        return Reflection(
            episode_summary=(
                f"intent_type={getattr(thought, 'intent_type', None)}; "
                f"intent={thought.intent}; result={result.status}; "
                f"actions={result.completed_actions}"
            ),
            lesson=lesson,
            repetition_detected=repetition_detected,
            suggested_next_focus=suggested_next_focus,
            suggested_mood_shift=suggested_mood_shift,
            avoid_next_intent_type=avoid_next_intent_type,
            reflection_hint=reflection_hint,
            store_structured=True,
            novelty_score=novelty_score,
            policy_feedback={
                "context_signature": f"mode={world_state.mode};goal={world_state.current_goal}",
                "action_signature": getattr(thought, "intent_type", thought.intent),
                "score_delta": 0.1 if result.status == "success" and not repetition_detected else -0.1,
            },
        )
