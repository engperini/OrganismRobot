from core.logging import get_logger

logger = get_logger("motors")


class Motors:
    def __init__(self) -> None:
        self.left_state = "stop"
        self.right_state = "stop"

    def stop(self) -> None:
        self.left_state = "stop"
        self.right_state = "stop"
        logger.info("motors -> stop")

    def forward_short(self) -> None:
        self.left_state = "forward"
        self.right_state = "forward"
        logger.info("motors -> forward_short")

    def backward_short(self) -> None:
        self.left_state = "backward"
        self.right_state = "backward"
        logger.info("motors -> backward_short")

    def get_states(self) -> tuple[str, str]:
        return self.left_state, self.right_state
