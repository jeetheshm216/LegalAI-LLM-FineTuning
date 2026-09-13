"""Hybrid statutory retrieval engine implementing Lexical (FTS5), Dense Vector, and RRF Fusion."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from ..database.base import BaseLegalDatabase
from ..embeddings.embedder import LegalEmbedder


@dataclass
class RetrievalResult:
    chunk_id: str
    act: str
    act_prefix: str
    act_type: str
    section: str
    section_title: str
    chapter: str
    text: str
    raw_section_text: str
    source: str
    source_url: str
    relevance_score: float
    effective_date: str
    document_version: str
    retrieval_mode: str


class LegalRetriever:
    """Orchestrates lexical, vector, and hybrid statutory searches."""

    def __init__(self, db: BaseLegalDatabase, embedder: Optional[LegalEmbedder] = None):
        self.db = db
        self.embedder = embedder

    def retrieve(
        self,
        query: str,
        act_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        effective_date: Optional[str] = None,
        mode: str = "hybrid",
        top_k: int = 5,
        rrf_k: int = 60
    ) -> List[RetrievalResult]:
        """
        Executes query retrieval across legal chunks.
        
        Args:
            query: Natural language advocate query or statutory reference.
            act_filter: Filter by act prefix (e.g. 'BNS', 'BNSS', 'BSA').
            section_filter: Exact statutory section number (e.g. '103', '482', '63').
            effective_date: Incident or filing date (YYYY-MM-DD) for temporal filtering.
            mode: 'hybrid', 'lexical', or 'vector'.
            top_k: Number of top results to return.
            rrf_k: Reciprocal Rank Fusion smoothing constant (default 60).
        """
        if mode == "lexical":
            lexical_results = self.db.search_lexical(
                query,
                act_filter=act_filter,
                section_filter=section_filter,
                effective_date=effective_date,
                limit=top_k
            )
            return [self._format_result(r, r.get("lexical_score", 1.0), "lexical") for r in lexical_results]

        if mode == "vector":
            if self.embedder is None:
                raise ValueError("LegalEmbedder is required for vector retrieval mode.")
            q_vec = self.embedder.encode_query(query)
            vector_results = self.db.search_vector(
                q_vec,
                act_filter=act_filter,
                section_filter=section_filter,
                effective_date=effective_date,
                limit=top_k
            )
            return [self._format_result(r, r.get("vector_score", 1.0), "vector") for r in vector_results]

        # Mode == 'hybrid': Reciprocal Rank Fusion (RRF)
        pool_size = max(top_k * 4, 25)
        
        # 1. Fetch Lexical Candidates
        lex_candidates = self.db.search_lexical(
            query,
            act_filter=act_filter,
            section_filter=section_filter,
            effective_date=effective_date,
            limit=pool_size
        )
        
        # 2. Fetch Vector Candidates
        vec_candidates = []
        if self.embedder is not None:
            q_vec = self.embedder.encode_query(query)
            vec_candidates = self.db.search_vector(
                q_vec,
                act_filter=act_filter,
                section_filter=section_filter,
                effective_date=effective_date,
                limit=pool_size
            )

        # 3. Compute RRF Scores
        scores: Dict[str, float] = {}
        doc_store: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(lex_candidates, start=1):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            doc_store[cid] = item

        for rank, item in enumerate(vec_candidates, start=1):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            if cid not in doc_store:
                doc_store[cid] = item

        # 4. Sort by fused score
        sorted_cids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        results = []
        for cid in sorted_cids[:top_k]:
            doc = doc_store[cid]
            fused_score = scores[cid]
            results.append(self._format_result(doc, fused_score, "hybrid"))

        return results

    def _format_result(self, doc: Dict[str, Any], score: float, mode: str) -> RetrievalResult:
        return RetrievalResult(
            chunk_id=doc["chunk_id"],
            act=doc["act_name"],
            act_prefix=doc["act_prefix"],
            act_type=doc["act_type"],
            section=doc["section_number"],
            section_title=doc["section_title"],
            chapter=doc["chapter"],
            text=doc["content"],
            raw_section_text=doc.get("raw_section_text", doc["content"]),
            source=doc["source"],
            source_url=doc["source_url"],
            relevance_score=float(score),
            effective_date=doc.get("effective_from", "2024-07-01"),
            document_version=doc.get("document_version", "1.0-ORIGINAL-ENACTMENT"),
            retrieval_mode=mode
        )
