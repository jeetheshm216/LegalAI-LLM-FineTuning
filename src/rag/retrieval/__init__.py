"""Hybrid statutory retrieval engine combining Lexical (FTS5) and Dense Vector search."""

from .retriever import LegalRetriever, RetrievalResult

__all__ = ["LegalRetriever", "RetrievalResult"]
