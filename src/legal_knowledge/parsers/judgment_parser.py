"""Parser for Indian Judicial Decisions (Supreme Court of India, High Courts)."""

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


class IndianJudgmentParser:
    """Parses Indian judgments into authoritative legal precedent chunks with case metadata."""

    def parse_judgment(
        self,
        document: IndianLegalDocument,
        citation: str,
        decision_date: str,
        acts_discussed: List[str],
        sections_discussed: List[str],
        headnote_or_summary: str,
        ratio_decidendi: str,
        operative_order: Optional[str] = None
    ) -> List[IndianLegalChunk]:
        """Creates indexed chunks representing the ratio decidendi, headnote, and legal principles of a judgment."""
        chunks: List[IndianLegalChunk] = []

        # Chunk 1: Headnote & Legal Principles
        doc_prefix = document.act_prefix or "JUDGMENT"
        chunk_1_id = f"{doc_prefix}_HEADNOTE"
        headnote_content = (
            f"IN THE {document.court.upper() if document.court else 'SUPREME COURT OF INDIA'}\n"
            f"Case: {document.title}\n"
            f"Citation: {citation}\n"
            f"Decision Date: {decision_date}\n"
            f"Bench: {document.bench or 'Bench'}\n"
            f"Coram: {', '.join(document.judges) if document.judges else 'Honorable Judges'}\n"
            f"Statutes Discussed: {', '.join(acts_discussed)}\n"
            f"Provisions: {', '.join(sections_discussed)}\n\n"
            f"LEGAL ISSUES & HEADNOTE:\n{headnote_or_summary}"
        )

        chunk_1 = IndianLegalChunk(
            chunk_id=chunk_1_id,
            document_id=document.document_id,
            title=document.title,
            act_name=document.title,
            act_prefix=doc_prefix,
            section_or_article="Headnote",
            provision_number="HN",
            provision_title="Legal Principles & Issues",
            chapter="Judicial Precedent",
            content=headnote_content,
            raw_text=headnote_or_summary,
            document_type=IndianDocumentType.JUDGMENT,
            jurisdiction_level=document.jurisdiction_level,
            country="India",
            state=document.state,
            court=document.court,
            bench=document.bench,
            citation=citation,
            decision_date=decision_date,
            legal_domain=document.legal_domain,
            authority_tier=document.authority_tier,
            temporal_status=document.temporal_status,
            effective_from=decision_date,
            transition_note=f"Judicial Precedent: {citation}",
            official_source_url=document.official_source_url
        )
        chunk_1.content_hash = chunk_1.compute_hash()
        chunks.append(chunk_1)

        # Chunk 2: Ratio Decidendi & Binding Holding
        chunk_2_id = f"{doc_prefix}_RATIO"
        ratio_content = (
            f"IN THE {document.court.upper() if document.court else 'SUPREME COURT OF INDIA'}\n"
            f"Case: {document.title} | Citation: {citation}\n\n"
            f"RATIO DECIDENDI & BINDING PRECEDENT:\n{ratio_decidendi}"
        )
        if operative_order:
            ratio_content += f"\n\nOPERATIVE ORDER:\n{operative_order}"

        chunk_2 = IndianLegalChunk(
            chunk_id=chunk_2_id,
            document_id=document.document_id,
            title=document.title,
            act_name=document.title,
            act_prefix=doc_prefix,
            section_or_article="Ratio Decidendi",
            provision_number="RATIO",
            provision_title="Binding Precedent & Holding",
            chapter="Binding Ruling",
            content=ratio_content,
            raw_text=ratio_decidendi,
            document_type=IndianDocumentType.JUDGMENT,
            jurisdiction_level=document.jurisdiction_level,
            country="India",
            state=document.state,
            court=document.court,
            bench=document.bench,
            citation=citation,
            decision_date=decision_date,
            legal_domain=document.legal_domain,
            authority_tier=document.authority_tier,
            temporal_status=document.temporal_status,
            effective_from=decision_date,
            transition_note=f"Binding Precedent under Article 141 Constitution of India ({citation})",
            official_source_url=document.official_source_url
        )
        chunk_2.content_hash = chunk_2.compute_hash()
        chunks.append(chunk_2)

        return chunks
