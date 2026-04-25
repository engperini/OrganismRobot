import RPi.GPIO as GPIO
import sys, tty, termios
from motor import Motor
from controller import RobotCar
from utils import setup_gpio, cleanup_gpio
import config 
import time
command_time = 1  # Tempo para cada comando em segundos

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == "__main__":
    # Configura GPIO conforme definido em config.py
    if config.GPIO_MODE == "BCM":
        GPIO.setmode(GPIO.BCM)
    else:
        GPIO.setmode(GPIO.BOARD)

    setup_gpio()

    left_motor = Motor(**config.LEFT_MOTOR_PINS)
    right_motor = Motor(**config.RIGHT_MOTOR_PINS)
    car = RobotCar(left_motor, right_motor)
    

    print("Controle manual iniciado. Use as setas ↑ ↓ ← →. Pressione 'q' para sair.")

    try:
        while True:
            key = get_key()
            if key == '\x1b':
                next1 = get_key()
                next2 = get_key()
                if next1 == '[':
                    if next2 == 'A':
                        print("Frente")
                        car.forward()
                        time.sleep(command_time)
                        car.stop()
                    elif next2 == 'B':
                        print("Trás")
                        car.backward()
                        time.sleep(command_time)
                        car.stop()
                    elif next2 == 'C':
                        print("Direita")
                        car.turn_right()
                        time.sleep(command_time)
                        car.stop()
                    elif next2 == 'D':
                        print("Esquerda")
                        car.turn_left()
                        time.sleep(command_time)
                        car.stop()

            elif key == 'q':
                print("Encerrando...")
                break
            else:
                car.stop()
    finally:
        car.stop()
        cleanup_gpio()
