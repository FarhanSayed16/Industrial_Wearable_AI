"""
Industrial Wearable AI — Offline Event Buffer
SQLite-backed queue to store events when the backend is unreachable.
"""
import asyncio
import json
import logging
import sqlite3
from typing import List, Tuple

log = logging.getLogger(__name__)

class OfflineBuffer:
    def __init__(self, db_path: str = "offline_events.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS buffered_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    async def add_events(self, worker_id: str, events: List[dict]):
        """Append a batch of events to the SQLite buffer."""
        async with self._lock:
            def _insert():
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT INTO buffered_events (worker_id, payload) VALUES (?, ?)",
                        (worker_id, json.dumps(events))
                    )
                    conn.commit()
            await asyncio.to_thread(_insert)

    async def get_batch(self, limit: int = 50) -> List[Tuple[int, str, List[dict]]]:
        """Fetch up to `limit` batches of events from the buffer."""
        async with self._lock:
            def _fetch():
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT id, worker_id, payload FROM buffered_events ORDER BY id ASC LIMIT ?", 
                        (limit,)
                    )
                    return [(r[0], r[1], json.loads(r[2])) for r in cursor.fetchall()]
            return await asyncio.to_thread(_fetch)

    async def delete_batch(self, ids: List[int]):
        """Remove successfully posted events from the buffer."""
        if not ids:
            return
        async with self._lock:
            def _delete():
                with sqlite3.connect(self.db_path) as conn:
                    conn.executemany(
                        "DELETE FROM buffered_events WHERE id = ?",
                        [(i,) for i in ids]
                    )
                    conn.commit()
            await asyncio.to_thread(_delete)

    async def get_count(self) -> int:
        """Get total number of buffered batches."""
        async with self._lock:
            def _count():
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM buffered_events")
                    return cursor.fetchone()[0]
            return await asyncio.to_thread(_count)

# Global instance
edge_buffer = OfflineBuffer()
