from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from project_eva.core.config import (
    PAN_SERVO_PIN,
    TILT_SERVO_PIN,
    PAN_CENTER,
    TILT_CENTER,
    SERVO_MIN,
    SERVO_MAX,
    INVERT_PAN,
    INVERT_TILT,
)
from time import sleep
import threading
import random


class PanTiltController:
    def __init__(self):
        self.factory = PiGPIOFactory()

        self.pan_servo = Servo(
            PAN_SERVO_PIN,
            min_pulse_width=0.5 / 1000,
            max_pulse_width=2.5 / 1000,
            pin_factory=self.factory,
        )

        self.tilt_servo = Servo(
            TILT_SERVO_PIN,
            min_pulse_width=0.5 / 1000,
            max_pulse_width=2.5 / 1000,
            pin_factory=self.factory,
        )

        self.servo_min = SERVO_MIN
        self.servo_max = SERVO_MAX

        self.invert_pan = INVERT_PAN
        self.invert_tilt = INVERT_TILT

        self.x_center = PAN_CENTER
        self.y_center = TILT_CENTER

        self.x = self.x_center
        self.y = self.y_center

        self.lock = threading.Lock()

        self._write_servos(self.x, self.y)
        self.detach()

    @property
    def pan_angle(self):
        return self.x

    @property
    def tilt_angle(self):
        return self.y
    
    def _clamp(self, value):
        return max(self.servo_min, min(self.servo_max, value))

    def _apply_axis_inversion(self, x, y):
        pan_value = -x if self.invert_pan else x
        tilt_value = -y if self.invert_tilt else y
        return pan_value, tilt_value

    def _write_servos(self, x, y):
        x = self._clamp(x)
        y = self._clamp(y)

        pan_value, tilt_value = self._apply_axis_inversion(x, y)

        self.pan_servo.value = pan_value
        self.tilt_servo.value = tilt_value

    def detach(self):
        self.pan_servo.detach()
        self.tilt_servo.detach()

    def stop(self):
        self.detach()

    def set_position(self, x, y):
        x = self._clamp(x)
        y = self._clamp(y)

        with self.lock:
            self._write_servos(x, y)
            self.x = x
            self.y = y

    def center(self, smooth=True):
        if smooth:
            self.move_smooth(self.x_center, self.y_center)
        else:
            self.set_position(self.x_center, self.y_center)
            self.detach()

    def move_smooth(self, target_x, target_y, step=0.01, delay=0.02):
        target_x = self._clamp(target_x)
        target_y = self._clamp(target_y)

        if step <= 0:
            step = 0.01

        with self.lock:
            current_x = self.x
            current_y = self.y

        def seq(start, stop, step_value):
            if abs(stop - start) < step_value:
                return [stop]

            points = []
            if start < stop:
                value = start
                while value < stop:
                    points.append(round(value, 3))
                    value += step_value
            else:
                value = start
                while value > stop:
                    points.append(round(value, 3))
                    value -= step_value

            points.append(stop)
            return points

        xs = seq(current_x, target_x, step)
        ys = seq(current_y, target_y, step)

        try:
            for x in xs:
                self._write_servos(x, self.y)
                sleep(delay)

            for y in ys:
                self._write_servos(target_x, y)
                sleep(delay)

            with self.lock:
                self.x = target_x
                self.y = target_y

        finally:
            self.detach()

    def random_move(self):
        x = round(random.uniform(-0.7, 0.7), 2)
        y = round(random.uniform(-0.3, 0.3), 2)
        self.move_smooth(x, y)

    def adjust_tracking(self, error_x, error_y, gain=0.02):
        new_x = self.x - (error_x * gain)
        new_y = self.y + (error_y * gain)
        self.set_position(new_x, new_y)