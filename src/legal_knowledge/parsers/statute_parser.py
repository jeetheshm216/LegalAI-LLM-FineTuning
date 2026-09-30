"""Parser for Indian Central and State Statutes, Constitutional provisions, and Subordinate Rules."""

import re
from typing import List, Dict, Any, Optional
from ..models import (
    IndianLegalDocument,
    IndianLegalChunk,
    IndianDocumentType,
    IndianJurisdictionLevel,
    AuthorityTier,
    TemporalStatus,
    LegalDomain
)


class IndianStatuteParser:
    """Parses Indian statutory texts (Acts, Codes, Constitution, Rules) into structured legal chunks."""

    # Patterns indicating footnotes, amendment notations, or procedural notes rather than substantive section headings
    FOOTNOTE_REJECT_PATTERN = re.compile(
        r'^(?:Subs\.|Ins\.|Omitted|Added|Proviso|The\s+words|The\s+proviso|The\s+application|Vide|This\s+Act|Section\s+\d+|\d+[a-z]{0,2}\s+[A-Za-z]+,\s+\d{4}|Serial\s+number|Clause|Because\s+of|Though\s+the|The\s+Bill|The\s+Code|The\s+Notes|We\s+are|As\s+regards|w\.e\.f\.)',
        re.IGNORECASE
    )

    def __init__(self):
        # Matches patterns like "Section 138. Dishonour...", "1. Short title...", "Article 21. Protection...", "1[10. Specific performance..."
        self.sec_art_pattern = re.compile(
            r'^(?:(?:\d*\[)?(?:(?:Section|Sec\.)\s+([0-9]+[A-Z]*)|([0-9]+[A-Z]*)))\.\s*(.*?)$',
            re.MULTILINE
        )

    def _strip_arrangement_of_sections(self, raw_text: str) -> str:
        """Strips the Table of Contents ('Arrangement of Sections') if present before the enacting formula."""
        enactment_idx = -1
        # Look for the formal enactment formula or Act number header
        for match in re.finditer(
            r'(?:BE\s+it\s+enacted|ACT\s+NO\.?\s+\d+|An\s+Act\s+to\b|\[\d+[a-z]{0,2}\s+[A-Za-z]+,\s+\d{4}\.?\])',
            raw_text,
            re.IGNORECASE
        ):
            if match.start() > 200:
                enactment_idx = match.start()
                break

        if enactment_idx != -1:
            return raw_text[enactment_idx:]
        return raw_text

    def parse_provisions(
        self,
        document: IndianLegalDocument,
        raw_text: str,
        default_chapter: str = "General Provisions"
    ) -> List[IndianLegalChunk]:
        """Parses a structured or raw statute text into individual provision chunks."""
        chunks: List[IndianLegalChunk] = []

        # Strip arrangement of sections table of contents
        body_text = self._strip_arrangement_of_sections(raw_text)

        lines = body_text.split("\n")
        current_num = ""
        current_title = ""
        current_lines: List[str] = []
        current_chapter = default_chapter
        seen_section_ids: Dict[str, int] = {}

        is_constitution = (document.document_type == IndianDocumentType.CONSTITUTION)
        prefix_type = "Article" if is_constitution else "Section"

        def flush_current():
            nonlocal current_num, current_title, current_lines, current_chapter
            if current_num and current_lines:
                body = "\n".join(current_lines).strip()
                if body and len(body) >= 20:
                    # Disambiguate duplicate section numbers in schedules or amendments
                    base_sec_id = current_num
                    if base_sec_id in seen_section_ids:
                        seen_section_ids[base_sec_id] += 1
                        chunk_id = f"{document.act_prefix}_{base_sec_id}_{seen_section_ids[base_sec_id]}"
                    else:
                        seen_section_ids[base_sec_id] = 1
                        chunk_id = f"{document.act_prefix}_{base_sec_id}"

                    sec_or_art = f"{prefix_type} {current_num}"
                    title_display = f" {current_title}" if current_title else ""
                    full_content = f"{document.title}\n{sec_or_art}.{title_display}\n\n{body}"

                    chunk = IndianLegalChunk(
                        chunk_id=chunk_id,
                        document_id=document.document_id,
                        title=document.title,
                        act_name=document.title,
                        act_prefix=document.act_prefix or "ACT",
                        section_or_article=sec_or_art,
                        provision_number=current_num,
                        provision_title=current_title or f"{sec_or_art} of {document.title}",
                        chapter=current_chapter,
                        content=full_content,
                        raw_text=body,
                        document_type=document.document_type,
                        jurisdiction_level=document.jurisdiction_level,
                        country=document.country,
                        state=document.state,
                        legal_domain=document.legal_domain,
                        authority_tier=document.authority_tier,
                        temporal_status=document.temporal_status,
                        effective_from=document.effective_from,
                        effective_until=document.effective_until,
                        transition_note=f"Status: {document.temporal_status.value}",
                        official_source_url=document.official_source_url
                    )
                    chunk.content_hash = chunk.compute_hash()
                    chunks.append(chunk)

            current_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_lines:
                    current_lines.append("")
                continue

            # Check for Chapter/Part headings
            if re.match(r'^(?:CHAPTER|PART)\s+[IVXLCDM0-9]+', stripped, re.IGNORECASE):
                current_chapter = stripped
                continue

            # Check for Section / Article start
            m = self.sec_art_pattern.match(stripped)
            if m:
                num = m.group(1) or m.group(2)
                rest = (m.group(3) or "").strip()

                # Filter out footnote lines like "1. Subs. by..." or "2. Ins. by..."
                if rest and self.FOOTNOTE_REJECT_PATTERN.match(rest):
                    if current_lines:
                        current_lines.append(stripped)
                    continue

                # Valid new provision heading
                flush_current()
                current_num = num

                # If the title has inline punctuation or substantive start, clean it
                if "—" in rest or "–" in rest or "" in rest:
                    parts = re.split(r'[—–]', rest, maxsplit=1)
                    current_title = parts[0].strip()
                    substantive_first_line = parts[1].strip() if len(parts) > 1 else ""
                    if substantive_first_line:
                        current_lines.append(substantive_first_line)
                else:
                    current_title = rest
            else:
                if current_num:
                    current_lines.append(stripped)

        # Flush final provision
        flush_current()
        return chunks
