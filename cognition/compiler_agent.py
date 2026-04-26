from core.schemas import ExecutablePlan, PlanAction


class CompilerAgent:
    def run(self, thought) -> ExecutablePlan:
        actions = []
        intent_type = (getattr(thought, "intent_type", "") or "").lower()

        # Mapeamento de intenções para comandos físicos
        if any(key in intent_type for key in ["safe_stop", "protect", "error"]):
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="servos.center"))

        elif any(key in intent_type for key in ["explore", "curious", "search"]):
            actions.append(PlanAction(tool="motors.forward", args={"duration": 2.0}))
            actions.append(PlanAction(tool="servos.random"))

        elif any(key in intent_type for key in ["inspect", "investigate", "sound", "image", "attention", "human", "interact"]):
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="servos.look", args={"x": -0.5, "y": 0.0}))
            actions.append(PlanAction(tool="servos.look", args={"x": 0.5, "y": 0.0}))

        elif any(key in intent_type for key in ["turn_left", "rotate_left"]):
            actions.append(PlanAction(tool="motors.turn_left", args={"duration": 1.5}))

        elif any(key in intent_type for key in ["turn_right", "rotate_right"]):
            actions.append(PlanAction(tool="motors.turn_right", args={"duration": 1.5}))

        elif any(key in intent_type for key in ["backward", "retreat"]):
            actions.append(PlanAction(tool="motors.backward", args={"duration": 2.0}))

        elif any(key in intent_type for key in ["rest", "sleep", "idle", "observe", "wait", "monitor"]):
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="servos.center"))

        else:
            # Intenção desconhecida → comportamento conservador
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="servos.center"))

        return ExecutablePlan(
            plan_id="plan_static",
            actions=actions,
            policy={
                "allow_base_motion": True,
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
