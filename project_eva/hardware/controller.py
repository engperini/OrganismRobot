from motor import Motor

class RobotCar:
    def __init__(self, left_motor: Motor, right_motor: Motor):
        self.left = left_motor
        self.right = right_motor

    def forward(self):
        self.left.forward()
        self.right.forward()

    def backward(self):
        self.left.backward()
        self.right.backward()

    def turn_left(self):
        self.left.stop()
        self.right.forward()

    def turn_right(self):
        self.right.stop()
        self.left.forward()

    def stop(self):
        self.left.stop()
        self.right.stop()
