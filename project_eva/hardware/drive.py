from project_eva.hardware.motor import Motor


# class RobotCar:
#     def __init__(self, left_motor: Motor, right_motor: Motor):
#         self.left = left_motor
#         self.right = right_motor

#     def forward(self):
#         self.left.forward()
#         self.right.forward()

#     def backward(self):
#         self.left.backward()
#         self.right.backward()

#     def turn_left(self):
#         self.left.stop()
#         self.right.forward()

#     def turn_right(self):
#         self.right.stop()
#         self.left.forward()

#     def rotate_left(self):
#         self.left.backward()
#         self.right.forward()

#     def rotate_right(self):
#         self.left.forward()
#         self.right.backward()

#     def stop(self):
#         self.left.stop()
#         self.right.stop()


class RobotCar:
    def __init__(self, left_motor, right_motor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def forward(self, duration: float = None):
        self.left_motor.forward(duration)
        self.right_motor.forward(duration)

    def backward(self, duration: float = None):
        self.left_motor.backward(duration)
        self.right_motor.backward(duration)

    def turn_left(self, duration: float = None):
        self.right_motor.forward(duration)
        self.left_motor.stop()

    def turn_right(self, duration: float = None):
        self.left_motor.forward(duration)
        self.right_motor.stop()

    def rotate_left(self, duration: float = None):
        self.left_motor.backward(duration)
        self.right_motor.forward(duration)

    def rotate_right(self, duration: float = None):
        self.left_motor.forward(duration)
        self.right_motor.backward(duration)

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
