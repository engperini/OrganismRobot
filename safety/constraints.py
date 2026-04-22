from core.config import DISTANCE_BLOCK_THRESHOLD

def is_front_motion_allowed(front_distance_cm):
    if front_distance_cm is None:
        return True
    return front_distance_cm >= DISTANCE_BLOCK_THRESHOLD

def is_battery_ok(battery_pct):
    if battery_pct is None:
        return True
    return battery_pct > 10
