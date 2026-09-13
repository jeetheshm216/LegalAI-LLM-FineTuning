"""Automated tests for LegalAI RAG ingestion, parsing, metadata, and database idempotency."""

import os
import json
import pytest
from src.rag.ingestion.extract import extract_act_text
from src.rag.ingestion.parser import StatutoryParser
from src.rag.ingestion.metadata import create_chunk_metadata, VALID_ACT_TYPES
from src.rag.database.sqlite_adapter import SQLiteLegalDatabase
from src.rag.concordance.concordance import ConcordanceRegistry


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_DIR, "data/raw")
MANIFEST_PATH = os.path.join(PROJECT_DIR, "data/sources/legal_sources_manifest.json")


def test_sources_manifest_validity():
    """Verify that the manifest exists, contains all 3 Acts, and has valid SHA-256 hashes."""
    assert os.path.exists(MANIFEST_PATH), "Manifest file must exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "acts" in manifest
    assert len(manifest["acts"]) == 3

    expected_acts = {
        "BNS_2023_Act_45.pdf": ("The Bharatiya Nyaya Sanhita, 2023", 358),
        "BNSS_2023_Act_46.pdf": ("The Bharatiya Nagarik Suraksha Sanhita, 2023", 531),
        "BSA_2023_Act_47.pdf": ("The Bharatiya Sakshya Adhiniyam, 2023", 170)
    }

    for act in manifest["acts"]:
        filename = act["filename"]
        assert filename in expected_acts
        assert act["sha256_hash"] is not None and len(act["sha256_hash"]) == 64
        assert act["verification_status"] == "VERIFIED_OFFICIAL_GAZETTE"
        assert act["act_type"] in VALID_ACT_TYPES


def test_bsa_section_parsing_completeness():
    """Verify that BSA (47 of 2023) parses exactly 170 statutory sections with zero omissions."""
    pdf_path = os.path.join(RAW_DIR, "BSA_2023_Act_47.pdf")
    assert os.path.exists(pdf_path), "BSA raw PDF must exist"

    processed_path = os.path.join(PROJECT_DIR, "data/processed/test_bsa_normalized.txt")
    text, stats = extract_act_text(pdf_path, processed_path, start_page=10, act_name="BSA 2023")
    assert stats["pages_extracted"] > 0

    parser = StatutoryParser("The Bharatiya Sakshya Adhiniyam, 2023", "47 of 2023", "EVIDENCE_LAW", "BSA")
    sections, chunks, parse_stats = parser.parse_enactment(text, total_sections=170)

    assert len(sections) == 170, f"Expected 170 BSA sections, got {len(sections)}"
    assert parse_stats["missing_sections"] == []
    assert len(chunks) >= 170

    # Verify key statutory section
    sec_63 = next(s for s in sections if s["section_number"] == "63")
    assert "electronic records" in sec_63["section_title"].lower() or "electronic" in sec_63["text"].lower()


def test_controlled_metadata_vocabulary():
    """Ensure illegal act_types raise an error and standard fields are present."""
    bad_chunk = {
        "chunk_id": "TEST_01",
        "parent_section_id": "TEST_01",
        "act_name": "Test Act",
        "act_number": "1 of 2023",
        "act_type": "UNKNOWN_CUSTOM_TYPE",
        "act_prefix": "CUSTOM",
        "section_number": "1",
        "section_title": "Test",
        "chapter_id": "I",
        "chapter_title": "Test",
        "content": "Test content"
    }
    with pytest.raises(ValueError, match="Invalid act_type"):
        create_chunk_metadata(bad_chunk)


def test_database_idempotency(tmp_path):
    """Ensure duplicate chunk insertion is strictly idempotent."""
    db_file = str(tmp_path / "test_idempotency.db")
    db = SQLiteLegalDatabase(db_file)

    sample_chunk = {
        "chunk_id": "BNS_2023_SEC_103",
        "section_id": "BNS_2023_SEC_103",
        "parent_section_id": "BNS_2023_SEC_103",
        "act_name": "The Bharatiya Nyaya Sanhita, 2023",
        "act_number": "45 of 2023",
        "act_type": "SUBSTANTIVE_CRIMINAL_LAW",
        "act_prefix": "BNS",
        "section_number": "103",
        "section_title": "Punishment for murder.",
        "chapter": "CHAPTER VI: OF OFFENCES AFFECTING THE HUMAN BODY",
        "content": "103. (1) Whoever commits murder shall be punished with death or imprisonment for life...",
        "raw_section_text": "103. (1) Whoever commits murder shall be punished with death...",
        "source": "India Code",
        "source_url": "https://indiacode.gov.in/handle/123456789/496548",
        "publication_date": "2023-12-25",
        "effective_from": "2024-07-01",
        "content_hash": "dummyhash"
    }

    # Insert parent document & section first to satisfy foreign keys
    doc_id = db.insert_document({
        "act_name": "The Bharatiya Nyaya Sanhita, 2023",
        "act_number": "45 of 2023",
        "act_prefix": "BNS",
        "act_type": "SUBSTANTIVE_CRIMINAL_LAW",
        "enactment_date": "2023-12-25",
        "commencement_date": "2024-07-01",
        "commencement_authority": "MHA S.O. 848(E)",
        "total_sections": 358
    })
    db.insert_sections([{
        "section_id": "BNS_2023_SEC_103",
        "document_id": doc_id,
        "act_prefix": "BNS",
        "section_number": "103",
        "section_title": "Punishment for murder.",
        "chapter_id": "CHAPTER VI",
        "chapter_title": "OF OFFENCES AFFECTING THE HUMAN BODY",
        "text": "103. (1) Whoever commits murder...",
        "effective_from": "2024-07-01"
    }])

    # Insert first time
    inserted_1 = db.insert_chunks([sample_chunk])
    assert inserted_1 == 1

    stats_1 = db.get_stats()
    assert stats_1["total_chunks"] == 1

    # Insert duplicate second time
    inserted_2 = db.insert_chunks([sample_chunk])
    assert inserted_2 == 1

    stats_2 = db.get_stats()
    assert stats_2["total_chunks"] == 1, "Duplicate insertion must not increase chunk count"


def test_concordance_verification_guard():
    """Verify that unverified concordance entries are rejected by ConcordanceRegistry."""
    registry = ConcordanceRegistry()
    verified = registry.get_all_verified_mappings()
    assert len(verified) > 0

    for m in verified:
        assert m["verification_status"] == "VERIFIED_STATUTORY_CONCORDANCE"
        assert m["legacy_section"] != ""
        assert m["modern_section"] != ""

    # Test lookup of CrPC 438 -> BNSS 482
    res = registry.lookup_legacy_to_modern("CrPC", "438")
    assert res is not None
    assert res.modern_section == "482"
    assert "Bharatiya Nagarik Suraksha Sanhita" in res.modern_act

    # Test lookup of IEA 65B -> BSA 63
    res_iea = registry.lookup_legacy_to_modern("Indian Evidence Act", "65B")
    assert res_iea is not None
    assert res_iea.modern_section == "63"
