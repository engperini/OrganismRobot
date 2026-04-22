class BodyStateRenderer:
    def compose(self, motor_state: dict | None = None, servo_state: dict | None = None, face_state: dict | None = None, inner_voice: dict | None = None):
        return {
            "motors": motor_state or {},
            "servos": servo_state or {},
            "face": face_state or {},
            "inner_voice": inner_voice or {},
        }
