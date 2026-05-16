import asyncio

from realtime.distance_loop import read_distance
from realtime.battery_loop import read_battery_pct
from realtime.motor_state_loop import read_motor_state
from realtime.servo_state_loop import read_servo_state
from realtime.error_loop import read_last_error
from realtime.camera_frame_loop import capture_frame_summary


class RealWorldAdapter:
    def __init__(self):
        print("[adapter] RealWorldAdapter initialized")

    def _run_async(self, coro):
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    def observe(self):
        try:
            camera_summary = self._run_async(
                capture_frame_summary()
            )

            distance = self._run_async(
                read_distance()
            )

            battery = self._run_async(
                read_battery_pct()
            )

            motor_state = self._run_async(
                read_motor_state()
            )

            servo_state = self._run_async(
                read_servo_state()
            )

            last_error = self._run_async(
                read_last_error()
            )

            return {
                "camera_summary": camera_summary,
                "distance_front_cm": distance,
                "battery_pct": battery,
                "motor_state": motor_state,
                "servo_state": servo_state,
                "last_error": last_error,
            }

        except Exception as exc:
            return {
                "adapter_error": str(exc)
            }
