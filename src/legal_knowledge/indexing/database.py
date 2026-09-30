"""Thread-safe SQLite and FTS5 database manager for Indian legal knowledge."""

import sqlite3
import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from .schema import SCHEMA_SQL
from ..models import (
    IndianLegalDocument,
    IndianLegalChunk,
    IndianDocumentType,
    IndianJurisdictionLevel,
    AuthorityTier,
    TemporalStatus,
    ProvisionType,
    SearchFilter,
    IndianLegalNotification,
    IndianLegalAmendment
)

logger = logging.getLogger("IndianLegalDB")


class IndianLegalDatabaseManager:
    """Manages storage, deduplication, strict namespace indexing, and full-text retrieval."""

    def __init__(self, db_path: str = "data/legalai_indian_legal_knowledge.db"):
        if not os.path.isabs(db_path):
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            self.db_path = os.path.join(repo_root, db_path)
        else:
            self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def upsert_document(self, doc: IndianLegalDocument):
        sql = """
        INSERT INTO indian_legal_documents (
            document_id, title, short_title, document_type, jurisdiction_level, country,
            state, court, bench, judges, act_prefix, act_number, enactment_date,
            commencement_date, legal_domain, authority_tier, temporal_status,
            effective_from, effective_until, amended_by, repealed_by, struck_down_by,
            official_source_url, source_id, content_hash, verification_status, created_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(document_id) DO UPDATE SET
            title=excluded.title,
            short_title=excluded.short_title,
            temporal_status=excluded.temporal_status,
            struck_down_by=excluded.struck_down_by,
            effective_until=excluded.effective_until,
            official_source_url=excluded.official_source_url,
            content_hash=excluded.content_hash,
            verification_status=excluded.verification_status;
        """
        with self._get_connection() as conn:
            conn.execute(sql, (
                doc.document_id, doc.title, getattr(doc, 'short_title', doc.title),
                doc.document_type.value if hasattr(doc.document_type, 'value') else str(doc.document_type),
                doc.jurisdiction_level.value if hasattr(doc.jurisdiction_level, 'value') else str(doc.jurisdiction_level),
                doc.country, doc.state, doc.court, doc.bench, json.dumps(doc.judges),
                doc.act_prefix, doc.act_number, doc.enactment_date, doc.commencement_date,
                doc.legal_domain,
                doc.authority_tier.value if hasattr(doc.authority_tier, 'value') else str(doc.authority_tier),
                doc.temporal_status.value if hasattr(doc.temporal_status, 'value') else str(doc.temporal_status),
                doc.effective_from, doc.effective_until, doc.amended_by, doc.repealed_by, doc.struck_down_by,
                doc.official_source_url, doc.source_id, getattr(doc, 'content_hash', ''),
                getattr(doc, 'verification_status', 'VERIFIED_OFFICIAL'), doc.created_at
            ))
            conn.commit()

    def upsert_chunk(self, chunk: IndianLegalChunk) -> bool:
        """Idempotently inserts or updates an Indian legal chunk with SHA-256 deduplication."""
        chunk_hash = chunk.content_hash or chunk.compute_hash()
        chunk.content_hash = chunk_hash

        ptype = chunk.provision_type.value if hasattr(chunk.provision_type, 'value') else str(chunk.provision_type)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chunk_id FROM indian_legal_chunks WHERE content_hash = ?", (chunk_hash,))
            existing = cursor.fetchone()
            if existing:
                return False

            sql_insert = """
            INSERT INTO indian_legal_chunks (
                chunk_id, document_id, title, act_name, act_prefix, provision_type,
                section_or_article, provision_number, provision_title, chapter, content,
                raw_text, document_type, jurisdiction_level, country, state, court, bench,
                citation, decision_date, legal_domain, authority_tier, temporal_status,
                effective_from, effective_until, transition_note, official_source_url,
                content_hash, embedding_blob
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT(chunk_id) DO UPDATE SET
                provision_type=excluded.provision_type,
                content=excluded.content,
                raw_text=excluded.raw_text,
                temporal_status=excluded.temporal_status,
                transition_note=excluded.transition_note,
                content_hash=excluded.content_hash,
                embedding_blob=COALESCE(excluded.embedding_blob, indian_legal_chunks.embedding_blob);
            """
            cursor.execute(sql_insert, (
                chunk.chunk_id, chunk.document_id, chunk.title, chunk.act_name, chunk.act_prefix,
                ptype, chunk.section_or_article, chunk.provision_number, chunk.provision_title,
                chunk.chapter, chunk.content, chunk.raw_text,
                chunk.document_type.value if hasattr(chunk.document_type, 'value') else str(chunk.document_type),
                chunk.jurisdiction_level.value if hasattr(chunk.jurisdiction_level, 'value') else str(chunk.jurisdiction_level),
                chunk.country, chunk.state, chunk.court, chunk.bench, chunk.citation, chunk.decision_date,
                chunk.legal_domain,
                chunk.authority_tier.value if hasattr(chunk.authority_tier, 'value') else str(chunk.authority_tier),
                chunk.temporal_status.value if hasattr(chunk.temporal_status, 'value') else str(chunk.temporal_status),
                chunk.effective_from, chunk.effective_until, chunk.transition_note,
                chunk.official_source_url, chunk_hash, chunk.embedding_blob
            ))

            # Update FTS5 table
            cursor.execute("DELETE FROM indian_legal_chunks_fts WHERE chunk_id = ?", (chunk.chunk_id,))
            try:
                cursor.execute("""
                INSERT INTO indian_legal_chunks_fts (
                    chunk_id, title, act_name, act_prefix, provision_type, section_or_article,
                    provision_number, provision_title, chapter, content, citation, court, state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.title, chunk.act_name, chunk.act_prefix, ptype,
                    chunk.section_or_article, chunk.provision_number, chunk.provision_title,
                    chunk.chapter, chunk.content, chunk.citation or "", chunk.court or "", chunk.state or ""
                ))
            except sqlite3.OperationalError:
                cursor.execute("""
                INSERT INTO indian_legal_chunks_fts (
                    chunk_id, title, act_name, act_prefix, section_or_article,
                    provision_number, provision_title, chapter, content, citation, court, state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.title, chunk.act_name, chunk.act_prefix,
                    chunk.section_or_article, chunk.provision_number, chunk.provision_title,
                    chunk.chapter, chunk.content, chunk.citation or "", chunk.court or "", chunk.state or ""
                ))
            conn.commit()
            return True

    def check_provision_exists(self, act_prefix: str, provision_number: str, provision_type: str = "SECTION") -> bool:
        """Determines whether a provision exists in the local corpus for a given Act and provision type."""
        sql = """
        SELECT 1 FROM indian_legal_chunks
        WHERE act_prefix = ? AND provision_number = ? AND provision_type = ?
        LIMIT 1
        """
        with self._get_connection() as conn:
            return conn.execute(sql, (act_prefix, provision_number, provision_type)).fetchone() is not None

    def get_chunk_by_provision(
        self,
        act_prefix: str,
        provision_number: str,
        provision_type: str = "SECTION"
    ) -> Optional[IndianLegalChunk]:
        """
        Direct retrieval of a specific statutory provision by Act prefix, provision number, and provision type.
        Enforces strict namespace separation.
        Automatically concatenates/merges all sub-chunks if the provision was split during chunking,
        ensuring complete statutory atomicity (all sub-sections, definitions, and punishments).
        """
        sql = """
        SELECT * FROM indian_legal_chunks
        WHERE act_prefix = ? AND provision_number = ? AND provision_type = ?
        ORDER BY chunk_id ASC
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (act_prefix, provision_number, provision_type))
            rows = cursor.fetchall()

            # Fallback if provision_type was ARTICLE
            if not rows and provision_type == "ARTICLE":
                cursor.execute(
                    "SELECT * FROM indian_legal_chunks WHERE act_prefix = ? AND provision_number = ? AND provision_type = 'ARTICLE' ORDER BY chunk_id ASC",
                    (act_prefix, provision_number)
                )
                rows = cursor.fetchall()

            if not rows:
                return None

            if len(rows) == 1:
                return self._row_to_chunk(rows[0])

            # Multi-chunk provision: merge all chunks into a complete unified section
            chunks = [self._row_to_chunk(r) for r in rows]
            base_chunk = chunks[0]

            merged_contents = []
            merged_raws = []
            header_prefix = None

            for idx, c in enumerate(chunks):
                c_content = c.content.strip()
                c_raw = (c.raw_text or c.content).strip()

                if idx == 0:
                    merged_contents.append(c_content)
                    merged_raws.append(c_raw)
                    if c_content.startswith("[") and "]" in c_content:
                        header_prefix = c_content[:c_content.index("]") + 1]
                else:
                    if header_prefix and c_content.startswith(header_prefix):
                        c_content = c_content[len(header_prefix):].strip()
                    if header_prefix and c_raw.startswith(header_prefix):
                        c_raw = c_raw[len(header_prefix):].strip()

                    merged_contents.append(c_content)
                    merged_raws.append(c_raw)

            base_chunk.content = "\n\n".join(merged_contents)
            base_chunk.raw_text = "\n\n".join(merged_raws)
            return base_chunk

    def get_chunk(self, chunk_id: str) -> Optional[IndianLegalChunk]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indian_legal_chunks WHERE chunk_id = ?", (chunk_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_chunk(row)
        return None

    def get_chunks_by_act(self, act_prefix: str, provision_type: Optional[str] = None) -> List[IndianLegalChunk]:
        sql = "SELECT * FROM indian_legal_chunks WHERE act_prefix = ?"
        params = [act_prefix]
        if provision_type:
            sql += " AND provision_type = ?"
            params.append(provision_type)
        sql += " ORDER BY provision_number"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_chunk(r) for r in rows]

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indian_legal_documents WHERE document_id = ?", (document_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_document_by_prefix(self, act_prefix: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indian_legal_documents WHERE act_prefix = ? LIMIT 1", (act_prefix,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indian_legal_documents ORDER BY title ASC")
            return [dict(r) for r in cursor.fetchall()]

    def search_fts(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 15
    ) -> List[Tuple[IndianLegalChunk, float]]:
        """Performs BM25-ranked full text search on FTS5 with legal metadata filtering."""
        clean_terms = []
        for term in query.replace('"', ' ').replace("'", ' ').split():
            clean = "".join(c for c in term if c.isalnum() or c in ("-", "_"))
            if clean and clean.lower() not in ("and", "or", "not", "near"):
                clean_terms.append(f'"{clean}"')

        if not clean_terms:
            return []

        fts_match = " OR ".join(clean_terms)
        where_clauses = ["fts.indian_legal_chunks_fts MATCH ?"]
        params: List[Any] = [fts_match]

        if filters:
            if filters.act_prefix:
                where_clauses.append("c.act_prefix = ?")
                params.append(filters.act_prefix)
            if filters.provision_type:
                pt = filters.provision_type.value if hasattr(filters.provision_type, 'value') else str(filters.provision_type)
                where_clauses.append("c.provision_type = ?")
                params.append(pt)
            if filters.jurisdiction_level:
                where_clauses.append("c.jurisdiction_level = ?")
                params.append(filters.jurisdiction_level.value)
            if filters.state:
                where_clauses.append("(c.state = ? OR c.state IS NULL)")
                params.append(filters.state)
            if filters.court:
                where_clauses.append("(c.court = ? OR c.court IS NULL)")
                params.append(filters.court)
            if filters.authority_tier:
                where_clauses.append("c.authority_tier = ?")
                params.append(filters.authority_tier.value)
            if filters.temporal_status:
                where_clauses.append("c.temporal_status = ?")
                params.append(filters.temporal_status.value)
            if filters.legal_domain:
                where_clauses.append("c.legal_domain = ?")
                params.append(filters.legal_domain)

        order_clause = "fts.rank"
        order_params: List[Any] = []
        if filters and filters.provision_number:
            order_clause = "CASE WHEN c.provision_number = ? THEN 0 ELSE 1 END, fts.rank"
            order_params.append(filters.provision_number)

        sql = f"""
        SELECT c.*, fts.rank as bm25_rank
        FROM indian_legal_chunks_fts fts
        JOIN indian_legal_chunks c ON fts.chunk_id = c.chunk_id
        WHERE {" AND ".join(where_clauses)}
        ORDER BY {order_clause}
        LIMIT ?
        """
        all_params = params + order_params + [limit]

        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, all_params)
                rows = cursor.fetchall()
                for row in rows:
                    chunk = self._row_to_chunk(row)
                    score = float(row["bm25_rank"]) if "bm25_rank" in row.keys() else 1.0
                    results.append((chunk, score))
            except Exception as e:
                logger.warning(f"FTS search error with query '{query}': {e}")

        return results

    def check_collision_matrix(self) -> List[Dict[str, Any]]:
        """Finds any collisions where identical provision_number appears under multiple provision_types in same Act."""
        sql = """
        SELECT act_prefix, provision_number, count(DISTINCT provision_type) as ptype_count,
               GROUP_CONCAT(DISTINCT provision_type) as types
        FROM indian_legal_chunks
        GROUP BY act_prefix, provision_number
        HAVING ptype_count > 1
        ORDER BY act_prefix, provision_number
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_document_count(self) -> int:
        with self._get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM indian_legal_documents").fetchone()[0]

    def get_chunk_count(self) -> int:
        with self._get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM indian_legal_chunks").fetchone()[0]

    def _row_to_chunk(self, r: sqlite3.Row) -> IndianLegalChunk:
        ptype = ProvisionType.SECTION
        if "provision_type" in r.keys() and r["provision_type"]:
            try:
                ptype = ProvisionType(r["provision_type"])
            except ValueError:
                ptype = ProvisionType.SECTION

        return IndianLegalChunk(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            title=r["title"],
            act_name=r["act_name"],
            act_prefix=r["act_prefix"],
            provision_type=ptype,
            section_or_article=r["section_or_article"],
            provision_number=r["provision_number"],
            provision_title=r["provision_title"],
            chapter=r["chapter"],
            content=r["content"],
            raw_text=r["raw_text"],
            document_type=IndianDocumentType(r["document_type"]),
            jurisdiction_level=IndianJurisdictionLevel(r["jurisdiction_level"]),
            country=r["country"],
            state=r["state"],
            court=r["court"],
            bench=r["bench"],
            citation=r["citation"],
            decision_date=r["decision_date"],
            legal_domain=r["legal_domain"],
            authority_tier=AuthorityTier(r["authority_tier"]),
            temporal_status=TemporalStatus(r["temporal_status"]),
            effective_from=r["effective_from"],
            effective_until=r["effective_until"],
            transition_note=r["transition_note"],
            official_source_url=r["official_source_url"],
            content_hash=r["content_hash"],
            embedding_blob=r["embedding_blob"]
        )
