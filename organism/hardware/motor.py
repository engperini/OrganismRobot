class Motor:
    def __init__(self, in1: int, in2: int):
        self.in1_pin = in1
        self.in2_pin = in2
        self.state = "stop"

        try:
            from gpiozero import OutputDevice
            self.in1 = OutputDevice(in1)
            self.in2 = OutputDevice(in2)
            self.real = True
        except Exception as exc:
            print(f"[motor] simulation mode pin {in1}/{in2}: {exc}")
            self.in1 = None
            self.in2 = None
            self.real = False

    def forward(self):
        self.state = "forward"
        if self.real:
            self.in1.off()
            self.in2.on()

    def backward(self):
        self.state = "backward"
        if self.real:
            self.in1.on()
            self.in2.off()

    def stop(self):
        self.state = "stop"
        if self.real:
            self.in1.off()
            self.in2.off()
