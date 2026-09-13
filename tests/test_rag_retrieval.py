"""Automated tests for LegalAI RAG retrieval, filtering, citation, and legal boundaries."""

import os
import pytest
from src.rag.database.sqlite_adapter import SQLiteLegalDatabase
from src.rag.retrieval.retriever import LegalRetriever
from src.rag.citation.citation import format_legal_citation


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data/legalai_rag_mvp.db")


@pytest.fixture
def retriever():
    """Provides a LegalRetriever instance against the ingested database."""
    if not os.path.exists(DB_PATH):
        pytest.skip("MVP database not found. Ingestion must run first.")
    db = SQLiteLegalDatabase(DB_PATH)
    return LegalRetriever(db=db, embedder=None)  # Tests lexical & filtering capabilities


def test_bns_substantive_query_retrieves_bns(retriever):
    """Test 1: Query for substantive murder provision retrieves BNS rather than BNSS/BSA."""
    results = retriever.retrieve(
        query="Whoever commits murder shall be punished with death or imprisonment for life",
        mode="lexical",
        top_k=5
    )
    assert len(results) > 0
    top = results[0]
    assert top.act_prefix == "BNS", f"Expected BNS for murder substantive law, got {top.act_prefix}"
    assert top.act_type == "SUBSTANTIVE_CRIMINAL_LAW"
    retrieved_sections = [r.section for r in results]
    assert "103" in retrieved_sections, f"Expected Section 103 in retrieved results, got {retrieved_sections}"


def test_bnss_procedural_query_retrieves_bnss(retriever):
    """Test 2: Query for anticipatory bail retrieves BNSS Section 482."""
    results = retriever.retrieve(
        query="Direction for grant of bail to person apprehending arrest",
        mode="lexical",
        top_k=5
    )
    assert len(results) > 0
    top = results[0]
    assert top.act_prefix == "BNSS", f"Expected BNSS for procedural bail, got {top.act_prefix}"
    assert top.act_type == "CRIMINAL_PROCEDURE"
    assert top.section == "482"


def test_bsa_evidence_query_retrieves_bsa(retriever):
    """Test 3: Query for electronic records admissibility retrieves BSA Section 63."""
    results = retriever.retrieve(
        query="Admissibility of electronic records certificate information produced by computer",
        mode="lexical",
        top_k=5
    )
    assert len(results) > 0
    top = results[0]
    assert top.act_prefix == "BSA", f"Expected BSA for electronic evidence, got {top.act_prefix}"
    assert top.act_type == "EVIDENCE_LAW"
    assert top.section == "63"


def test_explicit_act_filter(retriever):
    """Test 4: Explicit act filter restricts retrieval strictly to the designated Act."""
    results = retriever.retrieve(
        query="police report investigation",
        act_filter="BNSS",
        mode="lexical",
        top_k=5
    )
    assert len(results) > 0
    for r in results:
        assert r.act_prefix == "BNSS"


def test_explicit_section_filter(retriever):
    """Test 5: Explicit section filter retrieves the exact requested section."""
    results = retriever.retrieve(
        query="punishment",
        act_filter="BNS",
        section_filter="103",
        mode="lexical",
        top_k=5
    )
    assert len(results) > 0
    assert results[0].section == "103"
    assert results[0].act_prefix == "BNS"


def test_effective_date_temporal_filter(retriever):
    """Test 6: Effective date filter accurately enforces July 1, 2024 commencement cutoff."""
    # Before commencement date (e.g. 2024-01-01): 2023 Sanhitas were not yet in force
    results_pre = retriever.retrieve(
        query="murder",
        act_filter="BNS",
        section_filter="103",
        effective_date="2024-01-01",
        mode="lexical"
    )
    assert len(results_pre) == 0, "No 2023 Sanhita provision should be returned for date prior to 2024-07-01"

    # On or after commencement date (e.g. 2024-07-01 or 2024-09-01): Sanhitas are active
    results_post = retriever.retrieve(
        query="murder",
        act_filter="BNS",
        section_filter="103",
        effective_date="2024-07-15",
        mode="lexical"
    )
    assert len(results_post) > 0
    assert results_post[0].section == "103"


def test_metadata_survival_and_traceability(retriever):
    """Test 7 & 8: Metadata integrity survives through retrieval to citation formatting."""
    results = retriever.retrieve(
        query="electronic records",
        act_filter="BSA",
        section_filter="63",
        mode="lexical",
        top_k=1
    )
    assert len(results) == 1
    top = results[0]

    # Verify metadata fields
    assert top.source == "India Code" or "Legislative Department" in top.source
    assert top.source_url.startswith("https://indiacode.gov.in")
    assert top.document_version == "1.0-ORIGINAL-ENACTMENT"
    assert top.effective_date == "2024-07-01"

    # Verify citation formatting
    citation = format_legal_citation(top)
    assert "Section 63" in citation.citation_text
    assert "Bharatiya Sakshya Adhiniyam, 2023" in citation.citation_text
    assert "w.e.f. 2024-07-01" in citation.citation_text
    assert "indiacode.gov.in" in citation.citation_text
