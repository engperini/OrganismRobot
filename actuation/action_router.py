from actuation.motors import Motors
from actuation.pan_tilt import PanTilt

class ActionRouter:
    def __init__(self):
        self.motors = Motors()
        self.pan_tilt = PanTilt()

    def dispatch(self, tool: str, args: dict | None = None):
        args = args or {}

        if tool == "motors.stop":
            return self.motors.stop()

        if tool == "motors.forward_short":
            return self.motors.forward_short()

        if tool == "motors.backward_short":
            return self.motors.backward_short()

        if tool == "pan_tilt.center":
            return self.pan_tilt.center()

        if tool == "pan_tilt.look_left":
            return self.pan_tilt.look_left()

        if tool == "pan_tilt.look_right":
            return self.pan_tilt.look_right()

        if tool == "pan_tilt.explore_step":
            return self.pan_tilt.explore_step()

        return {"unhandled_tool": tool, "args": args}
