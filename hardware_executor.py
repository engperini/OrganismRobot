# # hardware_executor.py


# from project_eva.core.robot_core import RobotCore

# robot = RobotCore()
# robot.start()
# def execute_action(action: str, params: dict | None = None):
#     #duration = params.get("duration") if params else None
#     duration = float(params.get("duration")) if params and "duration" in params else None
#     print(f"Executando ação: {action} com duration: {duration}")

#     if action == "motors.forward":
#         robot.move_forward(duration)
#     elif action == "motors.backward":
#         robot.move_backward(duration)
#     elif action == "motors.stop":
#         robot.stop_base()
#     elif action == "motors.turn_left":
#         robot.turn_left(duration)
#     elif action == "motors.turn_right":
#         robot.turn_right(duration)
#     elif action == "motors.rotate_left":
#         robot.rotate_left(duration)
#     elif action == "motors.rotate_right":
#         robot.rotate_right(duration)
#     elif action == "servos.look":
#         x = params.get("x", 0.0) if params else 0.0
#         y = params.get("y", 0.0) if params else 0.0
#         robot.look(x, y)
#     elif action == "servos.center":
#         robot.servos.center()
#     elif action == "servos.random":
#         robot.servos.random_move()


from project_eva.core.robot_core import RobotCore

robot = RobotCore()

robot.start()

def execute_action(action: str, params: dict | None = None):
    duration = float(params.get("duration")) if params and "duration" in params else None
    print(f"Executando ação: {action} com duration: {duration}")

    if action == "motors.forward":
        robot.move_forward(duration)
    elif action == "motors.backward":
        robot.move_backward(duration)
    elif action == "motors.turn_left":
        robot.turn_left(duration)
    elif action == "motors.turn_right":
        robot.turn_right(duration)
    elif action == "motors.rotate_left":
        robot.rotate_left(duration)
    elif action == "motors.rotate_right":
        robot.rotate_right(duration)
    elif action == "motors.stop":
        robot.stop_base()
        robot.last_snapshot.left_motor_state = "stop"
        robot.last_snapshot.right_motor_state = "stop"
    elif action == "servos.center":
        robot.servos.center()
        robot.last_snapshot.servo_pan_deg = 0
        robot.last_snapshot.servo_tilt_deg = 0
    elif action == "servos.random":
        robot.servos.random_move()
        robot.last_snapshot.servo_pan_deg = robot.servos.pan_angle
        robot.last_snapshot.servo_tilt_deg = robot.servos.tilt_angle
    elif action == "servos.look":
        x = params.get("x", 0.0) if params else 0.0
        y = params.get("y", 0.0) if params else 0.0
        robot.look(x, y)
        robot.last_snapshot.servo_pan_deg = x
        robot.last_snapshot.servo_tilt_deg = y

    # 🔑 Retorna o snapshot atualizado como dict
    # return {
    #     "motors": {
    #         "left_motor_state": robot.last_snapshot.left_motor_state,
    #         "right_motor_state": robot.last_snapshot.right_motor_state,
    #     },
    #     "servos": {
    #         "servo_pan_deg": robot.last_snapshot.servo_pan_deg,
    #         "servo_tilt_deg": robot.last_snapshot.servo_tilt_deg,
    #     }
    # }

    if action.startswith("motors."):
        return {
            "left_motor_state": robot.last_snapshot.left_motor_state,
            "right_motor_state": robot.last_snapshot.right_motor_state,
        }
    elif action.startswith("servos."):
        return {
            "servo_pan_deg": robot.servos.x,
            "servo_tilt_deg": robot.servos.y,
        }

