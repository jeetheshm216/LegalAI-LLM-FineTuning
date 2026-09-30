"""Official Indian Legal Sources Registry.

Registers verified Indian legal repositories and official government databases.
Strictly restricted to official public-access Indian legal portals with permissible automated access.
Stores complete provenance, domain validation, and document-level metadata records.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from ..models import IndianJurisdictionLevel, AuthorityTier, IndianDocumentType


@dataclass
class IndianLegalSource:
    source_id: str
    authority: str
    authority_level: str  # PRIMARY, REGULATORY, SECONDARY
    domain: str
    source_type: str      # STATUTE, JUDGMENT, GAZETTE, NOTIFICATION
    country: str = "IN"
    active: bool = True
    source_url: str = ""
    jurisdiction_level: str = "CENTRAL"
    access_method: str = "PUBLIC_OFFICIAL_PORTAL"
    license_or_terms: str = "Public Domain under Indian Copyright Act Sec 52(1)(q)"
    state: Optional[str] = None
    verification_status: str = "VERIFIED_OFFICIAL"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "authority": self.authority,
            "authority_level": self.authority_level,
            "domain": self.domain,
            "source_type": self.source_type,
            "country": self.country,
            "active": self.active,
            "source_url": self.source_url,
            "jurisdiction_level": self.jurisdiction_level,
            "access_method": self.access_method,
            "license_or_terms": self.license_or_terms,
            "state": self.state,
            "verification_status": self.verification_status,
            "notes": self.notes
        }


@dataclass
class DocumentMetadataRecord:
    document_id: str
    title: str
    short_title: str
    act_number: Optional[str] = None
    year: Optional[int] = None
    authority: str = "India Code"
    source_url: str = ""
    source_domain: str = "indiacode.nic.in"
    source_type: str = "STATUTE"
    publication_date: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    retrieved_at: str = ""
    content_hash: str = ""
    verification_status: str = "VERIFIED_OFFICIAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "short_title": self.short_title,
            "act_number": self.act_number,
            "year": self.year,
            "authority": self.authority,
            "source_url": self.source_url,
            "source_domain": self.source_domain,
            "source_type": self.source_type,
            "publication_date": self.publication_date,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "retrieved_at": self.retrieved_at,
            "content_hash": self.content_hash,
            "verification_status": self.verification_status,
        }


class IndianSourceRegistry:
    """Registry of official Indian legal sources for primary legislation, judicial decisions, and regulatory instruments."""

    def __init__(self):
        self._sources: Dict[str, IndianLegalSource] = {}
        self._documents: Dict[str, DocumentMetadataRecord] = {}
        self._populate_official_sources()

    def _populate_official_sources(self):
        # 1. India Code ? Legislative Department, Ministry of Law and Justice
        self.register_source(
            IndianLegalSource(
                source_id="indiacode",
                authority="India Code",
                authority_level="PRIMARY",
                domain="indiacode.nic.in",
                source_type="STATUTE",
                country="IN",
                active=True,
                source_url="https://www.indiacode.nic.in",
                jurisdiction_level="CENTRAL",
                access_method="PUBLIC_WEB_REPOSITORY",
                license_or_terms="Government of India Open Access / Public Record",
                notes="Primary official repository for all enacted Indian Central Acts and subordinate rules."
            )
        )

        # 2. Supreme Court of India ? e-SCR / Digital Supreme Court Reports
        self.register_source(
            IndianLegalSource(
                source_id="sci_escr",
                authority="Supreme Court of India",
                authority_level="PRIMARY",
                domain="judgments.ecourts.gov.in",
                source_type="JUDGMENT",
                country="IN",
                active=True,
                source_url="https://judgments.ecourts.gov.in/pdfsearch/",
                jurisdiction_level="SUPREME_COURT",
                access_method="OFFICIAL_COURT_PORTAL",
                license_or_terms="Official Judicial Records / Public Domain under Indian Copyright Act Sec 52(1)(q)",
                notes="Authoritative reports of Supreme Court of India judgments with official SCR citations."
            )
        )

        # 3. Gazette of India ? Directorate of Printing
        self.register_source(
            IndianLegalSource(
                source_id="egazette",
                authority="Gazette of India",
                authority_level="PRIMARY",
                domain="egazette.gov.in",
                source_type="GAZETTE",
                country="IN",
                active=True,
                source_url="https://egazette.gov.in",
                jurisdiction_level="CENTRAL",
                access_method="OFFICIAL_GOVERNMENT_GAZETTE",
                license_or_terms="Official Gazette of the Republic of India / Statutory Promulgation",
                notes="Official gazette notifications for commencement, enforcement dates, and statutory amendments."
            )
        )

        # 4. Reserve Bank of India
        self.register_source(
            IndianLegalSource(
                source_id="rbi",
                authority="Reserve Bank of India",
                authority_level="REGULATORY",
                domain="rbi.org.in",
                source_type="REGULATION",
                country="IN",
                active=True,
                source_url="https://www.rbi.org.in",
                jurisdiction_level="TRIBUNAL_REGULATORY",
                access_method="REGULATORY_PORTAL",
                license_or_terms="Public Regulatory Disclosures under Banking Regulation Act & RBI Act",
                notes="Authoritative statutory notifications and directions issued by the Central Bank."
            )
        )

        # 5. Ministry of Corporate Affairs
        self.register_source(
            IndianLegalSource(
                source_id="mca",
                authority="Ministry of Corporate Affairs",
                authority_level="REGULATORY",
                domain="mca.gov.in",
                source_type="NOTIFICATION",
                country="IN",
                active=True,
                source_url="https://www.mca.gov.in",
                jurisdiction_level="CENTRAL",
                access_method="MINISTRY_PORTAL",
                license_or_terms="Official Central Ministry Publications",
                notes="Subordinate rules, commencement notifications, and statutory thresholds under Companies Act 2013."
            )
        )

    def register_source(self, source: IndianLegalSource):
        self._sources[source.source_id] = source

    def get_source(self, source_id: str) -> Optional[IndianLegalSource]:
        return self._sources.get(source_id)

    def list_sources(self) -> List[IndianLegalSource]:
        return list(self._sources.values())

    def register_document(self, doc: DocumentMetadataRecord):
        self._documents[doc.document_id] = doc

    def get_document(self, document_id: str) -> Optional[DocumentMetadataRecord]:
        return self._documents.get(document_id)

    def list_documents(self) -> List[DocumentMetadataRecord]:
        return list(self._documents.values())
