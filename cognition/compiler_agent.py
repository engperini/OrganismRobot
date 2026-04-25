from core.schemas import ExecutablePlan, PlanAction


class CompilerAgent:
    def run(self, thought) -> ExecutablePlan:
        actions = []
        intent_type = (getattr(thought, "intent_type", "") or "").lower()

        # This is not the safety layer.
        # It only maps broad cognitive intention into minimal executable body behavior.

        if any(key in intent_type for key in ["safe_stop", "protect", "error"]):
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="pan_tilt.center"))

        elif any(key in intent_type for key in ["explore", "curious", "search"]):
            actions.append(PlanAction(tool="pan_tilt.explore_step"))

        elif any(key in intent_type for key in ["inspect", "investigate", "sound", "image", "attention", "human", "interact"]):
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="pan_tilt.look_left"))
            actions.append(PlanAction(tool="pan_tilt.look_right"))

        elif any(key in intent_type for key in ["rest", "sleep", "idle", "observe", "wait", "monitor"]):
            actions.append(PlanAction(tool="motors.stop"))

        else:
            # Unknown intention is allowed cognitively.
            # Execution stays conservative until more tools exist.
            actions.append(PlanAction(tool="motors.stop"))

        return ExecutablePlan(
            plan_id="plan_static",
            actions=actions,
            policy={
                "allow_base_motion": False,
                "max_duration_s": 3,
                "source_intent_type": intent_type,
                "confidence": getattr(thought, "confidence", 0.5),
                "urgency": getattr(thought, "urgency", 0.0),
                "curiosity": getattr(thought, "curiosity", 0.0),
            },
            expression={
                "mood": thought.mood,
                "attention_target": getattr(thought, "attention_target", None),
            },
            voice_hint=getattr(thought, "external_message", None),
            store_memory=thought.store_candidate,
            memory_hint=thought.intent,
        )
