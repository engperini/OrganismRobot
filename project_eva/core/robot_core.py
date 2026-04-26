import threading
import time
import RPi.GPIO as GPIO

from core.schemas import RawSensorSnapshot

from project_eva.hardware.servos import PanTiltController
from project_eva.hardware.motor import Motor
from project_eva.hardware.drive import RobotCar
from project_eva.core.config import (
    LEFT_MOTOR_IN1,
    LEFT_MOTOR_IN2,
    RIGHT_MOTOR_IN1,
    RIGHT_MOTOR_IN2,
)


from project_eva.core.config import GPIO_MODE

if GPIO_MODE.upper() == "BCM":
    GPIO.setmode(GPIO.BCM)
elif GPIO_MODE.upper() == "BOARD":
    GPIO.setmode(GPIO.BOARD)
else:
    raise ValueError("GPIO_MODE inválido")

GPIO.setwarnings(False)



class RobotCore:
    def __init__(self,default_duration: float = 1.0):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.servos = PanTiltController()

        self.left_motor = Motor(LEFT_MOTOR_IN1, LEFT_MOTOR_IN2)
        self.right_motor = Motor(RIGHT_MOTOR_IN1, RIGHT_MOTOR_IN2)
        self.base = RobotCar(self.left_motor, self.right_motor)

        self.default_duration = default_duration

        self.running = True
        self.exploring = False

        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.last_snapshot = RawSensorSnapshot(
            left_motor_state="stop",
            right_motor_state="stop",
            servo_pan_deg=0,
            servo_tilt_deg=0,
            battery_pct=None,
            last_error=None
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.base.stop()
        self.servos.stop()
        GPIO.cleanup()

    # -------------------------
    # LOOP CENTRAL
    # -------------------------

    def loop(self):
        while self.running:
            if self.exploring:
                self.servos.random_move()
                time.sleep(1)
                self.last_snapshot.servo_pan_deg = self.servos.pan_angle
                self.last_snapshot.servo_tilt_deg = self.servos.tilt_angle

            else:
                time.sleep(0.2)

    # -------------------------
    # CONTROLES EXISTENTES
    # -------------------------

    def enable_exploring(self):
        self.exploring = True

    def disable_exploring(self):
        self.exploring = False

    def snapshot(self) -> RawSensorSnapshot:
        return self.last_snapshot


    def look(self, x, y):
        self.servos.move_smooth(x, y)
        self.last_snapshot.servo_pan_deg = self.servos.pan_angle
        self.last_snapshot.servo_tilt_deg = self.servos.tilt_angle


    # -------------------------
    # NOVOS CONTROLES DA BASE
    # -------------------------

    def move_forward(self, duration: float = None):
        d = duration if duration is not None else self.default_duration
        self.base.forward(d)
        self.last_snapshot.left_motor_state = "forward"
        self.last_snapshot.right_motor_state = "forward"


    def move_backward(self, duration: float = None):
        d = duration if duration is not None else self.default_duration
        self.base.backward(d)
        self.last_snapshot.left_motor_state = "backward"
        self.last_snapshot.right_motor_state = "backward"

    def turn_left(self, duration: float = None):
        d = duration if duration is not None else self.default_duration
        self.base.turn_left(d)

    def turn_right(self, duration: float = None):
        d = duration if duration is not None else self.default_duration
        self.base.turn_right(d)

    def rotate_left(self, duration: float = None):
        d = duration if duration is not None else self.default_duration
        self.base.rotate_left(d)

    def rotate_right(self, duration: float = None):
        d = duration if duration is not None else self.default_duration
        self.base.rotate_right(d)

    
    def stop_base(self):
        """Parada imediata da base (motores)."""
        self.base.stop()