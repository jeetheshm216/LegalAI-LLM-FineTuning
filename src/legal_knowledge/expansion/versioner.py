"""Document version detector and temporal manager for Indian statutes."""

import sqlite3
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from ..models import TemporalStatus, IndianLegalDocument
from ..indexing.database import IndianLegalDatabaseManager


class DocumentVersionManager:
    """Ensures non-destructive legal versioning. Never destroys historical legal text."""

    def __init__(self, db_manager: IndianLegalDatabaseManager):
        self.db = db_manager

    def evaluate_document_version(
        self,
        act_prefix: str,
        new_content_hash: str,
        amendment_date: Optional[str] = None
    ) -> Tuple[str, TemporalStatus, bool, Optional[str]]:
        """
        Evaluates an Act's version state against the existing database.
        Returns:
            (version_id: str, temporal_status: TemporalStatus, is_new_version: bool, note: Optional[str])
        """
        now_date = amendment_date or datetime.now().strftime("%Y-%m-%d")

        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            # Check existing document by act_prefix
            cursor.execute(
                "SELECT document_id, temporal_status, effective_from, effective_until "
                "FROM indian_legal_documents WHERE act_prefix = ?",
                (act_prefix,)
            )
            existing_doc = cursor.fetchone()

            if not existing_doc:
                # First time this Act is being ingested
                return "1.0-ORIGINAL-ENACTMENT", TemporalStatus.CURRENT, False, "Original enactment"

            # Check if an indexed record with this content hash already exists in state tracker
            cursor.execute(
                "SELECT content_hash FROM indian_corpus_ingestion_state WHERE act_prefix = ? AND status = 'INDEXED'",
                (act_prefix,)
            )
            state_row = cursor.fetchone()
            if state_row and state_row["content_hash"] == new_content_hash:
                # Identical content already present
                return "1.0-CURRENT", TemporalStatus.CURRENT, False, "Identical content already indexed"

            # Hash differs: Content has been amended or updated
            # Determine new version number
            cursor.execute(
                "SELECT COUNT(*) FROM indian_legal_documents WHERE act_prefix LIKE ?",
                (f"{act_prefix}%",)
            )
            version_count = cursor.fetchone()[0]
            new_version = f"{version_count + 1}.0-AMENDMENT-{now_date}"

            # Preserve the old document as AMENDED / HISTORICAL
            cursor.execute(
                "UPDATE indian_legal_documents SET temporal_status = ?, effective_until = ? "
                "WHERE act_prefix = ? AND temporal_status = ?",
                (TemporalStatus.AMENDED.value, now_date, act_prefix, TemporalStatus.CURRENT.value)
            )

            # Also update old chunks' temporal status
            cursor.execute(
                "UPDATE indian_legal_chunks SET temporal_status = ?, effective_until = ? "
                "WHERE act_prefix = ? AND temporal_status = ?",
                (TemporalStatus.AMENDED.value, now_date, act_prefix, TemporalStatus.CURRENT.value)
            )
            conn.commit()

            note = f"Amended version {new_version} created; preceding version preserved with effective_until={now_date}"
            return new_version, TemporalStatus.CURRENT, True, note
