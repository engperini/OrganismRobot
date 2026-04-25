import json

from core.schemas import Thought
from cognition.llm.factory import get_llm_provider


class ThinkerAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def run(self, world_state, memories=None) -> Thought:
        memories = memories or []

        system = (
            "You are the free-thinking cognitive core of a physical robot organism. "
            "You do not directly control hardware. You interpret the world_state, current_goal, "
            "risks, mood, and recent memory. Return ONLY valid JSON. No markdown."
        )

        prompt = json.dumps(
            {
                "world_state": world_state.model_dump(mode="json"),
                "memories": memories[-5:] if isinstance(memories, list) else [],
                "required_json_schema": {
                    "assessment": "short human-readable situation assessment",
                    "intent": "high level intention",
                    "strategy": ["short strategy step"],
                    "mood": "sleepy | curious | bored | neutral",
                    "store_candidate": False,
                    "why_store": None,
                },
                "rules": [
                    "Use current_goal as a central decision input.",
                    "If there is physical risk, prefer observation or stop.",
                    "Do not invent hardware actions.",
                    "Keep strategy short.",
                    "Mood must be one of: sleepy, curious, bored, neutral.",
                ],
            },
            ensure_ascii=False,
        )

        try:
            data = self.llm.complete_json(prompt=prompt, system=system)
            return Thought(
                assessment=data.get("assessment", "No assessment."),
                intent=data.get("intent", "idle"),
                strategy=data.get("strategy", ["wait"]),
                mood=data.get("mood", "bored"),
                store_candidate=bool(data.get("store_candidate", False)),
                why_store=data.get("why_store"),
            )
        except Exception as exc:
            return Thought(
                assessment=f"LLM fallback active: {exc}",
                intent="idle",
                strategy=["wait", "observe"],
                mood="bored",
                store_candidate=False,
            )
