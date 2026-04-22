from actuation.motors import Motors
from actuation.pan_tilt import PanTilt


class ActionRouter:
    def __init__(self, motors: Motors, pan_tilt: PanTilt) -> None:
        self.motors = motors
        self.pan_tilt = pan_tilt

    def dispatch(self, tool: str, args: dict) -> None:
        if tool == "motors.stop":
            self.motors.stop()
            return
        if tool == "motors.forward_short":
            self.motors.forward_short()
            return
        if tool == "motors.backward_short":
            self.motors.backward_short()
            return

        if tool == "pan_tilt.center":
            self.pan_tilt.center()
            return
        if tool == "pan_tilt.look_left":
            self.pan_tilt.look_left()
            return
        if tool == "pan_tilt.look_right":
            self.pan_tilt.look_right()
            return
        if tool == "pan_tilt.explore_step":
            self.pan_tilt.explore_step()
            return

        raise ValueError(f"Unknown tool: {tool}")
