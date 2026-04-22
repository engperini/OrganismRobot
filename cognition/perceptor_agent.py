from core.schemas import Perception

class PerceptorAgent:
    def run(self, snapshot) -> Perception:
        risk_flags = []
        attention_candidates = []
        novelty_hints = []

        if snapshot.distance_front_cm is not None and snapshot.distance_front_cm < 20:
            risk_flags.append("front_blocked")
            attention_candidates.append("front_obstacle")

        if snapshot.camera_summary:
            attention_candidates.append("camera_scene")

        if snapshot.last_error:
            risk_flags.append("critical_error")

        summary_parts = [
            f"front_distance={snapshot.distance_front_cm}",
            f"battery={snapshot.battery_pct}",
            f"camera={snapshot.camera_summary}",
            f"audio={snapshot.audio_summary}",
        ]

        return Perception(
            summary="; ".join(summary_parts),
            risk_flags=risk_flags,
            attention_candidates=attention_candidates,
            novelty_hints=novelty_hints,
        )
