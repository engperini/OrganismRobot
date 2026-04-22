from core.logging import get_logger

logger = get_logger("pan_tilt")


class PanTilt:
    def __init__(self) -> None:
        self.pan_deg = 0.0
        self.tilt_deg = 0.0
        self._explore_direction = 1

    def center(self) -> None:
        self.pan_deg = 0.0
        self.tilt_deg = 0.0
        logger.info("pan_tilt -> center")

    def look_left(self) -> None:
        self.pan_deg = -20.0
        logger.info("pan_tilt -> look_left")

    def look_right(self) -> None:
        self.pan_deg = 20.0
        logger.info("pan_tilt -> look_right")

    def explore_step(self) -> None:
        self.pan_deg += 10.0 * self._explore_direction

        if self.pan_deg >= 30.0:
            self.pan_deg = 30.0
            self._explore_direction = -1
        elif self.pan_deg <= -30.0:
            self.pan_deg = -30.0
            self._explore_direction = 1

        logger.info("pan_tilt -> explore_step pan=%.1f", self.pan_deg)

    def get_state(self) -> tuple[float, float]:
        return self.pan_deg, self.tilt_deg
