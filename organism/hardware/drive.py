import time


class RobotDrive:
    def __init__(self, left_motor, right_motor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def forward(self, duration=1.0):
        self.left_motor.forward()
        self.right_motor.forward()
        time.sleep(duration)
        self.stop()

    def backward(self, duration=1.0):
        self.left_motor.backward()
        self.right_motor.backward()
        time.sleep(duration)
        self.stop()

    def turn_left(self, duration=1.0):
        self.left_motor.stop()
        self.right_motor.forward()
        time.sleep(duration)
        self.stop()

    def turn_right(self, duration=1.0):
        self.right_motor.stop()
        self.left_motor.forward()
        time.sleep(duration)
        self.stop()

    def rotate_left(self, duration=1.0):
        self.left_motor.backward()
        self.right_motor.forward()
        time.sleep(duration)
        self.stop()

    def rotate_right(self, duration=1.0):
        self.left_motor.forward()
        self.right_motor.backward()
        time.sleep(duration)
        self.stop()

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
