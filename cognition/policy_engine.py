class PolicyEngine:
    def __init__(self):
        self._scores = {}

    def get_score(self, context_signature: str, action_signature: str) -> float:
        return self._scores.get((context_signature, action_signature), 0.0)

    def update_score(self, context_signature: str, action_signature: str, delta: float):
        key = (context_signature, action_signature)
        self._scores[key] = self._scores.get(key, 0.0) + delta
