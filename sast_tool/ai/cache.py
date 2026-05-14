import sqlite3
import hashlib
import json
from pathlib import Path

class AICache:
    def __init__(self, db_path=".ai_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _generate_key(self, rule_id, snippet):
        # Key based on rule and code context as per roadmap
        data = f"{rule_id}:{snippet}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get(self, rule_id, snippet):
        key = self._generate_key(rule_id, snippet)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT response FROM cache WHERE key = ?", (key,)).fetchone()
            return json.loads(row[0]) if row else None

    def set(self, rule_id, snippet, response):
        key = self._generate_key(rule_id, snippet)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO cache (key, response) VALUES (?, ?)", 
                         (key, json.dumps(response)))