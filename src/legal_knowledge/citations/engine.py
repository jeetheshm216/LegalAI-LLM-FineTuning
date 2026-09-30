"""Indian legal citation formatter, validator, and provenance resolver."""

from typing import Optional, Dict, Any
from ..models import IndianLegalChunk, IndianDocumentType, LegalCitation


class IndianCitationEngine:
    """Formats and validates Indian statutory, constitutional, and judicial citations."""

    def format_citation(self, chunk: IndianLegalChunk) -> LegalCitation:
        """Generates a standardized Indian legal citation from a retrieved chunk."""
        if chunk.document_type == IndianDocumentType.CONSTITUTION:
            cite_str = f"{chunk.section_or_article}, Constitution of India"
            return LegalCitation(
                citation_str=cite_str,
                citation_type="CONSTITUTIONAL",
                act_or_case="Constitution of India",
                section_or_para=chunk.section_or_article,
                court_or_authority="Parliament / Constituent Assembly",
                url=chunk.official_source_url
            )

        elif chunk.document_type == IndianDocumentType.JUDGMENT:
            case_title = chunk.title
            cite_num = chunk.citation or "SCR"
            court_name = chunk.court or "Supreme Court of India"
            year = chunk.decision_date[:4] if chunk.decision_date else None
            cite_str = f"{case_title}, {cite_num} ({court_name})"
            return LegalCitation(
                citation_str=cite_str,
                citation_type="JUDICIAL",
                act_or_case=case_title,
                section_or_para=chunk.section_or_article,
                court_or_authority=court_name,
                year=int(year) if year and year.isdigit() else None,
                reporter=cite_num.split()[1] if " " in cite_num else "SCC",
                url=chunk.official_source_url
            )

        else:
            # Central or State Act / Rule / Regulation
            sec_name = chunk.section_or_article
            act_title = chunk.act_name
            cite_str = f"{sec_name}, {act_title}"
            return LegalCitation(
                citation_str=cite_str,
                citation_type="STATUTORY",
                act_or_case=act_title,
                section_or_para=sec_name,
                court_or_authority="Parliament of India" if chunk.jurisdiction_level.value == "CENTRAL" else f"State Legislature of {chunk.state or 'India'}",
                url=chunk.official_source_url
            )

    def format_lawyer_provenance_block(self, chunk: IndianLegalChunk) -> str:
        """Renders a citation provenance footer suitable for formal advocate pleadings and research notes."""
        cite = self.format_citation(chunk)
        lines = [
            f"**Authority**: {cite.citation_str}",
            f"- **Type**: {chunk.document_type.value} ({chunk.jurisdiction_level.value})",
            f"- **Hierarchy**: {chunk.authority_tier.value}",
            f"- **Temporal Status**: {chunk.temporal_status.value}",
        ]
        if chunk.decision_date:
            lines.append(f"- **Decision Date**: {chunk.decision_date}")
        if chunk.bench:
            lines.append(f"- **Bench**: {chunk.bench}")
        if chunk.state:
            lines.append(f"- **State Jurisdiction**: {chunk.state}")
        if chunk.official_source_url:
            lines.append(f"- **Official Source**: [{chunk.official_source_url}]({chunk.official_source_url})")

        return "\n".join(lines)
