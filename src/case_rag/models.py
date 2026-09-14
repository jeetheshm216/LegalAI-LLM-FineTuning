"""
src/case_rag/models.py

Data structures and domain models for Case Document RAG.
Preserves strict document and page-level provenance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class EvidenceStatus(str, Enum):
    DOCUMENTED = "DOCUMENTED"
    REQUIRES_VERIFICATION = "REQUIRES_VERIFICATION"
    MISSING_FROM_SUPPLIED_MATERIAL = "MISSING_FROM_SUPPLIED_MATERIAL"
    POTENTIAL_CONTRADICTION = "POTENTIAL_CONTRADICTION"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"


@dataclass
class ExtractedPage:
    """Represents text extracted from a single physical document page."""
    page_number: int
    text: str
    char_count: int
    has_error: bool = False
    error_message: Optional[str] = None


@dataclass
class CaseDocument:
    """Metadata for an uploaded case document."""
    id: str
    case_id: str
    filename: str
    category: str
    file_type: str
    file_size: str
    uploaded_date: str
    status: str
    pages: int
    storage_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    """A semantic text chunk with strict page-level and document provenance."""
    chunk_id: str
    case_id: str
    document_id: str
    document_name: str
    document_type: str
    page_number: int
    chunk_index: int
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "case_id": self.case_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "metadata": self.metadata,
        }


@dataclass
class CaseRetrievalResult:
    """A single retrieved chunk for a case-specific query."""
    chunk_id: str
    case_id: str
    document_id: str
    document_name: str
    document_type: str
    page_number: int
    chunk_index: int
    text: str
    score: float
    dense_score: float = 0.0
    lexical_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "case_id": self.case_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "score": round(self.score, 4),
            "dense_score": round(self.dense_score, 4),
            "lexical_score": round(self.lexical_score, 4),
        }


@dataclass
class CaseAnalysisResult:
    """Full grounded case analysis result for frontend consumption."""
    answer: str
    case_sources: List[Dict[str, Any]]
    legal_sources: List[Dict[str, Any]]
    findings: Dict[str, List[str]] = field(default_factory=dict)
    reliability: str = "supported"
    reliability_label: str = "Supported by case documents"
    confidence_status: str = "CASE_DOCUMENT_GROUNDED"
    generation_time_sec: float = 0.0
