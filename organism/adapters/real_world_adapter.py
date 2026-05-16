from realtime.distance_loop import read_distance
from realtime.battery_loop import read_battery_pct
from realtime.motor_state_loop import read_motor_state
from realtime.servo_state_loop import read_servo_state
from realtime.error_loop import read_last_error
from realtime.camera_frame_loop import capture_frame_summary


class RealWorldAdapter:
    def __init__(self):
        print("[adapter] RealWorldAdapter initialized")

    def observe(self):
        try:
            return {
                "camera_summary": str(capture_frame_summary()),
                "distance_front_cm": str(read_distance()),
                "battery_pct": str(read_battery_pct()),
                "motor_state": str(read_motor_state()),
                "servo_state": str(read_servo_state()),
                "last_error": str(read_last_error()),
            }

        except Exception as exc:
            return {
                "error": str(exc)
            }
