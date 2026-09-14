"""
src/case_rag/index.py

Isolated SQLite and FTS5 storage index for Case Document RAG.
Stores case documents, page-aware chunks, FTS5 lexical index, and dense vector embeddings.
MANDATORY INVARIANT: All queries and retrievals are strictly filtered by case_id.
"""

import os
import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .models import CaseDocument, DocumentChunk


class CaseRAGIndex:
    """Manages case document storage, FTS5 lexical indexing, and dense vector embeddings."""

    def __init__(self, db_path: str = "data/legalai_case_rag.db"):
        self.db_path = Path(db_path)
        os.makedirs(self.db_path.parent, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Creates isolated tables for case documents, chunks, and FTS5 index."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_documents (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            document_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size TEXT,
            uploaded_date TEXT,
            status TEXT NOT NULL,
            pages INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_chunks (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            document_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            metadata_json TEXT,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(document_id) REFERENCES case_documents(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_chunks_case_id ON case_chunks(case_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_chunks_doc_id ON case_chunks(document_id);")

        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS case_chunks_fts USING fts5(
            id UNINDEXED,
            case_id,
            document_id,
            document_name,
            page_number UNINDEXED,
            text,
            tokenize = 'porter unicode61'
        );
        """)

        conn.commit()
        conn.close()

    def register_document(self, doc: CaseDocument) -> None:
        """Registers or updates a case document record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO case_documents (
                id, case_id, filename, document_type, file_path, file_size,
                uploaded_date, status, pages
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.id, doc.case_id, doc.filename, doc.category, doc.storage_path,
            doc.file_size, doc.uploaded_date, doc.status, doc.pages
        ))
        conn.commit()
        conn.close()

    def update_document_status(self, document_id: str, status: str) -> None:
        """Updates indexing status of a document."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE case_documents SET status = ? WHERE id = ?", (status, document_id))
        conn.commit()
        conn.close()

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: Optional[np.ndarray] = None) -> None:
        """Stores chunks into relational table and FTS5 index atomically."""
        if not chunks:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            for idx, chunk in enumerate(chunks):
                emb_blob = embeddings[idx].astype(np.float32).tobytes() if embeddings is not None else None
                meta_str = json.dumps(chunk.metadata)

                # Delete if exists to prevent duplicates
                cursor.execute("DELETE FROM case_chunks WHERE id = ?", (chunk.chunk_id,))
                cursor.execute("DELETE FROM case_chunks_fts WHERE id = ?", (chunk.chunk_id,))

                cursor.execute("""
                    INSERT INTO case_chunks (
                        id, case_id, document_id, document_name, document_type,
                        page_number, chunk_index, text, metadata_json, embedding
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.case_id, chunk.document_id, chunk.document_name,
                    chunk.document_type, chunk.page_number, chunk.chunk_index, chunk.text,
                    meta_str, emb_blob
                ))

                cursor.execute("""
                    INSERT INTO case_chunks_fts (id, case_id, document_id, document_name, page_number, text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.case_id, chunk.document_id, chunk.document_name,
                    str(chunk.page_number), chunk.text
                ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_chunks_for_case(self, case_id: str) -> List[Dict[str, Any]]:
        """Returns all chunks for a specific case with their embeddings."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, case_id, document_id, document_name, document_type,
                   page_number, chunk_index, text, metadata_json, embedding
            FROM case_chunks
            WHERE case_id = ?
            ORDER BY document_id, page_number, chunk_index
        """, (case_id,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            emb = None
            if r["embedding"]:
                emb = np.frombuffer(r["embedding"], dtype=np.float32)
            results.append({
                "chunk_id": r["id"],
                "case_id": r["case_id"],
                "document_id": r["document_id"],
                "document_name": r["document_name"],
                "document_type": r["document_type"],
                "page_number": r["page_number"],
                "chunk_index": r["chunk_index"],
                "text": r["text"],
                "metadata": json.loads(r["metadata_json"]) if r["metadata_json"] else {},
                "embedding": emb,
            })
        return results

    def count_chunks_for_case(self, case_id: str) -> int:
        """Returns number of indexed chunks for a case."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM case_chunks WHERE case_id = ?", (case_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def delete_document(self, document_id: str) -> None:
        """Removes a document and its chunks from index."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM case_documents WHERE id = ?", (document_id,))
        cursor.execute("DELETE FROM case_chunks WHERE document_id = ?", (document_id,))
        cursor.execute("DELETE FROM case_chunks_fts WHERE document_id = ?", (document_id,))
        conn.commit()
        conn.close()
