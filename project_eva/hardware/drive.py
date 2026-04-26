import time
from project_eva.hardware.motor import Motor

class RobotCar:
    def __init__(self, left_motor, right_motor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def forward(self, duration: float = None):
        d = duration if duration is not None else 1.0
        self.left_motor.forward()
        self.right_motor.forward()
        time.sleep(d)
        self.stop()

    def backward(self, duration: float = None):
        d = duration if duration is not None else 1.0
        self.left_motor.backward()
        self.right_motor.backward()
        time.sleep(d)
        self.stop()

    def turn_left(self, duration: float = None):
        d = duration if duration is not None else 1.0
        self.left_motor.stop()
        self.right_motor.forward()
        time.sleep(d)
        self.stop()

    def turn_right(self, duration: float = None):
        d = duration if duration is not None else 1.0
        self.right_motor.stop()
        self.left_motor.forward()
        time.sleep(d)
        self.stop()

    def rotate_left(self, duration: float = None):
        d = duration if duration is not None else 1.0       
        self.left_motor.backward()
        self.right_motor.forward()
        time.sleep(d)
        self.stop()

    def rotate_right(self, duration: float = None):
        d = duration if duration is not None else 1.0
        self.left_motor.forward()
        self.right_motor.backward()
        time.sleep(d)
        self.stop()

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
