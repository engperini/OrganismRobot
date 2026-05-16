import asyncio
import os
import platform

from organism.sensors.distance_sensor import read_distance
from organism.sensors.battery_sensor import read_battery_pct
from organism.sensors.motor_state_sensor import read_motor_state
from organism.sensors.servo_state_sensor import read_servo_state
from organism.sensors.error_sensor import read_last_error
from organism.sensors.camera_sensor import capture_frame_summary


class RealWorldAdapter:
    def __init__(self):
        self.use_hardware = os.getenv("USE_HARDWARE", "false").lower() == "true"
        self.runtime_mode = self._detect_runtime_mode()

        print(f"[adapter] RealWorldAdapter initialized mode={self.runtime_mode}")

    def _detect_runtime_mode(self):
        machine = platform.machine().lower()

        if self.use_hardware and ("arm" in machine or "aarch64" in machine):
            return "raspberry_hardware"

        return "pc_simulation"

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
            camera_summary = self._run_async(capture_frame_summary())
            distance = self._run_async(read_distance())
            battery = self._run_async(read_battery_pct())
            motor_state = self._run_async(read_motor_state())
            servo_state = self._run_async(read_servo_state())
            last_error = self._run_async(read_last_error())

            return {
                "runtime_mode": self.runtime_mode,
                "use_hardware": self.use_hardware,
                "camera_summary": camera_summary,
                "distance_front_cm": distance,
                "battery_pct": battery,
                "motor_state": motor_state,
                "servo_state": servo_state,
                "last_error": last_error,
            }

        except Exception as exc:
            return {
                "runtime_mode": self.runtime_mode,
                "use_hardware": self.use_hardware,
                "adapter_error": str(exc),
            }
