"""Data schemas and domain taxonomy for General Indian Legal Knowledge RAG."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import hashlib
import json


class IndianJurisdictionLevel(str, Enum):
    CENTRAL = "CENTRAL"
    STATE = "STATE"
    SUPREME_COURT = "SUPREME_COURT"
    HIGH_COURT = "HIGH_COURT"
    TRIBUNAL_REGULATORY = "TRIBUNAL_REGULATORY"


class IndianDocumentType(str, Enum):
    ACT = "ACT"
    CONSTITUTION = "CONSTITUTION"
    RULE = "RULE"
    REGULATION = "REGULATION"
    NOTIFICATION = "NOTIFICATION"
    CIRCULAR = "CIRCULAR"
    ORDER = "ORDER"
    JUDGMENT = "JUDGMENT"
    STATUTORY_INSTRUMENT = "STATUTORY_INSTRUMENT"


class ProvisionType(str, Enum):
    SECTION = "SECTION"
    ARTICLE = "ARTICLE"
    ORDER_RULE = "ORDER_RULE"
    REGULATION = "REGULATION"
    SCHEDULE_ITEM = "SCHEDULE_ITEM"
    CLAUSE = "CLAUSE"
    NOTIFICATION = "NOTIFICATION"
    JUDGMENT = "JUDGMENT"
    ACT = "ACT"


class AuthorityTier(str, Enum):
    TIER_1_PRIMARY = "TIER_1_PRIMARY"        # Central Acts, Constitution, Supreme Court, Gazette
    TIER_2_REGULATORY_STATE = "TIER_2_REGULATORY_STATE"  # High Court judgments, State Acts, Subordinate Rules, RBI/SEBI
    TIER_3_SECONDARY = "TIER_3_SECONDARY"      # Law Commission Reports, Institutional treatises


class TemporalStatus(str, Enum):
    CURRENT = "CURRENT"
    AMENDED = "AMENDED"
    REPEALED = "REPEALED"
    HISTORICAL = "HISTORICAL"
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    STRUCK_DOWN = "STRUCK_DOWN"               # Provision declared unconstitutional by SC/HC
    UNKNOWN = "UNKNOWN"


class LegalDomain(str, Enum):
    CRIMINAL = "Criminal Law"
    CIVIL = "Civil Law"
    CONSTITUTIONAL = "Constitutional Law"
    CONTRACT = "Contract Law"
    CORPORATE = "Corporate Law"
    COMMERCIAL = "Commercial Law"
    BANKING_FINANCE = "Banking & Financial Law"
    TAX = "Tax Law"
    PROPERTY = "Property Law"
    FAMILY = "Family Law"
    LABOUR = "Labour & Employment Law"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    CYBER_TECH = "Cyber & Technology Law"
    DATA_PROTECTION = "Data Protection & Privacy"
    CONSUMER = "Consumer Law"
    ARBITRATION = "Arbitration & Conciliation"
    INSOLVENCY = "Insolvency & Bankruptcy"
    COMPETITION = "Competition Law"
    EVIDENCE = "Evidence Law"
    PROCEDURAL = "Procedural Law"
    ADMINISTRATIVE = "Administrative Law"
    HUMAN_RIGHTS = "Human Rights"
    MOTOR_VEHICLES = "Motor Vehicle Law"
    REAL_ESTATE = "Real Estate Law"
    ENVIRONMENTAL = "Environmental Law"
    GENERAL = "General Indian Law"


@dataclass
class LegalCitation:
    citation_str: str
    citation_type: str = "STATUTORY"  # STATUTORY, JUDICIAL, GAZETTE
    act_or_case: str = ""
    section_or_para: Optional[str] = None
    court_or_authority: Optional[str] = None
    year: Optional[int] = None
    reporter: Optional[str] = None       # e.g., SCC, AIR, SCR, Gazette
    url: Optional[str] = None


@dataclass
class IndianLegalDocument:
    document_id: str
    title: str
    document_type: IndianDocumentType
    jurisdiction_level: IndianJurisdictionLevel
    country: str = "India"
    state: Optional[str] = None
    court: Optional[str] = None
    bench: Optional[str] = None
    judges: List[str] = field(default_factory=list)
    act_prefix: Optional[str] = None
    act_number: Optional[str] = None
    enactment_date: Optional[str] = None
    commencement_date: Optional[str] = None
    legal_domain: str = LegalDomain.GENERAL.value
    authority_tier: AuthorityTier = AuthorityTier.TIER_1_PRIMARY
    temporal_status: TemporalStatus = TemporalStatus.CURRENT
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None
    amended_by: Optional[str] = None
    repealed_by: Optional[str] = None
    struck_down_by: Optional[str] = None
    official_source_url: str = ""
    source_id: str = ""
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "document_type": self.document_type.value if hasattr(self.document_type, 'value') else str(self.document_type),
            "jurisdiction_level": self.jurisdiction_level.value if hasattr(self.jurisdiction_level, 'value') else str(self.jurisdiction_level),
            "country": self.country,
            "state": self.state,
            "court": self.court,
            "bench": self.bench,
            "judges": json.dumps(self.judges),
            "act_prefix": self.act_prefix,
            "act_number": self.act_number,
            "enactment_date": self.enactment_date,
            "commencement_date": self.commencement_date,
            "legal_domain": self.legal_domain,
            "authority_tier": self.authority_tier.value if hasattr(self.authority_tier, 'value') else str(self.authority_tier),
            "temporal_status": self.temporal_status.value if hasattr(self.temporal_status, 'value') else str(self.temporal_status),
            "effective_from": self.effective_from,
            "effective_until": self.effective_until,
            "amended_by": self.amended_by,
            "repealed_by": self.repealed_by,
            "struck_down_by": self.struck_down_by,
            "official_source_url": self.official_source_url,
            "source_id": self.source_id,
            "created_at": self.created_at,
        }


@dataclass
class IndianLegalChunk:
    chunk_id: str
    document_id: str
    title: str
    act_name: str
    act_prefix: str
    section_or_article: str
    provision_number: str
    provision_title: str
    chapter: str
    content: str
    raw_text: str
    provision_type: ProvisionType = ProvisionType.SECTION
    document_type: IndianDocumentType = IndianDocumentType.ACT
    jurisdiction_level: IndianJurisdictionLevel = IndianJurisdictionLevel.CENTRAL
    country: str = "India"
    state: Optional[str] = None
    court: Optional[str] = None
    bench: Optional[str] = None
    citation: Optional[str] = None
    decision_date: Optional[str] = None
    legal_domain: str = LegalDomain.GENERAL.value
    authority_tier: AuthorityTier = AuthorityTier.TIER_1_PRIMARY
    temporal_status: TemporalStatus = TemporalStatus.CURRENT
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None
    transition_note: Optional[str] = None
    official_source_url: str = ""
    content_hash: str = ""
    embedding_blob: Optional[bytes] = None

    def compute_hash(self) -> str:
        ptype = self.provision_type.value if hasattr(self.provision_type, 'value') else str(self.provision_type)
        data = f"{self.document_id}_{ptype}_{self.provision_number}_{self.content.strip()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "title": self.title,
            "act_name": self.act_name,
            "act_prefix": self.act_prefix,
            "provision_type": self.provision_type.value if hasattr(self.provision_type, 'value') else str(self.provision_type),
            "section_or_article": self.section_or_article,
            "provision_number": self.provision_number,
            "provision_title": self.provision_title,
            "chapter": self.chapter,
            "content": self.content,
            "raw_text": self.raw_text,
            "document_type": self.document_type.value if hasattr(self.document_type, 'value') else str(self.document_type),
            "jurisdiction_level": self.jurisdiction_level.value if hasattr(self.jurisdiction_level, 'value') else str(self.jurisdiction_level),
            "country": self.country,
            "state": self.state,
            "court": self.court,
            "bench": self.bench,
            "citation": self.citation,
            "decision_date": self.decision_date,
            "legal_domain": self.legal_domain,
            "authority_tier": self.authority_tier.value if hasattr(self.authority_tier, 'value') else str(self.authority_tier),
            "temporal_status": self.temporal_status.value if hasattr(self.temporal_status, 'value') else str(self.temporal_status),
            "effective_from": self.effective_from,
            "effective_until": self.effective_until,
            "transition_note": self.transition_note,
            "official_source_url": self.official_source_url,
            "content_hash": self.content_hash or self.compute_hash(),
        }


@dataclass
class IndianLegalNotification:
    notification_id: str
    notification_number: str
    date: str
    issuing_authority: str
    subject: str
    source_url: str
    effective_date: Optional[str] = None
    affected_act: Optional[str] = None
    affected_provision: Optional[str] = None
    document_id: Optional[str] = None
    content_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "notification_number": self.notification_number,
            "date": self.date,
            "issuing_authority": self.issuing_authority,
            "subject": self.subject,
            "source_url": self.source_url,
            "effective_date": self.effective_date,
            "affected_act": self.affected_act,
            "affected_provision": self.affected_provision,
            "document_id": self.document_id,
            "content_hash": self.content_hash,
        }


@dataclass
class IndianLegalAmendment:
    amendment_id: str
    act_id: str
    act_name: str
    amending_act_number: str
    amending_act_year: int
    effective_date: str
    sections_modified: List[str] = field(default_factory=list)
    source_url: str = ""


@dataclass
class StructuredLegalQuery:
    intent: str  # EXACT_PROVISION_QUERY, AMBIGUOUS_PROVISION, GENERAL_LEGAL, ACT_OVERVIEW, JUDGMENT_QUERY, NOTIFICATION_QUERY
    entity_type: Optional[str] = None
    act: Optional[str] = None
    act_prefix: Optional[str] = None
    provision_type: Optional[ProvisionType] = None
    provision_number: Optional[str] = None
    subclause: Optional[str] = None
    temporal_reference: Optional[str] = None
    context_reference: Optional[str] = None
    confidence: float = 1.0
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


@dataclass
class SearchFilter:
    jurisdiction_level: Optional[IndianJurisdictionLevel] = None
    state: Optional[str] = None
    court: Optional[str] = None
    authority_tier: Optional[AuthorityTier] = None
    temporal_status: Optional[TemporalStatus] = None
    legal_domain: Optional[str] = None
    incident_date: Optional[str] = None
    act_prefix: Optional[str] = None
    provision_type: Optional[ProvisionType] = None
    provision_number: Optional[str] = None
