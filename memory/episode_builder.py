class EpisodeBuilder:
    def build(self, thought, result, reflection):
        return {
            "intent": getattr(thought, "intent", None) if thought else None,
            "status": getattr(result, "status", None) if result else None,
            "summary": getattr(reflection, "episode_summary", None) if reflection else None,
        }
