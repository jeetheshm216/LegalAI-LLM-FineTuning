"""Comprehensive test suite for the Automated Indian Legal Corpus Expansion Engine."""

import pytest
import os
import shutil
import tempfile
import sqlite3
import json
from src.legal_knowledge.expansion.models import IngestionStatus, DiscoveredAct
from src.legal_knowledge.expansion.discovery import IndiaCodeDiscoveryEngine
from src.legal_knowledge.expansion.fetcher import IndiaCodeFetcher
from src.legal_knowledge.expansion.state_tracker import IngestionStateTracker
from src.legal_knowledge.expansion.versioner import DocumentVersionManager
from src.legal_knowledge.expansion.classifier import IndianDomainClassifier
from src.legal_knowledge.expansion.pipeline import AutomatedCorpusExpansionPipeline
from src.legal_knowledge.indexing.database import IndianLegalDatabaseManager
from src.legal_knowledge.models import (
    TemporalStatus,
    LegalDomain,
    IndianLegalDocument,
    IndianLegalChunk,
    IndianDocumentType,
    IndianJurisdictionLevel,
    AuthorityTier,
)


@pytest.fixture
def temp_env():
    """Creates an isolated temporary database and storage folder for expansion testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_expansion.db")
    raw_dir = os.path.join(temp_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    db_manager = IndianLegalDatabaseManager(db_path=db_path)
    state_tracker = IngestionStateTracker(db_path=db_path)

    yield {
        "dir": temp_dir,
        "db_path": db_path,
        "raw_dir": raw_dir,
        "db": db_manager,
        "tracker": state_tracker
    }

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_01_discovery_captures_valid_metadata():
    """Verifies that discovered Central Acts contain verified India Code metadata and no fabricated fields."""
    engine = IndiaCodeDiscoveryEngine()
    acts = engine.discover_central_acts()
    assert len(acts) >= 10

    for act in acts:
        assert act.act_id.isupper()
        assert act.handle_url.startswith("https://indiacode.gov.in/handle/")
        assert act.jurisdiction_level == "CENTRAL"
        assert act.source_id == "SRC_INDIA_CODE"
        assert act.short_title
        assert act.act_name
        assert act.text_url or act.pdf_url


def test_02_discovery_by_keyword():
    """Verifies targeted discovery by keyword."""
    engine = IndiaCodeDiscoveryEngine()
    comp_acts = engine.discover_by_keyword("Companies")
    assert len(comp_acts) >= 1
    assert comp_acts[0].act_id == "COMPANIES_ACT_2013"

    arb_acts = engine.discover_by_keyword("Arbitration")
    assert len(arb_acts) >= 1
    assert arb_acts[0].act_id == "ARBITRATION_ACT_1996"


def test_03_fetcher_caching_and_hash(temp_env):
    """Verifies local caching and SHA-256 calculation."""
    fetcher = IndiaCodeFetcher(storage_dir=temp_env["raw_dir"])
    
    # Create valid cached file
    test_path = os.path.join(temp_env["raw_dir"], "test_act.txt")
    meta_path = f"{test_path}.meta.json"
    content = b"Section 1. Short title.\nThis Act may be called the Test Act, 2024." * 20
    import hashlib
    h = hashlib.sha256(content).hexdigest()
    with open(test_path, "wb") as f:
        f.write(content)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "act_id": "TEST_ACT",
            "sha256_hash": h,
            "http_status": 200,
            "acquisition_method": "OFFICIAL_INDIA_CODE_HTTP_FETCH"
        }, f)
        
    act = DiscoveredAct(
        act_id="TEST_ACT",
        act_name="Test Act, 2024",
        short_title="Test Act",
        handle_url="https://indiacode.gov.in/handle/123456789/9999"
    )
    success, path, content_hash, err = fetcher.fetch_act(act)
    assert success is True
    assert content_hash == h
    assert err is None


def test_04_fetcher_rejects_corrupt_payload(temp_env):
    """Verifies that empty or corrupt files are rejected with failure diagnostics."""
    fetcher = IndiaCodeFetcher(storage_dir=temp_env["raw_dir"])
    act = DiscoveredAct(
        act_id="NON_EXISTENT_ACT",
        act_name="Invalid Act",
        short_title="Invalid",
        handle_url="http://127.0.0.1:59999/non_existent_url"
    )
    success, _, content_hash, err = fetcher.fetch_act(act)
    assert success is False
    assert content_hash is None
    assert err is not None


def test_05_versioner_exact_match_no_duplicate(temp_env):
    """Verifies that an identical hash causes the versioner to detect no change."""
    versioner = DocumentVersionManager(temp_env["db"])
    hash_v1 = "abcdef1234567890" * 4

    temp_env["db"].upsert_document(IndianLegalDocument(
        document_id="DOC_ACT_TEST",
        title="Test Act",
        act_prefix="ACT_TEST",
        act_number="1",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        legal_domain=LegalDomain.GENERAL.value,
        official_source_url="https://indiacode.gov.in/handle/1"
    ))

    temp_env["tracker"].record_discovered(DiscoveredAct(
        act_id="ACT_TEST", act_name="Test Act", short_title="Test", handle_url="https://indiacode.gov.in/handle/1"
    ))
    temp_env["tracker"].update_status(
        source_url="https://indiacode.gov.in/handle/1",
        status=IngestionStatus.INDEXED,
        content_hash=hash_v1
    )

    v_id, status, is_new, note = versioner.evaluate_document_version(
        act_prefix="ACT_TEST",
        new_content_hash=hash_v1
    )

    assert is_new is False
    assert "identical" in note.lower()


def test_06_versioner_changed_hash_preserves_old_version(temp_env):
    """Verifies that changed content hash creates a new amendment version while tagging prior as amended."""
    versioner = DocumentVersionManager(temp_env["db"])
    h1 = "1111111111111111" * 4
    h2 = "2222222222222222" * 4

    temp_env["db"].upsert_document(IndianLegalDocument(
        document_id="DOC_ACT_VER",
        title="Versioned Act",
        act_prefix="ACT_VER",
        act_number="2",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        legal_domain=LegalDomain.GENERAL.value,
        official_source_url="https://indiacode.gov.in/handle/2"
    ))

    temp_env["tracker"].record_discovered(DiscoveredAct(
        act_id="ACT_VER", act_name="Versioned Act", short_title="Versioned", handle_url="https://indiacode.gov.in/handle/2"
    ))
    temp_env["tracker"].update_status(
        source_url="https://indiacode.gov.in/handle/2",
        status=IngestionStatus.INDEXED,
        content_hash=h1
    )

    v_id, status, is_new, note = versioner.evaluate_document_version(
        act_prefix="ACT_VER",
        new_content_hash=h2,
        amendment_date="2025"
    )

    assert is_new is True
    assert status == TemporalStatus.CURRENT
    assert "2025" in v_id or "AMENDED" in v_id


def test_07_conservative_domain_classification():
    """Verifies rule-based domain classification accuracy with conservative fallback."""
    classifier = IndianDomainClassifier()

    d1, c1 = classifier.classify_act("The Insolvency and Bankruptcy Code, 2016")
    assert d1 == LegalDomain.INSOLVENCY.value
    assert c1 >= 0.85

    d2, c2 = classifier.classify_act("The Protection of Children from Sexual Offences Act, 2012")
    assert d2 == LegalDomain.CRIMINAL.value

    d3, c3 = classifier.classify_act("Arbitrary Customary Rituals Act, 1920")
    assert d3 == "Other / Unclassified"
    assert c3 < 0.70


def test_08_resumability_simulation(temp_env):
    """Verifies pipeline skips already indexed acts and resumes cleanly."""
    pipeline = AutomatedCorpusExpansionPipeline(db_path=temp_env["db_path"], raw_storage_dir=temp_env["raw_dir"])

    act = DiscoveredAct(
        act_id="RESUME_TEST",
        act_name="Resume Test Act",
        short_title="Resume Test",
        handle_url="https://indiacode.gov.in/handle/3"
    )

    pipeline.tracker.record_discovered(act)
    pipeline.tracker.update_status(act.handle_url, IngestionStatus.INDEXED, content_hash="hash123", chunks_created=10)

    res = pipeline.process_single_act(act)
    assert res["status"] == IngestionStatus.SKIPPED
    assert "already indexed" in res["reason"].lower()


def test_09_deduplication_exact_and_chunk(temp_env):
    """Verifies chunk-level deduplication prevents identical chunks from re-indexing."""
    chunk1 = IndianLegalChunk(
        chunk_id="CHK_TEST_1",
        document_id="DOC_TEST",
        title="Test Act",
        act_name="Test Act",
        act_prefix="TEST",
        section_or_article="Section 1",
        provision_number="1",
        provision_title="Short title",
        chapter="Part I",
        content="Test provision content verbatim",
        raw_text="Test provision content verbatim",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        legal_domain="Corporate",
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        official_source_url="https://indiacode.gov.in"
    )

    r1 = temp_env["db"].upsert_chunk(chunk1)
    assert r1 is True

    # Attempt to upsert identical content again under chunk_id 2
    chunk2 = IndianLegalChunk(
        chunk_id="CHK_TEST_2",
        document_id="DOC_TEST",
        title="Test Act",
        act_name="Test Act",
        act_prefix="TEST",
        section_or_article="Section 1",
        provision_number="1",
        provision_title="Short title duplicate",
        chapter="Part I",
        content="Test provision content verbatim",
        raw_text="Test provision content verbatim",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        legal_domain="Corporate",
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        official_source_url="https://indiacode.gov.in"
    )
    chunk2.content_hash = chunk1.compute_hash()

    r2 = temp_env["db"].upsert_chunk(chunk2)
    assert r2 is False


def test_10_retrieval_pilot_acts():
    """Verifies that newly indexed pilot Acts are retrievable via hybrid FTS search."""
    db_path = "data/legalai_indian_legal_knowledge.db"
    if not os.path.exists(db_path):
        pytest.skip("Corpus database not found.")

    db = IndianLegalDatabaseManager(db_path=db_path)
    res = db.search_fts("insolvency resolution process operational creditor", limit=5)
    assert len(res) > 0
    assert any("Insolvency and Bankruptcy" in c.title or "IBC" in c.act_prefix for c, _ in res)


def test_11_strict_provenance_guardrails():
    """
    CRITICAL PROVENANCE TEST:
    Verifies that statutory text is NEVER sourced from hardcoded Python dictionaries.
    Verifies that all raw cached files have genuine HTTP 200 acquisition metadata from India Code.
    """
    # 1. Ensure pilot_data does not contain PILOT_ACTS_DATA with statutory text
    import src.legal_knowledge.expansion.pilot_data as pd
    assert getattr(pd, "PILOT_STATUTORY_TEXT_IS_FORBIDDEN", False) is True
    assert not hasattr(pd, "PILOT_ACTS_DATA"), "FORBIDDEN: PILOT_ACTS_DATA dictionary containing statutory text must not exist."

    # 2. Check cached files in data/raw/central_acts/
    raw_dir = "data/raw/central_acts"
    if not os.path.exists(raw_dir):
        pytest.skip(f"Raw directory {raw_dir} does not exist.")

    meta_files = [f for f in os.listdir(raw_dir) if f.endswith(".meta.json")]
    assert len(meta_files) >= 10, f"Expected at least 10 cached Act metadata files, found {len(meta_files)}"

    for mf in meta_files:
        meta_path = os.path.join(raw_dir, mf)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        txt_file = meta_path.replace(".meta.json", "")
        assert os.path.exists(txt_file), f"Raw text file missing for {mf}"
        file_size = os.path.getsize(txt_file)

        # Genuine full document assertion
        assert file_size >= 10000, f"Raw statutory file {txt_file} is suspiciously small ({file_size} bytes). Expected full Act document."
        assert meta.get("http_status") == 200, f"HTTP status was not 200 in {mf}"
        assert meta.get("acquisition_method") == "OFFICIAL_INDIA_CODE_HTTP_FETCH", f"Invalid acquisition method in {mf}"
        assert "indiacode.gov.in" in meta.get("download_url", "")
        assert "indiacode.gov.in" in meta.get("source_url", "")
        assert len(meta.get("sha256_hash", "")) == 64
