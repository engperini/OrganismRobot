# import RPi.GPIO as GPIO


# class Motor:
#     def __init__(self, in1: int, in2: int):
#         self.in1 = in1
#         self.in2 = in2

#         GPIO.setup(self.in1, GPIO.OUT)
#         GPIO.setup(self.in2, GPIO.OUT)

#         self.stop()

#     def forward(self):
#         GPIO.output(self.in1, GPIO.HIGH)
#         GPIO.output(self.in2, GPIO.LOW)

#     def backward(self):
#         GPIO.output(self.in1, GPIO.LOW)
#         GPIO.output(self.in2, GPIO.HIGH)

#     def stop(self):
#         GPIO.output(self.in1, GPIO.LOW)
#         GPIO.output(self.in2, GPIO.LOW)


# from gpiozero import OutputDevice

# class Motor:
#     def __init__(self, in1: int, in2: int):
#         # Cada entrada do motor é um OutputDevice
#         self.in1 = OutputDevice(in1)
#         self.in2 = OutputDevice(in2)

#         self.stop()

#     def forward(self):
#         self.in1.on()
#         self.in2.off()

#     def backward(self):
#         self.in1.off()
#         self.in2.on()

#     def stop(self):
#         self.in1.off()
#         self.in2.off()

import time
from gpiozero import OutputDevice

class Motor:
    def __init__(self, in1: int, in2: int, default_duration: float = 1.0):
        self.in1 = OutputDevice(in1)
        self.in2 = OutputDevice(in2)
        self.default_duration = default_duration
        self.stop()

    def forward(self, duration: float = None):
        """Liga o motor para frente. Usa duration da API ou o default."""
        d = duration if duration is not None else self.default_duration
        self.in1.on()
        self.in2.off()
        time.sleep(d)
        self.stop()

    def backward(self, duration: float = None):
        """Liga o motor para trás. Usa duration da API ou o default."""
        d = duration if duration is not None else self.default_duration
        self.in1.off()
        self.in2.on()
        time.sleep(d)
        self.stop()

    def stop(self):
        """Desliga o motor."""
        self.in1.off()
        self.in2.off()

