import random
import time

from organism.hardware.config import (
    PAN_SERVO_PIN,
    TILT_SERVO_PIN,
    PAN_CENTER,
    TILT_CENTER,
    SERVO_MIN,
    SERVO_MAX,
    INVERT_PAN,
    INVERT_TILT,
)


class PanTilt:
    def __init__(self):
        self.x = PAN_CENTER
        self.y = TILT_CENTER

        try:
            from gpiozero import Servo
            from gpiozero.pins.pigpio import PiGPIOFactory

            factory = PiGPIOFactory()
            self.pan_servo = Servo(
                PAN_SERVO_PIN,
                min_pulse_width=0.5 / 1000,
                max_pulse_width=2.5 / 1000,
                pin_factory=factory,
            )
            self.tilt_servo = Servo(
                TILT_SERVO_PIN,
                min_pulse_width=0.5 / 1000,
                max_pulse_width=2.5 / 1000,
                pin_factory=factory,
            )
            self.real = True
        except Exception as exc:
            print(f"[servos] simulation mode: {exc}")
            self.pan_servo = None
            self.tilt_servo = None
            self.real = False

    def _clamp(self, value):
        return max(SERVO_MIN, min(SERVO_MAX, float(value)))

    def _write(self, x, y):
        x = self._clamp(x)
        y = self._clamp(y)

        pan_value = -x if INVERT_PAN else x
        tilt_value = -y if INVERT_TILT else y

        if self.real:
            self.pan_servo.value = pan_value
            self.tilt_servo.value = tilt_value

        self.x = x
        self.y = y

    def look(self, x=0.0, y=0.0):
        self._write(x, y)
        time.sleep(0.15)
        self.detach()

    def center(self):
        self.look(PAN_CENTER, TILT_CENTER)

    def random_move(self):
        x = round(random.uniform(-0.5, 0.5), 2)
        y = round(random.uniform(-0.3, 0.3), 2)
        self.look(x, y)

    def detach(self):
        if self.real:
            self.pan_servo.detach()
            self.tilt_servo.detach()

    def stop(self):
        self.detach()
