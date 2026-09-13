"""Local embedding model generator using sentence-transformers on GPU 0."""

import os
from typing import List, Union
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


class LegalEmbedder:
    """Encodes legal statutory provisions and queries using local BAAI/bge-large-en-v1.5."""

    DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"
    QUERY_PREFIX = "Represent this legal question for retrieving relevant Indian statutory provisions: "

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str = None):
        self.model_name = model_name

        if device is None:
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Loading LegalEmbedder '{self.model_name}' on device: {self.device}...")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        self.vector_dim = self.model.get_sentence_embedding_dimension()
        print(f"LegalEmbedder loaded successfully. Verified Vector Dimension: {self.vector_dim}")

    def encode_passages(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """Encodes statutory chunk texts into normalized dense vectors."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """Encodes an advocate search query with BGE asymmetric instruction prefix."""
        prefixed = self.QUERY_PREFIX + query
        embedding = self.model.encode(
            prefixed,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding
