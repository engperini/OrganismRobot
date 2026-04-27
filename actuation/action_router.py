from actuation.motors import Motors
from actuation.pan_tilt import PanTilt
from hardware_executor import execute_action
from core.config import settings


class ActionRouter:
    def __init__(self):
        self.motors = Motors()
        self.pan_tilt = PanTilt()
        self.use_hardware = settings.USE_HARDWARE
        print(f"[ActionRouter] USE_HARDWARE={self.use_hardware}")

    def dispatch(self, tool: str, args: dict | None = None):
        args = args or {}

        if self.use_hardware:
            try:
                return execute_action(tool, args)
            except Exception as exc:
                print(f"[ActionRouter] erro no hardware, fallback simulação: {exc}")

        # Simulação - aliases dos nomes reais atuais
        if tool == "motors.forward":
            return self.motors.forward_short()

        if tool == "motors.backward":
            return self.motors.backward_short()

        if tool == "servos.center":
            return self.pan_tilt.center()

        if tool == "servos.random":
            return self.pan_tilt.explore_step()

        # Simulação - nomes antigos mantidos
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
