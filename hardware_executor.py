# hardware_executor.py


from project_eva.core.robot_core import RobotCore

robot = RobotCore()
robot.start()
def execute_action(action: str, params: dict | None = None):
    duration = params.get("duration") if params else None

    if action == "motors.forward":
        robot.move_forward(duration)
    elif action == "motors.backward":
        robot.move_backward(duration)
    elif action == "motors.stop":
        robot.stop_base()
    elif action == "motors.turn_left":
        robot.turn_left(duration)
    elif action == "motors.turn_right":
        robot.turn_right(duration)
    elif action == "motors.rotate_left":
        robot.rotate_left(duration)
    elif action == "motors.rotate_right":
        robot.rotate_right(duration)
    elif action == "servos.look":
        x = params.get("x", 0.0) if params else 0.0
        y = params.get("y", 0.0) if params else 0.0
        robot.look(x, y)
    elif action == "servos.center":
        robot.servos.center()
    elif action == "servos.random":
        robot.servos.random_move()
