import sqlite3

class SQLiteStore:
    def __init__(self, db="memory.db"):
        self.conn = sqlite3.connect(db)
        self._init_db()

    def _init_db(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, data TEXT)")
