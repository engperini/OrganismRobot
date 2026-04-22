class FactStore:
    def __init__(self, sqlite_store):
        self.sqlite_store = sqlite_store

    def save_fact(self, key: str, value: str, source: str = "system"):
        self.sqlite_store.insert_fact(key=key, value=value, source=source)
