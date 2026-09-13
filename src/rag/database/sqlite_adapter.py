"""SQLite + FTS5 + Vector Cosine Operational Store for LegalAI RAG MVP."""

import sqlite3
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from .base import BaseLegalDatabase


class SQLiteLegalDatabase(BaseLegalDatabase):
    """Operational relational + vector database implementing canonical LegalAI RAG schema."""

    def __init__(self, db_path: str, vector_dim: int = 1024):
        self.db_path = db_path
        self.vector_dim = vector_dim
        self._conn = None
        self.initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def initialize_schema(self) -> None:
        """Initializes tables, FTS5 virtual tables, and indexes."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            
            # Ingestion Runs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL DEFAULT 'RUNNING',
                    corpus_version TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    vector_dimension INTEGER NOT NULL,
                    total_documents_ingested INTEGER DEFAULT 0,
                    total_sections_extracted INTEGER DEFAULT 0,
                    total_chunks_created INTEGER DEFAULT 0,
                    error_log TEXT
                )
            """)

            # Legal Sources
            cur.execute("""
                CREATE TABLE IF NOT EXISTS legal_sources (
                    source_id TEXT PRIMARY KEY,
                    official_domain TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL UNIQUE,
                    pdf_download_url TEXT,
                    publication_authority TEXT NOT NULL,
                    acquisition_method TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    retrieval_timestamp TEXT NOT NULL,
                    verification_status TEXT NOT NULL DEFAULT 'VERIFIED_OFFICIAL_GAZETTE',
                    notes TEXT
                )
            """)

            # Legal Documents
            cur.execute("""
                CREATE TABLE IF NOT EXISTS legal_documents (
                    document_id TEXT PRIMARY KEY,
                    source_id TEXT REFERENCES legal_sources(source_id),
                    act_name TEXT NOT NULL,
                    act_number TEXT NOT NULL,
                    act_prefix TEXT NOT NULL UNIQUE,
                    act_type TEXT NOT NULL,
                    enactment_date TEXT NOT NULL,
                    commencement_date TEXT NOT NULL,
                    commencement_authority TEXT NOT NULL,
                    document_version TEXT NOT NULL DEFAULT '1.0-ORIGINAL-ENACTMENT',
                    jurisdiction TEXT NOT NULL DEFAULT 'INDIA_CENTRAL',
                    language TEXT NOT NULL DEFAULT 'EN',
                    is_current INTEGER NOT NULL DEFAULT 1,
                    total_sections INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Legal Sections
            cur.execute("""
                CREATE TABLE IF NOT EXISTS legal_sections (
                    section_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES legal_documents(document_id),
                    act_prefix TEXT NOT NULL,
                    section_number TEXT NOT NULL,
                    section_title TEXT NOT NULL,
                    chapter_id TEXT NOT NULL,
                    chapter_title TEXT NOT NULL,
                    full_text TEXT NOT NULL,
                    effective_from TEXT NOT NULL,
                    effective_to TEXT,
                    is_current INTEGER NOT NULL DEFAULT 1,
                    amendment_date TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE (document_id, section_number)
                )
            """)

            # Legal Chunks
            cur.execute("""
                CREATE TABLE IF NOT EXISTS legal_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    section_id TEXT NOT NULL REFERENCES legal_sections(section_id),
                    parent_section_id TEXT NOT NULL,
                    act_name TEXT NOT NULL,
                    act_number TEXT NOT NULL,
                    act_type TEXT NOT NULL,
                    act_prefix TEXT NOT NULL,
                    section_number TEXT NOT NULL,
                    section_title TEXT NOT NULL,
                    chapter TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL DEFAULT 0,
                    total_chunks INTEGER NOT NULL DEFAULT 1,
                    content TEXT NOT NULL,
                    raw_section_text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    publication_date TEXT NOT NULL,
                    effective_from TEXT NOT NULL,
                    effective_to TEXT,
                    is_current INTEGER NOT NULL DEFAULT 1,
                    authority_level TEXT NOT NULL DEFAULT 'PARLIAMENTARY_ACT',
                    content_hash TEXT NOT NULL,
                    embedding_blob BLOB
                )
            """)

            # FTS5 Full-Text Search Virtual Table
            cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS legal_chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    act_name,
                    act_prefix,
                    section_number,
                    section_title,
                    content,
                    tokenize='porter unicode61'
                )
            """)

            # Legal Concordance
            cur.execute("""
                CREATE TABLE IF NOT EXISTS legal_concordance (
                    concordance_id TEXT PRIMARY KEY,
                    legacy_act TEXT NOT NULL,
                    legacy_section TEXT NOT NULL,
                    modern_act TEXT NOT NULL,
                    modern_section TEXT NOT NULL,
                    mapping_type TEXT NOT NULL,
                    authority TEXT NOT NULL,
                    verification_status TEXT NOT NULL DEFAULT 'VERIFIED_STATUTORY_CONCORDANCE',
                    notes TEXT,
                    UNIQUE (legacy_act, legacy_section, modern_act, modern_section)
                )
            """)

            # Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_prefix ON legal_chunks(act_prefix)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_sec ON legal_chunks(section_number)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_dates ON legal_chunks(effective_from, effective_to)")
            conn.commit()

    def record_ingestion_run(
        self,
        corpus_version: str,
        embedding_model: str,
        vector_dimension: int,
        status: str = "RUNNING"
    ) -> str:
        run_id = str(uuid.uuid4())
        started_at = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO ingestion_runs (
                    run_id, started_at, status, corpus_version, embedding_model, vector_dimension
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (run_id, started_at, status, corpus_version, embedding_model, vector_dimension))
            conn.commit()
        return run_id

    def complete_ingestion_run(
        self,
        run_id: str,
        status: str,
        total_docs: int,
        total_sections: int,
        total_chunks: int,
        error_log: Optional[str] = None
    ) -> None:
        completed_at = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE ingestion_runs
                SET status = ?, completed_at = ?, total_documents_ingested = ?,
                    total_sections_extracted = ?, total_chunks_created = ?, error_log = ?
                WHERE run_id = ?
            """, (status, completed_at, total_docs, total_sections, total_chunks, error_log, run_id))
            conn.commit()

    def insert_source(self, source_dict: Dict[str, Any]) -> str:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT source_id FROM legal_sources WHERE source_url = ?", (source_dict["source_url"],))
            row = cur.fetchone()
            if row:
                source_id = row[0]
                cur.execute("""
                    UPDATE legal_sources SET
                        official_domain = ?, source_name = ?, pdf_download_url = ?,
                        publication_authority = ?, acquisition_method = ?, sha256_hash = ?,
                        retrieval_timestamp = ?, verification_status = ?, notes = ?
                    WHERE source_id = ?
                """, (
                    source_dict["official_domain"],
                    source_dict["source_name"],
                    source_dict.get("pdf_download_url"),
                    source_dict["publication_authority"],
                    source_dict["acquisition_method"],
                    source_dict["sha256_hash"],
                    source_dict["retrieval_timestamp"],
                    source_dict.get("verification_status", "VERIFIED_OFFICIAL_GAZETTE"),
                    source_dict.get("notes"),
                    source_id
                ))
            else:
                source_id = source_dict.get("source_id", str(uuid.uuid4()))
                cur.execute("""
                    INSERT INTO legal_sources (
                        source_id, official_domain, source_name, source_url, pdf_download_url,
                        publication_authority, acquisition_method, sha256_hash, retrieval_timestamp,
                        verification_status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source_id,
                    source_dict["official_domain"],
                    source_dict["source_name"],
                    source_dict["source_url"],
                    source_dict.get("pdf_download_url"),
                    source_dict["publication_authority"],
                    source_dict["acquisition_method"],
                    source_dict["sha256_hash"],
                    source_dict["retrieval_timestamp"],
                    source_dict.get("verification_status", "VERIFIED_OFFICIAL_GAZETTE"),
                    source_dict.get("notes")
                ))
            conn.commit()
            return source_id

    def insert_document(self, doc_dict: Dict[str, Any]) -> str:
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT document_id FROM legal_documents WHERE act_prefix = ?", (doc_dict["act_prefix"],))
            row = cur.fetchone()
            if row:
                doc_id = row[0]
                cur.execute("""
                    UPDATE legal_documents SET
                        source_id = ?, act_name = ?, act_number = ?, act_type = ?,
                        enactment_date = ?, commencement_date = ?, commencement_authority = ?,
                        document_version = ?, jurisdiction = ?, language = ?, is_current = ?,
                        total_sections = ?
                    WHERE document_id = ?
                """, (
                    doc_dict.get("source_id"),
                    doc_dict["act_name"],
                    doc_dict["act_number"],
                    doc_dict["act_type"],
                    doc_dict["enactment_date"],
                    doc_dict["commencement_date"],
                    doc_dict["commencement_authority"],
                    doc_dict.get("document_version", "1.0-ORIGINAL-ENACTMENT"),
                    doc_dict.get("jurisdiction", "INDIA_CENTRAL"),
                    doc_dict.get("language", "EN"),
                    1 if doc_dict.get("is_current", True) else 0,
                    doc_dict["total_sections"],
                    doc_id
                ))
            else:
                doc_id = doc_dict.get("document_id", str(uuid.uuid4()))
                cur.execute("""
                    INSERT INTO legal_documents (
                        document_id, source_id, act_name, act_number, act_prefix, act_type,
                        enactment_date, commencement_date, commencement_authority, document_version,
                        jurisdiction, language, is_current, total_sections, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    doc_dict.get("source_id"),
                    doc_dict["act_name"],
                    doc_dict["act_number"],
                    doc_dict["act_prefix"],
                    doc_dict["act_type"],
                    doc_dict["enactment_date"],
                    doc_dict["commencement_date"],
                    doc_dict["commencement_authority"],
                    doc_dict.get("document_version", "1.0-ORIGINAL-ENACTMENT"),
                    doc_dict.get("jurisdiction", "INDIA_CENTRAL"),
                    doc_dict.get("language", "EN"),
                    1 if doc_dict.get("is_current", True) else 0,
                    doc_dict["total_sections"],
                    now
                ))
            conn.commit()
            return doc_id

    def insert_sections(self, sections: List[Dict[str, Any]]) -> int:
        now = datetime.now().isoformat()
        count = 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            for s in sections:
                sec_id = s.get("section_id", f"{s['act_prefix']}_2023_SEC_{s['section_number']}")
                cur.execute("""
                    INSERT INTO legal_sections (
                        section_id, document_id, act_prefix, section_number, section_title,
                        chapter_id, chapter_title, full_text, effective_from, effective_to,
                        is_current, amendment_date, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(document_id, section_number) DO UPDATE SET
                        act_prefix = excluded.act_prefix,
                        section_title = excluded.section_title,
                        chapter_id = excluded.chapter_id,
                        chapter_title = excluded.chapter_title,
                        full_text = excluded.full_text,
                        effective_from = excluded.effective_from,
                        effective_to = excluded.effective_to,
                        is_current = excluded.is_current,
                        amendment_date = excluded.amendment_date
                """, (
                    sec_id,
                    s["document_id"],
                    s["act_prefix"],
                    s["section_number"],
                    s["section_title"],
                    s["chapter_id"],
                    s["chapter_title"],
                    s["text"],
                    s.get("effective_from", "2024-07-01"),
                    s.get("effective_to"),
                    1 if s.get("is_current", True) else 0,
                    s.get("amendment_date"),
                    now
                ))
                count += 1
            conn.commit()
        return count

    def insert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: Optional[np.ndarray] = None
    ) -> int:
        count = 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            for idx, c in enumerate(chunks):
                emb_blob = None
                if embeddings is not None:
                    vec = embeddings[idx].astype(np.float32)
                    emb_blob = vec.tobytes()

                # Insert into relational chunks
                cur.execute("""
                    INSERT INTO legal_chunks (
                        chunk_id, section_id, parent_section_id, act_name, act_number, act_type,
                        act_prefix, section_number, section_title, chapter, chunk_index, total_chunks,
                        content, raw_section_text, source, source_url, publication_date, effective_from,
                        effective_to, is_current, authority_level, content_hash, embedding_blob
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(chunk_id) DO UPDATE SET
                        section_id = excluded.section_id,
                        parent_section_id = excluded.parent_section_id,
                        act_name = excluded.act_name,
                        act_number = excluded.act_number,
                        act_type = excluded.act_type,
                        act_prefix = excluded.act_prefix,
                        section_number = excluded.section_number,
                        section_title = excluded.section_title,
                        chapter = excluded.chapter,
                        chunk_index = excluded.chunk_index,
                        total_chunks = excluded.total_chunks,
                        content = excluded.content,
                        raw_section_text = excluded.raw_section_text,
                        source = excluded.source,
                        source_url = excluded.source_url,
                        publication_date = excluded.publication_date,
                        effective_from = excluded.effective_from,
                        effective_to = excluded.effective_to,
                        is_current = excluded.is_current,
                        authority_level = excluded.authority_level,
                        content_hash = excluded.content_hash,
                        embedding_blob = excluded.embedding_blob
                """, (
                    c["chunk_id"],
                    c.get("section_id", c["parent_section_id"]),
                    c["parent_section_id"],
                    c["act_name"],
                    c["act_number"],
                    c["act_type"],
                    c["act_prefix"],
                    c["section_number"],
                    c["section_title"],
                    c.get("chapter", f"{c.get('chapter_id', '')}: {c.get('chapter_title', '')}"),
                    c.get("chunk_index", 0),
                    c.get("total_chunks", 1),
                    c["content"],
                    c.get("raw_section_text", c["content"]),
                    c.get("source", "India Code"),
                    c.get("source_url", ""),
                    c.get("publication_date", "2023-12-25"),
                    c.get("effective_from", "2024-07-01"),
                    c.get("effective_to"),
                    1 if c.get("is_current", True) else 0,
                    c.get("authority_level", "PARLIAMENTARY_ACT"),
                    c.get("content_hash", ""),
                    emb_blob
                ))

                # Update FTS5 virtual table
                cur.execute("DELETE FROM legal_chunks_fts WHERE chunk_id = ?", (c["chunk_id"],))
                cur.execute("""
                    INSERT INTO legal_chunks_fts (
                        chunk_id, act_name, act_prefix, section_number, section_title, content
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    c["chunk_id"],
                    c["act_name"],
                    c["act_prefix"],
                    c["section_number"],
                    c["section_title"],
                    c["content"]
                ))
                count += 1
            conn.commit()
        return count

    def insert_concordance(self, concordance_list: List[Dict[str, Any]]) -> int:
        count = 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            for m in concordance_list:
                cid = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO legal_concordance (
                        concordance_id, legacy_act, legacy_section, modern_act, modern_section,
                        mapping_type, authority, verification_status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(legacy_act, legacy_section, modern_act, modern_section) DO UPDATE SET
                        mapping_type = excluded.mapping_type,
                        authority = excluded.authority,
                        verification_status = excluded.verification_status,
                        notes = excluded.notes
                """, (
                    cid,
                    m["legacy_act"],
                    m["legacy_section"],
                    m["modern_act"],
                    m["modern_section"],
                    m["mapping_type"],
                    m["authority"],
                    m.get("verification_status", "VERIFIED_STATUTORY_CONCORDANCE"),
                    m.get("notes")
                ))
                count += 1
            conn.commit()
        return count

    def search_lexical(
        self,
        query: str,
        act_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        effective_date: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Executes FTS5 BM25-ranked full-text search with optional temporal and act filters."""
        # Clean query for FTS5 syntax
        clean_q = "".join(c if c.isalnum() or c.isspace() else " " for c in query).strip()
        tokens = [t for t in clean_q.split() if t]
        if not tokens:
            return []

        fts_match = " OR ".join(f'"{t}"' for t in tokens)

        sql = """
            SELECT 
                c.chunk_id, c.act_name, c.act_prefix, c.act_type, c.section_number,
                c.section_title, c.chapter, c.content, c.raw_section_text, c.source,
                c.source_url, c.publication_date, c.effective_from, c.effective_to,
                c.is_current, c.authority_level,
                bm25(legal_chunks_fts) AS bm25_rank
            FROM legal_chunks_fts
            JOIN legal_chunks c ON legal_chunks_fts.chunk_id = c.chunk_id
            WHERE legal_chunks_fts MATCH ?
        """
        params = [fts_match]

        if act_filter:
            sql += " AND (c.act_prefix = ? OR c.act_name LIKE ?)"
            params.extend([act_filter.upper(), f"%{act_filter}%"])

        if section_filter:
            sql += " AND c.section_number = ?"
            params.append(str(section_filter))

        if effective_date:
            sql += " AND c.effective_from <= ? AND (c.effective_to IS NULL OR c.effective_to >= ?)"
            params.extend([effective_date, effective_date])

        sql += " ORDER BY bm25_rank ASC LIMIT ?"
        params.append(limit)

        results = []
        with self._get_connection() as conn:
            cur = conn.execute(sql, params)
            for row in cur.fetchall():
                d = dict(row)
                # Convert BM25 rank (lower is better in FTS5) to positive relevance score
                d["lexical_score"] = float(1.0 / (1.0 + abs(d["bm25_rank"])))
                results.append(d)

        return results

    def search_vector(
        self,
        query_vector: np.ndarray,
        act_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        effective_date: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Executes cosine similarity dense vector search across stored embeddings."""
        q_vec = query_vector.astype(np.float32).flatten()
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        sql = """
            SELECT 
                chunk_id, act_name, act_prefix, act_type, section_number,
                section_title, chapter, content, raw_section_text, source,
                source_url, publication_date, effective_from, effective_to,
                is_current, authority_level, embedding_blob
            FROM legal_chunks
            WHERE embedding_blob IS NOT NULL
        """
        params = []

        if act_filter:
            sql += " AND (act_prefix = ? OR act_name LIKE ?)"
            params.extend([act_filter.upper(), f"%{act_filter}%"])

        if section_filter:
            sql += " AND section_number = ?"
            params.append(str(section_filter))

        if effective_date:
            sql += " AND effective_from <= ? AND (effective_to IS NULL OR effective_to >= ?)"
            params.extend([effective_date, effective_date])

        candidates = []
        with self._get_connection() as conn:
            cur = conn.execute(sql, params)
            for row in cur.fetchall():
                blob = row["embedding_blob"]
                if not blob:
                    continue
                doc_vec = np.frombuffer(blob, dtype=np.float32)
                # Compute cosine similarity
                doc_norm = np.linalg.norm(doc_vec)
                if doc_norm > 0:
                    sim = float(np.dot(q_vec, doc_vec) / doc_norm)
                else:
                    sim = 0.0

                item = dict(row)
                del item["embedding_blob"]
                item["vector_score"] = sim
                candidates.append(item)

        candidates.sort(key=lambda x: x["vector_score"], reverse=True)
        return candidates[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistical metrics for ingestion report."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM legal_sources")
            total_sources = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM legal_documents")
            total_docs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM legal_sections")
            total_sections = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM legal_chunks")
            total_chunks = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM legal_concordance")
            total_concordance = cur.fetchone()[0]

            cur.execute("SELECT act_prefix, COUNT(*) FROM legal_sections GROUP BY act_prefix")
            sections_by_act = dict(cur.fetchall())

            cur.execute("SELECT act_prefix, COUNT(*) FROM legal_chunks GROUP BY act_prefix")
            chunks_by_act = dict(cur.fetchall())

            return {
                "total_sources": total_sources,
                "total_documents": total_docs,
                "total_sections": total_sections,
                "total_chunks": total_chunks,
                "total_concordance": total_concordance,
                "sections_by_act": sections_by_act,
                "chunks_by_act": chunks_by_act
            }
