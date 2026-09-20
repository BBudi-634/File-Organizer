import sqlite3
import time
import uuid
from pathlib import Path

DB_PATH = Path.home() / ".file_organizer" / "history.db"

def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT NOT NULL,
            src TEXT NOT NULL,
            dest TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    """)
    return conn

def new_batch_id() -> str:
    """Generate a unique ID for a group of moves."""
    return uuid.uuid4().hex[:8]

def record_move(batch_id: str, src: str, dest: str) -> None:
    """Record a successful move."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO moves (batch_id, src, dest, timestamp) VALUES (?, ?, ?, ?)",
            (batch_id, str(src), str(dest), time.time()),
        )

def get_last_batch() -> list[tuple[str, str]]:
    """Return (src, dest) pairs from the most recent batch, oldest first."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT batch_id FROM moves ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return []
        batch_id = row[0]
        rows = conn.execute(
            "SELECT src, dest FROM moves WHERE batch_id = ? ORDER BY id ASC",
            (batch_id,),
        ).fetchall()
    return rows

def get_batch_by_id(batch_id: str) -> list[tuple[str, str]]:
    """Return (src, dest) pairs for a specific batch, oldest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT src, dest FROM moves WHERE batch_id = ? ORDER BY id ASC",
            (batch_id,),
        ).fetchall()
    return rows

def list_recent_batches(limit: int = 10) -> list[tuple[str, float, int]]:
    """Return (batch_id, timestamp, move_count) for the most recent batches."""
    with _connect() as conn:
        rows = conn.execute("""
            SELECT batch_id, MAX(timestamp) AS ts, COUNT(*) AS n
            FROM moves
            GROUP BY batch_id
            ORDER BY ts DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return rows