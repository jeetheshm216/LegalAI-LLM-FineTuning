"""
src/case_rag/retriever.py

Hybrid retriever for Case Document RAG.
Combines dense vector cosine similarity with SQLite FTS5 BM25 lexical ranking via RRF.
CRITICAL SECURITY INVARIANT: Case isolation is strictly enforced; a query for case-01
can NEVER retrieve chunks from case-02.
"""

import re
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional

from .models import CaseRetrievalResult
from .index import CaseRAGIndex
from .embeddings import CaseEmbedder


STOPWORDS = {
    "what", "is", "are", "the", "this", "that", "there", "did", "was", "were",
    "where", "when", "who", "whom", "which", "how", "for", "from", "with", "about",
    "and", "or", "in", "on", "at", "to", "by", "of", "an", "a", "be", "been",
    "have", "has", "had", "can", "could", "should", "would", "do", "does", "done",
    "according", "mentioned", "refer", "referred", "say", "said", "any", "some",
    "tell", "give", "show", "check", "find", "between", "under", "into", "over"
}


class CaseRetriever:
    """Hybrid dense + lexical retriever restricted strictly by case_id."""

    def __init__(self, index: CaseRAGIndex, embedder: CaseEmbedder):
        self.index = index
        self.embedder = embedder

    def retrieve(
        self,
        query: str,
        case_id: str,
        top_k: int = 6,
        dense_weight: float = 0.7,
        lexical_weight: float = 0.3
    ) -> List[CaseRetrievalResult]:
        """Executes case-isolated hybrid retrieval for a query."""
        if not case_id or not query:
            return []

        # 1. Fetch all chunks for this specific case (strict data boundary)
        case_chunks = self.index.get_chunks_for_case(case_id)
        if not case_chunks:
            return []

        # 2. Dense Vector Retrieval
        query_emb = self.embedder.encode_query(query)
        dense_scores: Dict[str, float] = {}

        chunk_embeddings = [c["embedding"] for c in case_chunks if c["embedding"] is not None]
        chunk_ids_with_emb = [c["chunk_id"] for c in case_chunks if c["embedding"] is not None]

        if chunk_embeddings:
            matrix = np.array(chunk_embeddings, dtype=np.float32)
            # Dot product for normalized vectors = cosine similarity
            sims = np.dot(matrix, query_emb)
            for cid, sim in zip(chunk_ids_with_emb, sims):
                dense_scores[cid] = float(sim)

        # 3. Lexical FTS5 Retrieval with stopword filtering
        lexical_scores: Dict[str, float] = {}
        cleaned_query = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
        tokens = [t for t in cleaned_query.split() if len(t) > 2 and t not in STOPWORDS]

        if tokens:
            fts_query = " OR ".join(f'"{t}"' for t in tokens[:8])
            conn = self.index._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, bm25(case_chunks_fts) as rank
                    FROM case_chunks_fts
                    WHERE case_id = ? AND case_chunks_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """, (case_id, fts_query, top_k * 3))
                rows = cursor.fetchall()
                for r in rows:
                    raw_rank = float(r["rank"])
                    # FTS5 bm25 returns negative numbers where more negative = better match
                    bm25_positive = max(-raw_rank, 0.0)
                    lexical_scores[r["id"]] = bm25_positive
            except sqlite3.OperationalError:
                pass
            finally:
                conn.close()

        chunk_lookup = {c["chunk_id"]: c for c in case_chunks}
        all_candidate_ids = set(dense_scores.keys()) | set(lexical_scores.keys())

        # Normalize lexical scores to [0, 1] among candidates
        max_lex = max(lexical_scores.values()) if lexical_scores else 1.0
        if max_lex <= 0:
            max_lex = 1.0

        combined_candidates = []
        for cid in all_candidate_ids:
            chunk = chunk_lookup.get(cid)
            if not chunk:
                continue

            dense_sim = dense_scores.get(cid, 0.0)
            raw_lex = lexical_scores.get(cid, 0.0)
            norm_lex = raw_lex / max_lex

            # Linear hybrid fusion: dense semantics + lexical keyword boost
            hybrid_score = (dense_weight * dense_sim) + (lexical_weight * norm_lex)

            combined_candidates.append(CaseRetrievalResult(
                chunk_id=chunk["chunk_id"],
                case_id=chunk["case_id"],
                document_id=chunk["document_id"],
                document_name=chunk["document_name"],
                document_type=chunk["document_type"],
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                score=hybrid_score,
                dense_score=dense_sim,
                lexical_score=norm_lex
            ))

        # Sort by combined hybrid score descending
        combined_candidates.sort(key=lambda x: x.score, reverse=True)
        return combined_candidates[:top_k]
