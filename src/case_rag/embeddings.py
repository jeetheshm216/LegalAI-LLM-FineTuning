"""
src/case_rag/embeddings.py

Dense embedding generator for Case Document RAG.
Reuses local BAAI/bge-large-en-v1.5 sentence-transformers model.
"""

from typing import List, Optional, Union
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


class CaseEmbedder:
    """Encodes case document passages and lawyer queries into normalized dense vectors."""

    DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"
    QUERY_PREFIX = "Represent this legal inquiry for retrieving case materials, evidence, and pleadings: "

    def __init__(self, model_name: str = DEFAULT_MODEL, device: Optional[str] = None, existing_model=None):
        if existing_model is not None:
            self.model = existing_model
            self.device = str(existing_model.device) if hasattr(existing_model, "device") else "cuda:0"
        else:
            if device is None:
                self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device
            self.model = SentenceTransformer(model_name, device=self.device)

        self.vector_dim = self.model.get_sentence_embedding_dimension()

    def encode_passages(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encodes case document chunks into normalized dense vectors."""
        if not texts:
            return np.empty((0, self.vector_dim), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """Encodes a lawyer query with domain prefix into a normalized vector."""
        prefixed = self.QUERY_PREFIX + query
        embedding = self.model.encode(
            prefixed,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding
