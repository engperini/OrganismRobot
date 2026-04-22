from core.config import SAFETY
from core.schemas import WorldState, ExecutablePlan


def is_front_blocked(world_state: WorldState) -> bool:
    if world_state.front_distance_cm is None:
        return False
    return world_state.front_distance_cm < SAFETY.min_front_distance_cm


def is_battery_critical(world_state: WorldState) -> bool:
    if world_state.battery_pct is None:
        return False
    return world_state.battery_pct <= SAFETY.critical_battery_pct


def is_action_timeout_valid(plan: ExecutablePlan) -> bool:
    for action in plan.actions:
        if action.timeout_s > SAFETY.max_action_timeout_s:
            return False
    return True
