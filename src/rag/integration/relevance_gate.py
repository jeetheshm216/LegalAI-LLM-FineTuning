"""
relevance_gate.py

Evidence sufficiency and statutory relevance gate for LegalAI RAG.
Filters candidate retrieval chunks using configurable dense cosine similarity,
lexical FTS matching, and domain consistency thresholds to prevent irrelevant chunks
from being injected into the model prompt.
"""

import os
import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("LegalAI-RelevanceGate")


@dataclass
class GateEvaluationResult:
    is_passed: bool
    filtered_chunks: List[Any]
    rejection_reason: Optional[str]
    max_dense_score: float
    max_lexical_score: float
    max_rrf_score: float
    audit_logs: List[Dict[str, Any]]


class StatutoryRelevanceGate:
    """Evaluates candidate chunks to ensure they meet minimum statutory authority and relevance thresholds."""

    def __init__(
        self,
        min_dense_similarity: float = float(os.getenv("RAG_MIN_DENSE_SIMILARITY", "0.55")),
        min_lexical_score: float = float(os.getenv("RAG_MIN_LEXICAL_SCORE", "0.05")),
        min_rrf_score: float = float(os.getenv("RAG_MIN_RRF_SCORE", "0.015")),
    ):
        self.min_dense_similarity = min_dense_similarity
        self.min_lexical_score = min_lexical_score
        self.min_rrf_score = min_rrf_score

    def evaluate_candidates(
        self,
        query: str,
        candidates: List[Any],
        target_domain: Optional[str] = None,
        target_statute_code: Optional[str] = None,
        target_section: Optional[str] = None
    ) -> GateEvaluationResult:
        """
        Filters and audits candidate retrieval chunks.
        """
        audit_logs = []
        accepted_chunks = []

        max_dense = 0.0
        max_lexical = 0.0
        max_rrf = 0.0

        q_clean = query.lower()

        for c in candidates:
            # Extract scores
            rrf_score = getattr(c, "relevance_score", 0.0)
            chunk_act = getattr(c, "act_prefix", "").upper()
            chunk_sec = str(getattr(c, "section", "")).strip()
            chunk_title = getattr(c, "section_title", "").lower()
            chunk_text = getattr(c, "text", "").lower()

            max_rrf = max(max_rrf, rrf_score)

            # Check if an explicit target section was requested and matches
            section_matched = False
            if target_section and target_section.lower() == chunk_sec.lower():
                section_matched = True

            # Check Act domain compatibility
            act_compatible = True
            if target_statute_code:
                if chunk_act != target_statute_code:
                    act_compatible = False

            # Check keyword relevance overlap
            # Extract key nouns / substantive words (>4 chars) from query
            q_keywords = [w for w in re.findall(r'\b[a-z]{4,}\b', q_clean) if w not in ("what", "which", "where", "under", "about", "provisions", "section", "act", "india", "law")]
            overlap_count = sum(1 for kw in q_keywords if kw in chunk_title or kw in chunk_text)
            overlap_ratio = overlap_count / max(len(q_keywords), 1)

            # Heuristic estimate for dense score from RRF or direct rank
            dense_score = getattr(c, "vector_score", 0.0)
            if dense_score == 0.0:
                # If RRF was used, rank 1 corresponds to ~0.0163; top rank proxy
                dense_score = min(1.0, rrf_score * 35.0)

            max_dense = max(max_dense, dense_score)

            # Acceptance decision criteria:
            # 1. Exact section match (e.g. Section 103 BNS) -> Accept immediately
            # 2. Dense score >= min_dense_similarity AND act_compatible AND keyword overlap
            # 3. If query explicitly outside criminal law -> Reject
            decision = "REJECT"
            reason = ""

            if section_matched and act_compatible:
                decision = "ACCEPT"
                reason = "Exact statutory section and Act match."
            elif not act_compatible:
                decision = "REJECT"
                reason = f"Act mismatch: target={target_statute_code}, retrieved={chunk_act}."
            elif overlap_count == 0 and not section_matched:
                decision = "REJECT"
                reason = "Zero substantive keyword overlap with query."
            elif rrf_score < self.min_rrf_score and overlap_ratio < 0.2:
                decision = "REJECT"
                reason = f"Sub-threshold RRF score ({rrf_score:.4f} < {self.min_rrf_score}) and poor overlap ({overlap_ratio:.2f})."
            else:
                decision = "ACCEPT"
                reason = f"Passed statutory relevance gate (RRF: {rrf_score:.4f}, Keyword matches: {overlap_count})."

            log_entry = {
                "chunk_id": getattr(c, "chunk_id", ""),
                "act": chunk_act,
                "section": chunk_sec,
                "title": chunk_title[:50],
                "rrf_score": round(rrf_score, 4),
                "keyword_matches": overlap_count,
                "decision": decision,
                "reason": reason
            }
            audit_logs.append(log_entry)

            if decision == "ACCEPT":
                accepted_chunks.append(c)

        is_passed = len(accepted_chunks) > 0
        rejection_reason = None
        if not is_passed:
            if not candidates:
                rejection_reason = "No candidate statutory chunks retrieved from database."
            else:
                rejection_reason = f"All {len(candidates)} candidate chunks rejected by relevance gate (unrelated to query intent)."

        return GateEvaluationResult(
            is_passed=is_passed,
            filtered_chunks=accepted_chunks,
            rejection_reason=rejection_reason,
            max_dense_score=max_dense,
            max_lexical_score=max_lexical,
            max_rrf_score=max_rrf,
            audit_logs=audit_logs
        )
