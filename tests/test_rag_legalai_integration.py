"""Automated tests for LegalAI RAG + LegalAI v2 integration layer.

Contains:
A. Fast Retrieval & Grounding Context Tests (10 unit tests)
B. Model Integration Smoke Tests (3 LLM generation tests sharing a session-scoped model)
"""

import os
import pytest
import torch

from src.rag.database.sqlite_adapter import SQLiteLegalDatabase
from src.rag.embeddings.embedder import LegalEmbedder
from src.rag.retrieval.retriever import LegalRetriever
from src.rag.citation.citation import format_legal_citation
from src.rag.concordance.concordance import ConcordanceRegistry
from src.rag.integration.grounded_prompt import build_grounded_prompt
from src.rag.integration.rag_legalai import LegalAIRAGPipeline, answer_legal_question

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data/legalai_rag_mvp.db")


# ============================================================================
# PART A: RETRIEVAL & CONTEXT TESTS (Fast execution, no 14B model reload)
# ============================================================================

@pytest.fixture(scope="module")
def shared_pipeline():
    """Provides a pipeline instance with lazy-loaded LLM."""
    if not os.path.exists(DB_PATH):
        pytest.skip(f"MVP database not found at {DB_PATH}. Ingestion must run first.")
    return LegalAIRAGPipeline(db_path=DB_PATH, lazy_load_model=True)


def test_1_bns_section_103_retrieval(shared_pipeline):
    """Test 1: Query for murder punishment retrieves BNS Section 103."""
    results = shared_pipeline.retriever.retrieve(
        query="Whoever commits murder shall be punished with death or imprisonment for life",
        act_filter="BNS",
        section_filter="103",
        mode="hybrid",
        top_k=1
    )
    assert len(results) == 1
    top = results[0]
    assert top.act_prefix == "BNS"
    assert top.section == "103"
    assert "murder" in top.section_title.lower()


def test_2_bnss_section_482_retrieval(shared_pipeline):
    """Test 2: Query for anticipatory bail retrieves BNSS Section 482."""
    results = shared_pipeline.retriever.retrieve(
        query="Direction for grant of bail to person apprehending arrest",
        act_filter="BNSS",
        section_filter="482",
        mode="hybrid",
        top_k=1
    )
    assert len(results) == 1
    top = results[0]
    assert top.act_prefix == "BNSS"
    assert top.section == "482"
    assert "bail" in top.section_title.lower()


def test_3_bsa_section_63_retrieval(shared_pipeline):
    """Test 3: Query for electronic records retrieves BSA Section 63."""
    results = shared_pipeline.retriever.retrieve(
        query="Admissibility of electronic records and certificate requirement",
        act_filter="BSA",
        section_filter="63",
        mode="hybrid",
        top_k=1
    )
    assert len(results) == 1
    top = results[0]
    assert top.act_prefix == "BSA"
    assert top.section == "63"
    assert "electronic" in top.section_title.lower()


def test_4_bns_bnss_bsa_distinction(shared_pipeline):
    """Test 4: Verify substantive/procedural/evidentiary domain separation."""
    # BNS
    res_bns = shared_pipeline.retriever.retrieve(query="offence murder", act_filter="BNS", top_k=1)
    assert res_bns[0].act_type == "SUBSTANTIVE_CRIMINAL_LAW"

    # BNSS
    res_bnss = shared_pipeline.retriever.retrieve(query="bail investigation", act_filter="BNSS", top_k=1)
    assert res_bnss[0].act_type == "CRIMINAL_PROCEDURE"

    # BSA
    res_bsa = shared_pipeline.retriever.retrieve(query="evidence document", act_filter="BSA", top_k=1)
    assert res_bsa[0].act_type == "EVIDENCE_LAW"


def test_5_pre_july_1_2024_temporal_case(shared_pipeline):
    """Test 5: Verify pre-July 1, 2024 date filter does not return 2023 Sanhitas as active law."""
    results_pre = shared_pipeline.retriever.retrieve(
        query="murder",
        effective_date="2024-05-15",
        mode="lexical"
    )
    assert len(results_pre) == 0, "No 2023 Sanhita provision can be active prior to 2024-07-01."


def test_6_post_july_1_2024_case(shared_pipeline):
    """Test 6: Verify post-July 1, 2024 date returns active 2023 Sanhita provision."""
    results_post = shared_pipeline.retriever.retrieve(
        query="murder",
        effective_date="2024-08-15",
        act_filter="BNS",
        section_filter="103",
        mode="lexical"
    )
    assert len(results_post) == 1
    assert results_post[0].section == "103"


def test_7_nonexistent_fabricated_section_resistance(shared_pipeline):
    """Test 7: Query for fabricated Section 999 BNS returns explicit not-found without substituting another section."""
    res = shared_pipeline.answer_question("What is Section 999 of BNS?")
    assert res["confidence_status"] == "INSUFFICIENT_RETRIEVAL"
    assert "Section 999" in res["answer"]
    assert "was not found" in res["answer"]
    assert res["retrieved_sources"] == []


def test_8_citation_generation(shared_pipeline):
    """Test 8: Verify pinpoint statutory citation formatting."""
    results = shared_pipeline.retriever.retrieve(
        query="electronic records",
        act_filter="BSA",
        section_filter="63",
        top_k=1
    )
    assert len(results) == 1
    cit = format_legal_citation(results[0])
    assert "Section 63" in cit.citation_text
    assert "Bharatiya Sakshya Adhiniyam, 2023" in cit.citation_text
    assert "w.e.f. 2024-07-01" in cit.citation_text
    assert "indiacode.gov.in" in cit.citation_text


def test_9_insufficient_retrieval_handling(shared_pipeline):
    """Test 9: Query outside the current corpus triggers insufficient evidence response."""
    res = shared_pipeline.answer_question(
        "What are the specific tax filing exemptions under Section 80C of the Income Tax Act?"
    )
    assert res["confidence_status"] == "INSUFFICIENT_RETRIEVAL"
    assert "available legal sources do not provide sufficient information" in res["answer"]


def test_10_metadata_traceability(shared_pipeline):
    """Test 10: Verify complete source provenance metadata survives to output."""
    results = shared_pipeline.retriever.retrieve(
        query="murder",
        act_filter="BNS",
        section_filter="103",
        top_k=1
    )
    assert len(results) == 1
    r = results[0]
    assert r.source_url.startswith("https://indiacode.gov.in")
    assert r.document_version == "1.0-ORIGINAL-ENACTMENT"
    assert r.chapter.startswith("CHAPTER VI")
    assert r.effective_date == "2024-07-01"


# ============================================================================
# PART B: MODEL INTEGRATION SMOKE TESTS (Loads 14B model ONCE)
# ============================================================================

@pytest.fixture(scope="module")
def loaded_pipeline():
    """Loads the 14B base model and attaches the LegalAI v2 LoRA adapter once for smoke testing."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA GPU required for 14B model smoke tests.")
    if not os.path.exists("outputs/qwen14b-legalai-v2"):
        pytest.skip("outputs/qwen14b-legalai-v2 not found.")

    pipeline = LegalAIRAGPipeline(db_path=DB_PATH, lazy_load_model=False)
    return pipeline


@pytest.mark.gpu
def test_smoke_bns_103_generation(loaded_pipeline):
    """Smoke Test 1: Grounded answer for BNS Section 103 (Murder punishment)."""
    q = "What is the punishment for murder under Section 103 of the BNS?"
    output = loaded_pipeline.answer_question(q, top_k=2, max_new_tokens=256)

    assert output["confidence_status"] == "GROUNDED_STATUTORY"
    assert len(output["citations"]) > 0
    assert any("Section 103" in c for c in output["citations"])
    ans = output["answer"].lower()
    assert "death" in ans or "imprisonment for life" in ans
    assert "section 103" in ans


@pytest.mark.gpu
def test_smoke_bnss_482_generation(loaded_pipeline):
    """Smoke Test 2: Grounded answer for BNSS Section 482 (Anticipatory bail)."""
    q = "What provision of BNSS deals with anticipatory bail?"
    output = loaded_pipeline.answer_question(q, top_k=5, max_new_tokens=256)

    assert output["confidence_status"] == "GROUNDED_STATUTORY"
    assert len(output["citations"]) > 0
    assert any("Section 482" in c for c in output["citations"])
    ans = output["answer"].lower()
    assert "482" in ans
    assert "bail" in ans or "arrest" in ans


@pytest.mark.gpu
def test_smoke_bsa_63_generation(loaded_pipeline):
    """Smoke Test 3: Grounded answer for BSA Section 63 (Electronic records)."""
    q = "Which BSA provision deals with admissibility of electronic records?"
    output = loaded_pipeline.answer_question(q, top_k=2, max_new_tokens=256)

    assert output["confidence_status"] == "GROUNDED_STATUTORY"
    assert len(output["citations"]) > 0
    assert any("Section 63" in c for c in output["citations"])
    ans = output["answer"].lower()
    assert "63" in ans
    assert "electronic" in ans
