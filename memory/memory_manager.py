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
