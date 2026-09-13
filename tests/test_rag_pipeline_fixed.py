"""
test_rag_pipeline_fixed.py

Comprehensive regression test suite for the fixed LegalAI RAG architecture.
Tests the 17 mandatory verification cases across:
- In-corpus statutory authority (BNS 103, BNSS 482, BSA 63)
- Statutory separation (BNS vs BNSS vs BSA)
- Fabricated section rejection (BNS 999)
- Out-of-corpus domain protection (Constitution Art 21, NI Act 138, IT Act 79, Contract 74, RERA, RTI, DPDP, Trademark, Patent)
- Temporal-law validation & Article 20(1) non-retroactivity (June 15, 2024 vs July 1, 2024 vs July 2, 2024)
"""

import pytest
from datetime import date
from src.rag.database.sqlite_adapter import SQLiteLegalDatabase
from src.rag.integration.domain_detector import LegalDomainDetector
from src.rag.integration.relevance_gate import StatutoryRelevanceGate
from src.rag.integration.temporal_guard import TemporalLawGuard
from src.rag.integration.citation_verifier import StatutoryCitationVerifier
from src.rag.integration.grounded_prompt import build_grounded_prompt
from src.rag.retrieval.retriever import LegalRetriever, RetrievalResult


@pytest.fixture(scope="module")
def domain_detector():
    return LegalDomainDetector()


@pytest.fixture(scope="module")
def temporal_guard():
    return TemporalLawGuard()


@pytest.fixture(scope="module")
def relevance_gate():
    return StatutoryRelevanceGate()


@pytest.fixture(scope="module")
def citation_verifier():
    return StatutoryCitationVerifier()


@pytest.fixture(scope="module")
def db():
    return SQLiteLegalDatabase("data/legalai_rag_mvp.db")


# -------------------------------------------------------------
# Tests 1-3: In-Corpus Statutory Core
# -------------------------------------------------------------

def test_1_bns_section_103_in_corpus(domain_detector, db):
    """Test 1: BNS Section 103 belongs in-corpus and is correctly retrieved."""
    q = "What is the punishment for murder under Section 103 of BNS?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is True
    assert res.statute_code == "BNS"
    assert res.specific_provision == "103"

    retriever = LegalRetriever(db)
    results = retriever.retrieve(q, act_filter="BNS", section_filter="103", mode="lexical")
    assert len(results) > 0
    assert results[0].act_prefix == "BNS"
    assert str(results[0].section) == "103"
    assert "murder" in results[0].section_title.lower()


def test_2_bnss_section_482_in_corpus(domain_detector, db):
    """Test 2: BNSS Section 482 belongs in-corpus and maps to bail."""
    q = "What provision of BNSS deals with anticipatory bail?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is True
    assert res.statute_code == "BNSS"

    retriever = LegalRetriever(db)
    results = retriever.retrieve("direction for grant of bail to person apprehending arrest", act_filter="BNSS", section_filter="482", mode="lexical")
    assert len(results) > 0
    assert results[0].act_prefix == "BNSS"
    assert str(results[0].section) == "482"


def test_3_bsa_section_63_in_corpus(domain_detector, db):
    """Test 3: BSA Section 63 belongs in-corpus and covers electronic records."""
    q = "Which BSA provision deals with admissibility of electronic records?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is True
    assert res.statute_code == "BSA"

    retriever = LegalRetriever(db)
    results = retriever.retrieve("admissibility of electronic records", act_filter="BSA", section_filter="63", mode="lexical")
    assert len(results) > 0
    assert results[0].act_prefix == "BSA"
    assert str(results[0].section) == "63"


def test_4_bns_bnss_bsa_domain_separation(domain_detector):
    """Test 4: BNS, BNSS, and BSA domains are strictly separated."""
    bns_res = domain_detector.detect("Is theft punishable under BNS?")
    bnss_res = domain_detector.detect("What is the arrest procedure under BNSS?")
    bsa_res = domain_detector.detect("How are electronic records proved under BSA?")

    assert bns_res.detected_domain == "Substantive Criminal Law"
    assert bnss_res.detected_domain == "Criminal Procedure"
    assert bsa_res.detected_domain == "Evidence Law"


def test_5_fake_bns_999_rejection(domain_detector, citation_verifier):
    """Test 5: Fabricated Section 999 BNS is rejected (exceeds 358 statutory sections)."""
    q = "What is BNS Section 999?"
    res = domain_detector.detect(q)
    assert res.specific_provision == "999"
    sec_num = int(res.specific_provision)
    assert sec_num > 358  # Exceeds BNS maximum of 358 sections

    # Citation verifier catches it
    v_res = citation_verifier.verify("Under Section 999 of BNS, the court may...", [], target_statute_code="BNS")
    assert v_res.is_valid is False
    assert any("exceeds BNS maximum" in h for h in v_res.hallucinated_provisions)


# -------------------------------------------------------------
# Tests 6-14: Out-of-Corpus Domain Protection (No Wrong-Act Hallucinations)
# -------------------------------------------------------------

def test_6_constitution_article_21_out_of_corpus(domain_detector):
    """Test 6: Article 21 Constitution is recognized as out-of-corpus."""
    q = "What does Article 21 of the Constitution of India protect?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Constitution" in res.target_statute


def test_7_ni_act_138_out_of_corpus(domain_detector):
    """Test 7: Section 138 cheque dishonour is recognized as NI Act (out-of-corpus)."""
    q = "What are the essential ingredients for an offence under Section 138 of the Negotiable Instruments Act?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Negotiable Instruments" in res.target_statute


def test_8_it_act_79_out_of_corpus(domain_detector):
    """Test 8: Section 79 intermediary liability is recognized as IT Act (out-of-corpus)."""
    q = "How does Section 79 of the Information Technology Act protect digital intermediaries?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Information Technology" in res.target_statute


def test_9_contract_act_74_out_of_corpus(domain_detector):
    """Test 9: Section 74 liquidated damages is recognized as Contract Act (out-of-corpus)."""
    q = "What is the legal difference between liquidated damages and penalty under Section 74 of the Indian Contract Act?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Contract Act" in res.target_statute


def test_10_rera_delay_out_of_corpus(domain_detector):
    """Test 10: RERA builder delay is recognized as out-of-corpus."""
    q = "What remedies are available to an allottee for builder delay under RERA?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Real Estate" in res.target_statute


def test_11_rti_response_deadline_out_of_corpus(domain_detector):
    """Test 11: RTI 30-day deadline is recognized as out-of-corpus."""
    q = "What is the statutory response deadline for a Public Information Officer under the RTI Act?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Right to Information" in res.target_statute


def test_12_dpdp_consent_out_of_corpus(domain_detector):
    """Test 12: DPDP consent and data fiduciary are recognized as out-of-corpus."""
    q = "Under the DPDP Act, what are the mandatory conditions for valid consent by a data principal?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Digital Personal Data Protection" in res.target_statute


def test_13_trademark_out_of_corpus(domain_detector):
    """Test 13: Trademark descriptive mark is recognized as out-of-corpus."""
    q = "Can a purely descriptive word acquire distinctiveness for trademark registration?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Trade Marks" in res.target_statute


def test_14_patent_out_of_corpus(domain_detector):
    """Test 14: Patent inventive step is recognized as out-of-corpus."""
    q = "What constitutes an inventive step under the Patents Act, 1970?"
    res = domain_detector.detect(q)
    assert res.is_in_corpus is False
    assert "Patents" in res.target_statute


# -------------------------------------------------------------
# Tests 15-17: Temporal Law Validation & Article 20(1) Non-Retroactivity
# -------------------------------------------------------------

def test_15_june_15_2024_offence_article_20(temporal_guard):
    """Test 15: Substantive offence committed on June 15, 2024 CANNOT apply BNS retrospectively."""
    q = "A theft allegedly took place on 15 June 2024, but the FIR is registered in 2025. Which substantive law applies?"
    t_res = temporal_guard.analyze(q)
    assert t_res.has_date_context is True
    assert t_res.is_pre_commencement is True
    assert "Indian Penal Code, 1860" in t_res.applicable_substantive_law
    assert "Article 20(1)" in t_res.applicable_substantive_law
    assert "CANNOT be applied retrospectively" in t_res.temporal_guidance


def test_16_july_1_2024_offence_bns(temporal_guard):
    """Test 16: Offence committed on July 1, 2024 is governed by BNS 2023."""
    q = "An assault was committed on 1 July 2024. Which penal code applies?"
    t_res = temporal_guard.analyze(q)
    assert t_res.has_date_context is True
    assert t_res.is_pre_commencement is False
    assert "Bharatiya Nyaya Sanhita, 2023 (BNS)" in t_res.applicable_substantive_law


def test_17_july_2_2024_offence_bns(temporal_guard):
    """Test 17: Offence committed on July 2, 2024 is governed by BNS 2023."""
    q = "A robbery took place on 2 July 2024. Which penal code applies to the offence?"
    t_res = temporal_guard.analyze(q)
    assert t_res.has_date_context is True
    assert t_res.is_pre_commencement is False
    assert "Bharatiya Nyaya Sanhita, 2023 (BNS)" in t_res.applicable_substantive_law
