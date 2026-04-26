

import time
from gpiozero import OutputDevice

class Motor:
    def __init__(self, in1: int, in2: int, default_duration: float = 1.0):
        self.in1 = OutputDevice(in1)
        self.in2 = OutputDevice(in2)
        self.default_duration = default_duration
        self.stop()

    def backward(self, duration: float = None):
        """Liga o motor para frente. Usa duration da API ou o default."""
        d = duration if duration is not None else self.default_duration
        self.in1.on()
        self.in2.off()
      

    def forward(self, duration: float = None):
        """Liga o motor para trás. Usa duration da API ou o default."""
        d = duration if duration is not None else self.default_duration
        self.in1.off()
        self.in2.on()
  

    def stop(self):
        """Desliga o motor."""
        self.in1.off()
        self.in2.off()

