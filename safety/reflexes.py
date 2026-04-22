from core.schemas import PlanAction, ExecutablePlan


def emergency_stop_plan(reason: str = "emergency_stop") -> ExecutablePlan:
    return ExecutablePlan(
        plan_id=f"reflex_{reason}",
        actions=[
            PlanAction(tool="motors.stop", args={}, timeout_s=1.0),
        ],
        policy={"origin": "reflex", "reason": reason},
        expression={"mood": "sleepy", "face_mode": "sleepy"},
        voice_hint="Melhor parar agora.",
        store_memory=True,
        memory_hint=f"Emergency reflex triggered: {reason}",
    )
