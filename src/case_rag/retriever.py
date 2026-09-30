"""
src/case_rag/retriever.py

Hybrid retriever for Case Document RAG.
Combines dense vector cosine similarity with SQLite FTS5 BM25 lexical ranking.
Enhancements:
- Query-conditioned retrieval with prioritized lexical matching
- Exact entity/clause/date boosting (e.g. "Clause 24", "Port strike")
- Intent-guided keyword hints as a ranking aid
- Absolute strict case_id isolation (zero cross-matter leakage)
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

# Ranking hints for specific sub-intents / output plans (used strictly as ranking aids)
INTENT_RANKING_HINTS = {
    "CASE_EVIDENCE": ["evidence", "exhibit", "receipt", "communication", "notification", "letter", "agreement", "invoice", "record"],
    "AVAILABLE_EVIDENCE": ["evidence", "exhibit", "receipt", "communication", "notification", "letter", "agreement", "invoice", "record"],
    "CASE_EVIDENCE_GAPS": ["missing", "discrepancy", "gap", "unsupported", "defect", "verification", "unproduced"],
    "EVIDENCE_GAPS": ["missing", "discrepancy", "gap", "unsupported", "defect", "verification", "unproduced"],
    "CASE_TIMELINE": ["dated", "order", "hearing", "filing", "notice", "issued", "received", "event"],
    "CHRONOLOGICAL_TIMELINE": ["dated", "order", "hearing", "filing", "notice", "issued", "received", "event"],
    "HEARING_PREPARATION": ["hearing", "injunction", "order", "bench", "interim", "application", "direction", "prayer"],
    "HEARING_BRIEF": ["hearing", "injunction", "order", "bench", "interim", "application", "direction", "prayer"],
    "CASE_ARGUMENTS": ["ground", "contention", "argue", "claim", "breach", "liability", "damages"],
    "POTENTIAL_ARGUMENTS": ["ground", "contention", "argue", "claim", "breach", "liability", "damages"],
    "CASE_COUNTERARGUMENTS": ["defence", "opposing", "respondent", "denial", "counterclaim", "objection"],
    "OPPOSING_ARGUMENTS": ["defence", "opposing", "respondent", "denial", "counterclaim", "objection"],
    "CASE_RISKS": ["risk", "weakness", "vulnerability", "limitation", "delay", "default", "breach"],
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
        lexical_weight: float = 0.3,
        normalized_query: Optional[str] = None,
        sub_intent: Optional[str] = None,
        user_goal: Optional[str] = None,
        output_plan: Optional[str] = None,
    ) -> List[CaseRetrievalResult]:
        """
        Executes query-conditioned, case-isolated hybrid retrieval.
        
        Priority hierarchy:
        1. Exact user query terms & entity/clause matches (e.g. "Clause 24", "port strike")
        2. Specific entity/date/document references
        3. Intent-conditioned lexical ranking hints
        4. Dense semantic similarity
        5. Absolute case_id boundary
        """
        if not case_id or not query:
            return []

        # 1. Fetch all chunks for this specific case (strict data boundary)
        case_chunks = self.index.get_chunks_for_case(case_id)
        if not case_chunks:
            return []

        effective_query = normalized_query or query

        # 2. Dense Vector Retrieval
        query_emb = self.embedder.encode_query(effective_query)
        dense_scores: Dict[str, float] = {}

        chunk_embeddings = [c["embedding"] for c in case_chunks if c["embedding"] is not None]
        chunk_ids_with_emb = [c["chunk_id"] for c in case_chunks if c["embedding"] is not None]

        if chunk_embeddings:
            matrix = np.array(chunk_embeddings, dtype=np.float32)
            # Dot product for normalized vectors = cosine similarity
            sims = np.dot(matrix, query_emb)
            for cid, sim in zip(chunk_ids_with_emb, sims):
                dense_scores[cid] = float(sim)

        # 3. Exact user query terms & entities extraction
        cleaned_query = re.sub(r'[^\w\s]', ' ', effective_query.lower()).strip()
        tokens = [t for t in cleaned_query.split() if len(t) > 2 and t not in STOPWORDS]

        # Extract specific clauses (e.g., "clause 24", "section 63")
        clause_matches = re.findall(r'\b(?:clause|section|order|rule|article)\s+\d+[a-z]?\b', effective_query.lower())
        # Extract quoted or key phrase candidates (e.g., "port strike", "bench iv")
        key_phrases = []
        if "port strike" in effective_query.lower():
            key_phrases.append("port strike")
        if "charterparty" in effective_query.lower():
            key_phrases.append("charterparty")
        if "injunction" in effective_query.lower() or "bench iv" in effective_query.lower():
            key_phrases.append("injunction")
            key_phrases.append("bench iv")

        # 4. Lexical FTS5 Retrieval with stopword filtering + intent hints
        lexical_scores: Dict[str, float] = {}
        exact_match_boosts: Dict[str, float] = {}

        # Collect search tokens: primary user tokens first, then up to 3 intent ranking hints as secondary
        search_terms = list(tokens[:8])
        intent_key = sub_intent or output_plan or ""
        intent_hints = INTENT_RANKING_HINTS.get(intent_key, [])
        for hint in intent_hints[:3]:
            if hint not in search_terms and hint not in STOPWORDS:
                search_terms.append(hint)

        if search_terms:
            fts_query = " OR ".join(f'"{t}"' for t in search_terms)
            conn = self.index._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, bm25(case_chunks_fts) as rank
                    FROM case_chunks_fts
                    WHERE case_id = ? AND case_chunks_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """, (case_id, fts_query, top_k * 4))
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

        # 5. Compute Exact Clause & Phrase Boosts directly on chunk text
        chunk_lookup = {c["chunk_id"]: c for c in case_chunks}
        all_candidate_ids = set(dense_scores.keys()) | set(lexical_scores.keys())

        for cid in all_candidate_ids:
            chunk = chunk_lookup.get(cid)
            if not chunk:
                continue
            text_lower = chunk["text"].lower()
            boost = 0.0

            # Exact clause boost (highest priority)
            for cl in clause_matches:
                if cl in text_lower:
                    boost += 1.5

            # Key phrase boost
            for kp in key_phrases:
                if kp in text_lower:
                    boost += 0.8

            # Sub-intent specific text boosts (subtle ranking aids)
            if sub_intent == "CASE_TIMELINE" or output_plan == "CHRONOLOGICAL_TIMELINE":
                # Boost chunks containing dates/procedural orders
                if re.search(r'\b(?:19|20)\d{2}\b', text_lower) or "order" in text_lower:
                    boost += 0.3
            elif sub_intent == "HEARING_PREPARATION" or output_plan == "HEARING_BRIEF":
                if "hearing" in text_lower or "interim" in text_lower or "injunction" in text_lower:
                    boost += 0.4
            elif sub_intent in ("CASE_EVIDENCE", "CASE_EVIDENCE_GAPS"):
                if "exhibit" in text_lower or "notification" in text_lower or "annexure" in text_lower:
                    boost += 0.3

            if boost > 0:
                exact_match_boosts[cid] = boost

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
            exact_boost = exact_match_boosts.get(cid, 0.0)

            # Linear hybrid fusion: dense semantics + lexical keyword boost + exact clause/phrase boost
            hybrid_score = (dense_weight * dense_sim) + (lexical_weight * norm_lex) + exact_boost

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
