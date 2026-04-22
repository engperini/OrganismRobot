class Retrieval:
    def __init__(self, sqlite_store):
        self.sqlite_store = sqlite_store

    def get_recent_events(self, limit: int = 10):
        return self.sqlite_store.fetch_recent("events", limit)

    def get_recent_episodes(self, limit: int = 10):
        return self.sqlite_store.fetch_recent("episodes", limit)

    def get_recent_errors(self, limit: int = 10):
        return self.sqlite_store.fetch_recent("errors", limit)
