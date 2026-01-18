import sqlite3
import datetime
from typing import List, Set
from config import DB_PATH

class Storage:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS completed_followups (
                    meeting_id TEXT PRIMARY KEY,
                    completion_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completion_method TEXT
                )
            """)

    def mark_complete(self, meeting_id: str, method: str = "slack"):
        """Marks a meeting as completed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO completed_followups (meeting_id, completion_method) VALUES (?, ?)",
                (meeting_id, method)
            )

    def is_completed(self, meeting_id: str) -> bool:
        """Checks if a meeting is already completed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM completed_followups WHERE meeting_id = ?", (meeting_id,))
            return cursor.fetchone() is not None

    def get_completed_ids(self) -> Set[str]:
        """Returns a set of all completed meeting IDs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT meeting_id FROM completed_followups")
            return {row[0] for row in cursor.fetchall()}

    def cleanup_old_records(self, days: int = 30):
        """Deletes records older than X days."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM completed_followups WHERE completion_timestamp < ?", (cutoff.isoformat(),))
