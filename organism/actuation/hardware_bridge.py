import os
import platform

from organism.hardware.robot_core import RobotCore


class HardwareBridge:
    def __init__(self):
        self.use_hardware = os.getenv("USE_HARDWARE", "false").lower() == "true"
        self.runtime_mode = self._detect_runtime_mode()
        self.robot = RobotCore()

        print(f"[hardware_bridge] mode={self.runtime_mode} use_hardware={self.use_hardware}")

    def _detect_runtime_mode(self):
        machine = platform.machine().lower()

        if self.use_hardware and ("arm" in machine or "aarch64" in machine):
            return "raspberry_hardware"

        return "pc_simulation"

    def execute(self, action):
        name = action.get("name", "motors.stop")
        args = action.get("args", {}) or {}

        print(f"[hardware_bridge] action={name} args={args}")

        if name == "motors.forward":
            self.robot.move_forward(args.get("duration", 1.0))

        elif name == "motors.backward":
            self.robot.move_backward(args.get("duration", 1.0))

        elif name == "motors.turn_left":
            self.robot.turn_left(args.get("duration", 1.0))

        elif name == "motors.turn_right":
            self.robot.turn_right(args.get("duration", 1.0))

        elif name == "motors.rotate_left":
            self.robot.rotate_left(args.get("duration", 1.0))

        elif name == "motors.rotate_right":
            self.robot.rotate_right(args.get("duration", 1.0))

        elif name == "servos.look":
            self.robot.look(args.get("x", 0.0), args.get("y", 0.0))

        elif name == "servos.random":
            self.robot.random_look()

        elif name == "servos.center":
            self.robot.center()

        else:
            self.robot.stop_base()

        return {
            "runtime_mode": self.runtime_mode,
            "action": name,
            "snapshot": self.robot.get_snapshot(),
        }

    def shutdown(self):
        self.robot.shutdown()
