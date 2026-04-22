class PerceptorAgent:
    def run(self, snapshot):
        return {
            "summary": "basic perception",
            "distance": snapshot.distance_front_cm,
            "risk_flags": [],
        }
