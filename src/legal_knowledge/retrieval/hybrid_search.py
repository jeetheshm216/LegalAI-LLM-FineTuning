"""Hybrid FTS5 and Dense Vector search with Reciprocal Rank Fusion and Authority Ranking."""

import numpy as np
from typing import List, Tuple, Optional, Dict
from ..models import IndianLegalChunk, SearchFilter
from ..indexing.database import IndianLegalDatabaseManager
from ..authority.ranker import IndianAuthorityRanker


class IndianLegalHybridSearcher:
    """Combines lexical keyword matching (FTS5 BM25) and dense semantic search with Indian legal authority weighting."""

    def __init__(self, db_manager: IndianLegalDatabaseManager, embedder=None):
        self.db = db_manager
        self.embedder = embedder
        self.ranker = IndianAuthorityRanker()

    def search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        top_k: int = 5,
        rrf_k: int = 60
    ) -> List[Tuple[IndianLegalChunk, float]]:
        """Executes hybrid retrieval using Reciprocal Rank Fusion and Authority Ranking with strict Act constraints."""
        # 1. Lexical retrieval via SQLite FTS5 (act_prefix and provision_number applied)
        fts_results = self.db.search_fts(query, filters=filters, limit=top_k * 3)

        # 2. Semantic retrieval if embedder is available and embeddings exist
        vector_results = []
        if self.embedder is not None:
            try:
                query_vec = self.embedder.encode_query(query)
                all_chunks = self.db.get_all_chunks()

                scored_chunks = []
                for chunk in all_chunks:
                    # Apply pre-filters
                    if filters:
                        if filters.act_prefix and chunk.act_prefix != filters.act_prefix:
                            continue
                        if filters.jurisdiction_level and chunk.jurisdiction_level != filters.jurisdiction_level:
                            continue
                        if filters.state and chunk.state and chunk.state != filters.state:
                            continue
                        if filters.court and chunk.court and filters.court not in chunk.court:
                            continue
                        if filters.temporal_status and chunk.temporal_status != filters.temporal_status:
                            continue
                        if filters.provision_type and chunk.provision_type != filters.provision_type:
                            continue

                    if chunk.embedding_blob is not None:
                        chunk_vec = np.frombuffer(chunk.embedding_blob, dtype=np.float32)
                        dot_product = float(np.dot(query_vec, chunk_vec))
                        norm_prod = float(np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec))
                        cosine_sim = dot_product / norm_prod if norm_prod > 0 else 0.0
                        scored_chunks.append((chunk, cosine_sim))

                scored_chunks.sort(key=lambda x: x[1], reverse=True)
                vector_results = scored_chunks[:top_k * 3]
            except Exception:
                # Graceful fallback to FTS only if vector inference fails
                pass

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, IndianLegalChunk] = {}

        # Merge FTS rankings
        for rank, (chunk, _) in enumerate(fts_results, start=1):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        # Merge Vector rankings
        for rank, (chunk, _) in enumerate(vector_results, start=1):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        # 3B. Deterministic Provision Pinning (Exact statutory provision match)
        if filters and filters.act_prefix and filters.provision_number:
            exact_chunk = self.db.get_chunk_by_provision(filters.act_prefix, filters.provision_number)
            if exact_chunk:
                cid = exact_chunk.chunk_id
                chunk_map[cid] = exact_chunk
                # Dominant score boost to guarantee exact statutory provision ranks #1
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 100.0

        # 3C. Substantive Concept / Title Match Boosting
        import re as _re
        query_words = set(_re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())) - {
            "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
            "does", "will", "would", "should", "could", "can", "are", "the", "and",
            "for", "with", "about", "into", "through", "during", "before", "after",
            "from", "under", "again", "further", "then", "legal", "definition",
            "bns", "bnss", "bsa", "ipc", "crpc", "cpc", "iea", "act", "sanhita", "code"
        }
        for cid, chunk in chunk_map.items():
            c_title_clean = _re.sub(r'[^a-zA-Z0-9\s]', '', chunk.provision_title or '').lower().strip()
            c_title_words = set(c_title_clean.split())
            if c_title_words and c_title_words.intersection(query_words):
                if c_title_clean in query_words:
                    rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 25.0
                else:
                    rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 10.0

        if not rrf_scores:
            return []

        # Convert to list of (chunk, rrf_score)
        combined_candidates = [(chunk_map[cid], rrf_scores[cid]) for cid in rrf_scores]

        # Enforce strict Act constraint if specified: reject any cross-domain leakage
        if filters and filters.act_prefix:
            combined_candidates = [
                (c, s) for (c, s) in combined_candidates
                if c.act_prefix == filters.act_prefix
            ]

        if not combined_candidates:
            return []

        # 4. Authority Ranking re-weighting
        ranked_results = self.ranker.rank_chunks(combined_candidates)

        return ranked_results[:top_k]
