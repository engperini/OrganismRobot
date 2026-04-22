import sqlite3
from pathlib import Path

class SQLiteStore:
    def __init__(self, db="memory.db"):
        Path(db).parent.mkdir(parents=True, exist_ok=True) if "/" in db else None
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS episodes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS errors (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT,
                source TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS policy_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_signature TEXT,
                action_signature TEXT,
                score REAL
            )
        ''')
        self.conn.commit()

    def insert_event(self, data: str):
        self.conn.execute("INSERT INTO events (data) VALUES (?)", (data,))
        self.conn.commit()

    def insert_decision(self, data: str):
        self.conn.execute("INSERT INTO decisions (data) VALUES (?)", (data,))
        self.conn.commit()

    def insert_action(self, data: str):
        self.conn.execute("INSERT INTO actions (data) VALUES (?)", (data,))
        self.conn.commit()

    def insert_episode(self, data: str):
        self.conn.execute("INSERT INTO episodes (data) VALUES (?)", (data,))
        self.conn.commit()

    def insert_error(self, data: str):
        self.conn.execute("INSERT INTO errors (data) VALUES (?)", (data,))
        self.conn.commit()

    def insert_fact(self, key: str, value: str, source: str):
        self.conn.execute(
            "INSERT INTO facts (key, value, source) VALUES (?, ?, ?)",
            (key, value, source),
        )
        self.conn.commit()

    def insert_policy_feedback(self, context_signature: str, action_signature: str, score: float):
        self.conn.execute(
            "INSERT INTO policy_feedback (context_signature, action_signature, score) VALUES (?, ?, ?)",
            (context_signature, action_signature, score),
        )
        self.conn.commit()

    def fetch_recent(self, table: str, limit: int = 10):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()
