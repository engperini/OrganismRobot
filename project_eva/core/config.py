# config.py
# Aqui você centraliza todas as definições de hardware

# Modo de numeração dos pinos (BCM ou BOARD)
GPIO_MODE = "BCM"

# Definição dos pinos dos motores

LEFT_MOTOR_IN1 = 22 #22
LEFT_MOTOR_IN2 = 23 #23
RIGHT_MOTOR_IN1 = 17 #17 #19
RIGHT_MOTOR_IN2 = 18 #18 #26


PAN_SERVO_PIN = 12
TILT_SERVO_PIN = 13

PAN_CENTER = -0.2
TILT_CENTER = 0.3

SERVO_MIN = -0.5
SERVO_MAX = 0.5

INVERT_PAN = False
INVERT_TILT = False
