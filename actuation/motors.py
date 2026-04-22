class Motors:
    def __init__(self):
        self.left_state = "stop"
        self.right_state = "stop"

    def stop(self):
        self.left_state = "stop"
        self.right_state = "stop"
        return {"left_motor_state": self.left_state, "right_motor_state": self.right_state}

    def forward_short(self):
        self.left_state = "forward"
        self.right_state = "forward"
        return {"left_motor_state": self.left_state, "right_motor_state": self.right_state}

    def backward_short(self):
        self.left_state = "backward"
        self.right_state = "backward"
        return {"left_motor_state": self.left_state, "right_motor_state": self.right_state}
