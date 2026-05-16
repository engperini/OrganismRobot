from dataclasses import dataclass

from organism.hardware.config import (
    LEFT_MOTOR_IN1,
    LEFT_MOTOR_IN2,
    RIGHT_MOTOR_IN1,
    RIGHT_MOTOR_IN2,
)
from organism.hardware.motor import Motor
from organism.hardware.drive import RobotDrive
from organism.hardware.servos import PanTilt


@dataclass
class RobotSnapshot:
    left_motor_state: str = "stop"
    right_motor_state: str = "stop"
    servo_pan_deg: float = 0.0
    servo_tilt_deg: float = 0.0
    last_error: str | None = None


class RobotCore:
    def __init__(self):
        print("[robot_core] initializing")

        self.left_motor = Motor(LEFT_MOTOR_IN1, LEFT_MOTOR_IN2)
        self.right_motor = Motor(RIGHT_MOTOR_IN1, RIGHT_MOTOR_IN2)
        self.drive = RobotDrive(self.left_motor, self.right_motor)
        self.servos = PanTilt()

        self.snapshot = RobotSnapshot()

    def _duration(self, duration):
        try:
            return max(0.1, min(float(duration or 1.0), 2.0))
        except Exception:
            return 1.0

    def stop_base(self):
        self.drive.stop()
        self.snapshot.left_motor_state = "stop"
        self.snapshot.right_motor_state = "stop"

    def move_forward(self, duration=None):
        self.drive.forward(self._duration(duration))
        self.snapshot.left_motor_state = "forward"
        self.snapshot.right_motor_state = "forward"
        self.stop_base()

    def move_backward(self, duration=None):
        self.drive.backward(self._duration(duration))
        self.snapshot.left_motor_state = "backward"
        self.snapshot.right_motor_state = "backward"
        self.stop_base()

    def turn_left(self, duration=None):
        self.drive.turn_left(self._duration(duration))
        self.snapshot.left_motor_state = "turn_left"
        self.snapshot.right_motor_state = "turn_left"
        self.stop_base()

    def turn_right(self, duration=None):
        self.drive.turn_right(self._duration(duration))
        self.snapshot.left_motor_state = "turn_right"
        self.snapshot.right_motor_state = "turn_right"
        self.stop_base()

    def rotate_left(self, duration=None):
        self.drive.rotate_left(self._duration(duration))
        self.snapshot.left_motor_state = "rotate_left"
        self.snapshot.right_motor_state = "rotate_left"
        self.stop_base()

    def rotate_right(self, duration=None):
        self.drive.rotate_right(self._duration(duration))
        self.snapshot.left_motor_state = "rotate_right"
        self.snapshot.right_motor_state = "rotate_right"
        self.stop_base()

    def look(self, x=0.0, y=0.0):
        self.servos.look(x, y)
        self.snapshot.servo_pan_deg = self.servos.x
        self.snapshot.servo_tilt_deg = self.servos.y

    def center(self):
        self.servos.center()
        self.snapshot.servo_pan_deg = self.servos.x
        self.snapshot.servo_tilt_deg = self.servos.y

    def random_look(self):
        self.servos.random_move()
        self.snapshot.servo_pan_deg = self.servos.x
        self.snapshot.servo_tilt_deg = self.servos.y

    def get_snapshot(self):
        return {
            "left_motor_state": self.snapshot.left_motor_state,
            "right_motor_state": self.snapshot.right_motor_state,
            "servo_pan_deg": self.snapshot.servo_pan_deg,
            "servo_tilt_deg": self.snapshot.servo_tilt_deg,
            "last_error": self.snapshot.last_error,
        }

    def shutdown(self):
        self.stop_base()
        self.servos.stop()
