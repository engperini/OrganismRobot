from memory.retrieval import Retrieval
from memory.episode_builder import EpisodeBuilder


class MemoryManager:
    def __init__(self, sqlite_store, short_term):
        self.sqlite_store = sqlite_store
        self.short_term = short_term
        self.retrieval = Retrieval(sqlite_store)
        self.episode_builder = EpisodeBuilder()

    def persist_event(self, data: str):
        self.sqlite_store.insert_event(data)

    def persist_error(self, data: str):
        self.sqlite_store.insert_error(data)

    def persist_episode(self, thought, result, reflection):
        episode = self.episode_builder.build(thought, result, reflection)
        self.sqlite_store.insert_episode(str(episode))
        return episode

    def remember(self, item):
        self.short_term.add(item)

    def get_recent_context(self, limit=5):
        recent_items = self.short_term.recent(limit)

        compact = []
        for item in recent_items:
            thought = item.get("thought", {}) if isinstance(item, dict) else {}
            result = item.get("result", {}) if isinstance(item, dict) else {}
            reflection = item.get("reflection", {}) if isinstance(item, dict) else {}

            compact.append({
                "intent": thought.get("intent"),
                "intent_type": thought.get("intent_type"),
                "mood": thought.get("mood"),
                "external_message": thought.get("external_message"),
                "result_status": result.get("status"),
                "completed_actions": result.get("completed_actions"),
                "episode_summary": reflection.get("episode_summary"),
                "lesson": reflection.get("lesson"),
            })

        return compact
