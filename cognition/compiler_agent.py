from core.schemas import ExecutablePlan, PlanAction

class CompilerAgent:
    def run(self, thought) -> ExecutablePlan:
        actions = []

        if thought.intent == "safe_stop":
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="pan_tilt.center"))

        elif thought.intent == "inspect":
            actions.append(PlanAction(tool="motors.stop"))
            actions.append(PlanAction(tool="pan_tilt.look_left"))
            actions.append(PlanAction(tool="pan_tilt.look_right"))

        elif thought.intent == "explore":
            actions.append(PlanAction(tool="pan_tilt.explore_step"))

        elif thought.intent == "idle":
            actions.append(PlanAction(tool="motors.stop"))

        return ExecutablePlan(
            plan_id="plan_static",
            actions=actions,
            policy={"allow_base_motion": False, "max_duration_s": 3},
            expression={"mood": thought.mood},
            voice_hint=None,
            store_memory=thought.store_candidate,
            memory_hint=thought.intent,
        )
