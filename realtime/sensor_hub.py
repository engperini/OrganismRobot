from core.schemas import RawSensorSnapshot

class SensorHub:
    def __init__(self):
        self.snapshot = RawSensorSnapshot()

    def update(self, **kwargs):
        self.snapshot = self.snapshot.copy(update=kwargs)

    def get(self):
        return self.snapshot
