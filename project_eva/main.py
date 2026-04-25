from core.robot_core import RobotCore
from time import sleep

if __name__ == "__main__":
    robot = RobotCore()
    robot.start()

    robot.enable_exploring()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        robot.stop()

