"""Metadata enrichment and controlled vocabulary enforcement for LegalAI RAG."""

import hashlib
from typing import Dict, Any

VALID_ACT_TYPES = {
    "SUBSTANTIVE_CRIMINAL_LAW",
    "CRIMINAL_PROCEDURE",
    "EVIDENCE_LAW"
}

ACT_METADATA_REGISTRY = {
    "BNS": {
        "act_name": "The Bharatiya Nyaya Sanhita, 2023",
        "act_number": "45 of 2023",
        "act_type": "SUBSTANTIVE_CRIMINAL_LAW",
        "official_domain": "indiacode.gov.in",
        "source": "Legislative Department, Ministry of Law and Justice, Government of India",
        "source_url": "https://indiacode.gov.in/handle/123456789/496548",
        "publication_date": "2023-12-25",
        "effective_from": "2024-07-01",
        "effective_to": None,
        "document_version": "1.0-ORIGINAL-ENACTMENT",
        "jurisdiction": "INDIA_CENTRAL",
        "language": "EN",
        "authority_level": "PARLIAMENTARY_ACT",
        "is_current": True,
        "commencement_notification": "Ministry of Home Affairs Notification S.O. 848(E) dated 23-02-2024"
    },
    "BNSS": {
        "act_name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
        "act_number": "46 of 2023",
        "act_type": "CRIMINAL_PROCEDURE",
        "official_domain": "indiacode.gov.in",
        "source": "Legislative Department, Ministry of Law and Justice, Government of India",
        "source_url": "https://indiacode.gov.in/handle/123456789/496550",
        "publication_date": "2023-12-25",
        "effective_from": "2024-07-01",
        "effective_to": None,
        "document_version": "1.0-ORIGINAL-ENACTMENT",
        "jurisdiction": "INDIA_CENTRAL",
        "language": "EN",
        "authority_level": "PARLIAMENTARY_ACT",
        "is_current": True,
        "commencement_notification": "Ministry of Home Affairs Notification S.O. 849(E) dated 23-02-2024"
    },
    "BSA": {
        "act_name": "The Bharatiya Sakshya Adhiniyam, 2023",
        "act_number": "47 of 2023",
        "act_type": "EVIDENCE_LAW",
        "official_domain": "indiacode.gov.in",
        "source": "Legislative Department, Ministry of Law and Justice, Government of India",
        "source_url": "https://indiacode.gov.in/handle/123456789/496549",
        "publication_date": "2023-12-25",
        "effective_from": "2024-07-01",
        "effective_to": None,
        "document_version": "1.0-ORIGINAL-ENACTMENT",
        "jurisdiction": "INDIA_CENTRAL",
        "language": "EN",
        "authority_level": "PARLIAMENTARY_ACT",
        "is_current": True,
        "commencement_notification": "Ministry of Home Affairs Notification S.O. 850(E) dated 23-02-2024"
    }
}


def create_chunk_metadata(chunk: Dict[str, Any], raw_manifest_entry: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Enriches a statutory chunk with validated metadata and controlled vocabulary.
    """
    act_prefix = chunk.get("act_prefix")
    reg = ACT_METADATA_REGISTRY.get(act_prefix, {})
    
    act_type = reg.get("act_type", chunk.get("act_type"))
    if act_type not in VALID_ACT_TYPES:
        raise ValueError(f"Invalid act_type '{act_type}'. Must be one of: {VALID_ACT_TYPES}")
        
    content_bytes = chunk["content"].encode("utf-8")
    content_hash = hashlib.sha256(content_bytes).hexdigest()
    
    retrieval_date = "2026-09-13T11:22:55"
    if raw_manifest_entry and "retrieval_timestamp" in raw_manifest_entry:
        retrieval_date = raw_manifest_entry["retrieval_timestamp"]
        
    metadata = {
        "chunk_id": chunk["chunk_id"],
        "section_id": chunk.get("section_id", chunk["parent_section_id"]),
        "parent_section_id": chunk["parent_section_id"],
        "act_name": reg.get("act_name", chunk["act_name"]),
        "act_number": reg.get("act_number", chunk["act_number"]),
        "act_prefix": act_prefix,
        "act_type": act_type,
        "section_number": chunk["section_number"],
        "section_title": chunk["section_title"],
        "chapter": f"{chunk['chapter_id']}: {chunk['chapter_title']}",
        "chapter_id": chunk["chapter_id"],
        "chapter_title": chunk["chapter_title"],
        "chunk_index": chunk.get("chunk_index", 0),
        "total_chunks": chunk.get("total_chunks", 1),
        "content": chunk["content"],
        "document_version": reg.get("document_version", "1.0-ORIGINAL-ENACTMENT"),
        "source": reg.get("source", "India Code"),
        "source_url": reg.get("source_url", ""),
        "publication_date": reg.get("publication_date", "2023-12-25"),
        "effective_from": reg.get("effective_from", "2024-07-01"),
        "effective_to": reg.get("effective_to"),
        "is_current": reg.get("is_current", True),
        "amendment_date": None,
        "jurisdiction": reg.get("jurisdiction", "INDIA_CENTRAL"),
        "language": reg.get("language", "EN"),
        "retrieval_date": retrieval_date,
        "content_hash": content_hash,
        "authority_level": reg.get("authority_level", "PARLIAMENTARY_ACT")
    }
    
    return metadata
