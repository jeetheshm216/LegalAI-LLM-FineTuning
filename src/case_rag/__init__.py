"""
src/case_rag/__init__.py

Case Document RAG subsystem for LegalAI.
Provides document extraction, page provenance preservation, case-isolated indexing,
hybrid retrieval, and grounded Case Analysis V1 generation.
"""

from .models import (
    EvidenceStatus,
    ExtractedPage,
    CaseDocument,
    DocumentChunk,
    CaseRetrievalResult,
    CaseAnalysisResult,
)
from .document_processor import DocumentProcessor
from .chunker import CaseDocumentChunker
from .embeddings import CaseEmbedder
from .index import CaseRAGIndex
from .retriever import CaseRetriever
from .pipeline import CaseRAGPipeline

__all__ = [
    "EvidenceStatus",
    "ExtractedPage",
    "CaseDocument",
    "DocumentChunk",
    "CaseRetrievalResult",
    "CaseAnalysisResult",
    "DocumentProcessor",
    "CaseDocumentChunker",
    "CaseEmbedder",
    "CaseRAGIndex",
    "CaseRetriever",
    "CaseRAGPipeline",
]
