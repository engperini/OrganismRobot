class PanTilt:
    def __init__(self):
        self.pan = 0.0
        self.tilt = 0.0
        self._explore_dir = 1

    def center(self):
        self.pan = 0.0
        self.tilt = 0.0
        return {"servo_pan_deg": self.pan, "servo_tilt_deg": self.tilt}

    def look_left(self):
        self.pan = -20.0
        return {"servo_pan_deg": self.pan, "servo_tilt_deg": self.tilt}

    def look_right(self):
        self.pan = 20.0
        return {"servo_pan_deg": self.pan, "servo_tilt_deg": self.tilt}

    def explore_step(self):
        self.pan += 10.0 * self._explore_dir
        if self.pan >= 30.0:
            self._explore_dir = -1
        elif self.pan <= -30.0:
            self._explore_dir = 1
        return {"servo_pan_deg": self.pan, "servo_tilt_deg": self.tilt}
