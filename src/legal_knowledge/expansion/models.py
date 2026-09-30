"""Data schemas for the Automated Indian Legal Corpus Expansion Engine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List


class IngestionStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    QUEUED = "QUEUED"
    DOWNLOADING = "DOWNLOADING"
    DOWNLOADED = "DOWNLOADED"
    PARSED = "PARSED"
    VALIDATED = "VALIDATED"
    INDEXED = "INDEXED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


@dataclass
class DiscoveredAct:
    """Metadata representing an authoritative Indian Act discovered from an official repository."""
    act_id: str
    act_name: str
    short_title: str
    handle_url: str
    act_number: Optional[str] = None
    enactment_year: Optional[int] = None
    pdf_url: Optional[str] = None
    text_url: Optional[str] = None
    ministry: Optional[str] = None
    jurisdiction_level: str = "CENTRAL"
    source_id: str = "SRC_INDIA_CODE"
    discovery_timestamp: str = ""
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "act_id": self.act_id,
            "act_name": self.act_name,
            "short_title": self.short_title,
            "handle_url": self.handle_url,
            "act_number": self.act_number,
            "enactment_year": self.enactment_year,
            "pdf_url": self.pdf_url,
            "text_url": self.text_url,
            "ministry": self.ministry,
            "jurisdiction_level": self.jurisdiction_level,
            "source_id": self.source_id,
            "discovery_timestamp": self.discovery_timestamp,
            "raw_metadata": self.raw_metadata,
        }


@dataclass
class IngestionRecord:
    """Persistent tracking record for a legal document in the expansion engine."""
    source_url: str
    act_name: str
    act_prefix: str
    status: IngestionStatus
    act_number: Optional[str] = None
    enactment_year: Optional[int] = None
    content_hash: Optional[str] = None
    version_id: str = "1.0"
    chunks_created: int = 0
    last_attempt: str = ""
    last_successful: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class IngestionSummary:
    """Observability counts and metrics for an expansion run."""
    discovered: int = 0
    already_indexed: int = 0
    new_documents: int = 0
    downloaded: int = 0
    parsed: int = 0
    validated: int = 0
    indexed: int = 0
    skipped: int = 0
    failed: int = 0
    chunks_added: int = 0
    failures: List[Dict[str, Any]] = field(default_factory=list)
    indexed_acts: List[Dict[str, Any]] = field(default_factory=list)

    def to_report(self) -> str:
        lines = [
            "============================================================",
            "LEGALAI — INDIAN LEGAL CORPUS EXPANSION REPORT",
            "============================================================",
            f"Source Repository:   India Code (Official Central Acts)",
            f"Discovered:          {self.discovered}",
            f"Already Indexed:     {self.already_indexed}",
            f"New Documents:       {self.new_documents}",
            f"Downloaded:          {self.downloaded}",
            f"Parsed:              {self.parsed}",
            f"Validated:           {self.validated}",
            f"Indexed:             {self.indexed}",
            f"Skipped:             {self.skipped}",
            f"Failed:              {self.failed}",
            f"Chunks Added:        {self.chunks_added}",
            "============================================================",
        ]
        if self.indexed_acts:
            lines.append("\nIndexed Acts Summary:")
            for item in self.indexed_acts:
                lines.append(f"  ✓ {item.get('title')} ({item.get('act_prefix')}): {item.get('chunks')} chunks [Status: {item.get('status')}]")

        if self.failures:
            lines.append("\nFailures / Rejections:")
            for f in self.failures:
                lines.append(f"  ✗ {f.get('act_name')}: {f.get('reason')} [Stage: {f.get('stage')}]")

        return "\n".join(lines)
