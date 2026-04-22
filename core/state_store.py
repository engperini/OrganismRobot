from core.schemas import WorldState
from threading import Lock

class StateStore:
    def __init__(self):
        self._lock = Lock()
        self._state = WorldState()

    def get(self) -> WorldState:
        with self._lock:
            return self._state

    def update(self, **kwargs):
        with self._lock:
            self._state = self._state.copy(update=kwargs)
