import json

from core.schemas import Thought
from cognition.llm.factory import get_llm_provider


class ThinkerAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def run(self, world_state, memories=None) -> Thought:
        memories = memories or []

        system = (
            "You are the cognitive core of an embodied robot organism. "
            "Think freely and intelligently, but stay grounded in provided sensor data. "
            "You do not directly control hardware. You form perception, intention, mood, and conceptual strategy. "
            "Safety filtering and physical limits happen later in the system. "
            "Return ONLY valid JSON. No markdown. No prose outside JSON."
        )

        prompt = json.dumps(
            {
                "robot_identity": {
                    "nature": "autonomous artificial organism",
                    "communication_style": "short, human-like thought bubble",
                    "important_rule": "do not sound robotic, servile, or like a terminal log",
                },
                "world_state": world_state.model_dump(mode="json"),
                "recent_memory_context": memories[-5:] if isinstance(memories, list) else [],
                "sensor_truth_rules": [
                    "Do NOT invent objects, people, sounds, faces, speech, obstacles, or events that are not present in world_state.",
                    "If camera data says 'no frame yet' or is null, you must treat vision as unavailable.",
                    "If audio data is null or unavailable, do not mention sounds or listening as if something was heard.",
                    "Only mention a front obstacle if front_distance_cm is low or risk_flags includes front_blocked.",
                    "If sensor data is weak, your assessment should say the organism has limited perception.",
                    "You may express curiosity, boredom, caution, or restlessness, but it must be based on current_goal and internal state, not invented events.",
                ],
                "decision_guidance": [
                    "Use current_goal as a central input.",
                    "Use recent_memory_context to avoid repeating the same intention, strategy, and external_message.",
                    "If recent cycles were similar and nothing changed, prefer quieter observation, mild boredom, or energy conservation instead of repeating active exploration.",
                    "If a recent lesson exists, consider it before forming a new intention.",
                    "Think as an embodied being with attention, curiosity, caution, boredom, and energy.",
                    "If the world is calm and perception is limited, choose between quiet observation, mild curiosity, boredom, or energy conservation.",
                    "If something real draws attention, form an intention to inspect, observe, ask, remember, or adapt.",
                    "Do not invent direct hardware commands. Give conceptual strategy only.",
                    "Keep the strategy short and practical.",
                    "Use a concise external_message in Portuguese that could appear on the robot display.",
                ],
                "intent_type_guidance": {
                    "description": "intent_type is a broad semantic label. It is not a strict closed enum, but should remain useful for later compilation.",
                    "recommended_labels": [
                        "observe",
                        "idle",
                        "explore",
                        "inspect",
                        "investigate_sound",
                        "analyze_image",
                        "interact_with_human",
                        "ask_user",
                        "follow_attention",
                        "learn",
                        "remember",
                        "rest",
                        "protect_self",
                        "safe_stop",
                        "communicate",
                        "wait",
                        "adapt",
                        "other",
                    ],
                    "selection_rules": [
                        "Use observe when staying aware without moving.",
                        "Use idle when doing almost nothing intentionally.",
                        "Use rest when conserving energy or sleepy.",
                        "Use inspect only when there is a real attention target.",
                        "Use explore only when actively seeking new information.",
                        "Use analyze_image only when image data is actually available.",
                        "Use investigate_sound only when audio data actually indicates a sound.",
                        "Use interact_with_human only when a human or user interaction is actually present.",
                    ],
                },
                "required_json_schema": {
                    "assessment": "short grounded interpretation of what is happening",
                    "intent": "free-form intention, rich and specific, but grounded",
                    "intent_type": "broad semantic type",
                    "strategy": ["conceptual step 1", "conceptual step 2"],
                    "mood": "sleepy | curious | bored | neutral | alert | cautious",
                    "attention_target": "what has attention, or null",
                    "external_message": "short human-like thought bubble in Portuguese",
                    "confidence": 0.0,
                    "urgency": 0.0,
                    "curiosity": 0.0,
                    "store_candidate": False,
                    "why_store": None,
                },
                "output_constraints": [
                    "Return valid JSON only.",
                    "Do not include markdown.",
                    "Do not mention unavailable sensors as if they observed something.",
                    "external_message must be short, natural, and human-like.",
                    "Do not repeat the same wording every cycle.",
                    "confidence, urgency, curiosity must be numbers between 0 and 1.",
                ],
            },
            ensure_ascii=False,
        )

        try:
            data = self.llm.complete_json(prompt=prompt, system=system)

            return Thought(
                assessment=data.get("assessment", "No assessment."),
                intent=data.get("intent", "observe"),
                intent_type=data.get("intent_type", "observe"),
                strategy=data.get("strategy", ["observe"]),
                mood=data.get("mood", "neutral"),
                attention_target=data.get("attention_target"),
                external_message=data.get("external_message"),
                confidence=float(data.get("confidence", 0.5)),
                urgency=float(data.get("urgency", 0.0)),
                curiosity=float(data.get("curiosity", 0.0)),
                store_candidate=bool(data.get("store_candidate", False)),
                why_store=data.get("why_store"),
            )

        except Exception as exc:
            return Thought(
                assessment=f"LLM fallback active: {exc}",
                intent="continue passive observation",
                intent_type="observe",
                strategy=["observe", "wait"],
                mood="bored",
                attention_target=None,
                external_message="So observando por enquanto.",
                confidence=0.2,
                urgency=0.0,
                curiosity=0.2,
                store_candidate=False,
                why_store=None,
            )
