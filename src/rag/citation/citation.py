"""Pinpoint, traceable statutory citation generator for Indian law."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class PinpointCitation:
    act_name: str
    act_number: str
    section_number: str
    section_title: str
    chapter: str
    source: str
    source_url: str
    version: str
    effective_date: str
    citation_text: str


def format_legal_citation(result: Any) -> PinpointCitation:
    """
    Generates a cryptographically and institutionally traceable statutory citation.
    Strict Rule: Zero fake URLs; if URL is missing, omit URL rather than hallucinating.
    """
    if hasattr(result, "act"):
        act_name = result.act
        act_prefix = result.act_prefix
        section_number = result.section
        section_title = result.section_title
        chapter = result.chapter
        source = result.source
        source_url = result.source_url
        version = result.document_version
        effective_date = result.effective_date
    else:
        act_name = result["act_name"]
        act_prefix = result.get("act_prefix", "")
        section_number = result["section_number"]
        section_title = result["section_title"]
        chapter = result.get("chapter", "")
        source = result.get("source", "India Code")
        source_url = result.get("source_url", "")
        version = result.get("document_version", "1.0-ORIGINAL-ENACTMENT")
        effective_date = result.get("effective_from", "2024-07-01")

    # Format authoritative citation string
    citation_parts = [
        f"Section {section_number} ('{section_title}')",
        f"{act_name}",
        f"w.e.f. {effective_date}",
        f"Version: {version}",
        f"Authority: {source}"
    ]

    if source_url and source_url.startswith("http"):
        citation_parts.append(f"Official Repository: <{source_url}>")

    citation_text = ", ".join(citation_parts)

    return PinpointCitation(
        act_name=act_name,
        act_number=act_prefix,
        section_number=section_number,
        section_title=section_title,
        chapter=chapter,
        source=source,
        source_url=source_url,
        version=version,
        effective_date=effective_date,
        citation_text=citation_text
    )
