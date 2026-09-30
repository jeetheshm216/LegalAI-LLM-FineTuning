"""Persistent state tracking for safe, resumable legal corpus expansion."""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import IngestionStatus, DiscoveredAct, IngestionRecord

SCHEMA_STATE_SQL = """
CREATE TABLE IF NOT EXISTS indian_corpus_ingestion_state (
    source_url TEXT PRIMARY KEY,
    act_name TEXT NOT NULL,
    act_prefix TEXT NOT NULL,
    act_number TEXT,
    enactment_year INTEGER,
    status TEXT NOT NULL,
    content_hash TEXT,
    version_id TEXT NOT NULL DEFAULT '1.0',
    chunks_created INTEGER DEFAULT 0,
    last_attempt TEXT,
    last_successful TEXT,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_state_status ON indian_corpus_ingestion_state(status);
CREATE INDEX IF NOT EXISTS idx_state_prefix ON indian_corpus_ingestion_state(act_prefix);
"""


class IngestionStateTracker:
    """Tracks the lifecycle of discovered Indian legal documents to ensure restartability and idempotency."""

    def __init__(self, db_path: str = "data/legalai_indian_legal_knowledge.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_STATE_SQL)
            conn.commit()

    def record_discovered(self, act: DiscoveredAct) -> bool:
        """Registers a discovered Act if not already tracked. Returns True if newly added."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM indian_corpus_ingestion_state WHERE source_url = ?", (act.handle_url,))
            existing = cursor.fetchone()
            if existing:
                return False

            sql = """
            INSERT INTO indian_corpus_ingestion_state (
                source_url, act_name, act_prefix, act_number, enactment_year,
                status, version_id, chunks_created, last_attempt, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, '1.0', 0, ?, NULL)
            """
            cursor.execute(sql, (
                act.handle_url, act.act_name, act.act_id, act.act_number,
                act.enactment_year, IngestionStatus.DISCOVERED.value, now
            ))
            conn.commit()
            return True

    def update_status(
        self,
        source_url: str,
        status: IngestionStatus,
        content_hash: Optional[str] = None,
        chunks_created: int = 0,
        version_id: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Updates document status, content hash, and failure logs."""
        now = datetime.now().isoformat()
        last_succ = now if status == IngestionStatus.INDEXED else None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM indian_corpus_ingestion_state WHERE source_url = ?", (source_url,))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO indian_corpus_ingestion_state (
                    source_url, act_name, act_prefix, status, version_id, chunks_created, last_attempt
                ) VALUES (?, '', '', ?, ?, ?, ?)
                """, (source_url, status.value, version_id or '1.0', chunks_created, now))

            sql = """
            UPDATE indian_corpus_ingestion_state
            SET status = ?,
                content_hash = COALESCE(?, content_hash),
                chunks_created = CASE WHEN ? > 0 THEN ? ELSE chunks_created END,
                version_id = COALESCE(?, version_id),
                last_attempt = ?,
                last_successful = COALESCE(?, last_successful),
                error_message = ?
            WHERE source_url = ?
            """
            cursor.execute(sql, (
                status.value, content_hash, chunks_created, chunks_created,
                version_id, now, last_succ, error_message, source_url
            ))
            conn.commit()

    def get_record(self, source_url: str) -> Optional[IngestionRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indian_corpus_ingestion_state WHERE source_url = ?", (source_url,))
            row = cursor.fetchone()
            if row:
                return IngestionRecord(
                    source_url=row["source_url"],
                    act_name=row["act_name"],
                    act_prefix=row["act_prefix"],
                    status=IngestionStatus(row["status"]),
                    act_number=row["act_number"],
                    enactment_year=row["enactment_year"],
                    content_hash=row["content_hash"],
                    version_id=row["version_id"],
                    chunks_created=row["chunks_created"],
                    last_attempt=row["last_attempt"],
                    last_successful=row["last_successful"],
                    error_message=row["error_message"]
                )
        return None

    def is_already_indexed(self, source_url: str) -> bool:
        rec = self.get_record(source_url)
        return rec is not None and rec.status == IngestionStatus.INDEXED

    def list_by_status(self, status: IngestionStatus) -> List[IngestionRecord]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indian_corpus_ingestion_state WHERE status = ?", (status.value,))
            rows = cursor.fetchall()
            for row in rows:
                results.append(IngestionRecord(
                    source_url=row["source_url"],
                    act_name=row["act_name"],
                    act_prefix=row["act_prefix"],
                    status=IngestionStatus(row["status"]),
                    act_number=row["act_number"],
                    enactment_year=row["enactment_year"],
                    content_hash=row["content_hash"],
                    version_id=row["version_id"],
                    chunks_created=row["chunks_created"],
                    last_attempt=row["last_attempt"],
                    last_successful=row["last_successful"],
                    error_message=row["error_message"]
                ))
        return results

    def get_counts(self) -> Dict[str, int]:
        counts = {s.value: 0 for s in IngestionStatus}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM indian_corpus_ingestion_state GROUP BY status")
            for row in cursor.fetchall():
                counts[row[0]] = row[1]
        return counts
