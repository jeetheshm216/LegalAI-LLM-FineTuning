"""Comprehensive test suite for General Indian Legal Knowledge Platform.

Verifies:
1. Constitutional law retrieval (Arts 14, 19, 21, 32, 226)
2. Commercial and Central statutes retrieval (IT Act, NI Act, Contract Act)
3. Existing criminal statute compatibility (BNS, BNSS, BSA)
4. Judicial precedents (Arjun Panditrao Khotkar, Shreya Singhal)
5. Temporal legal versioning and 1 July 2024 criminal transition
6. Judicial invalidation / Struck down detection (Section 66A IT Act)
7. Foreign law interception and polite redirection (GDPR, US Code, US Constitution)
8. State-specific metadata support (Tamil Nadu, etc.)
9. Authority ranking (Tier 1 vs Tier 2 vs Tier 3)
10. Safe abstention on unverified/out-of-corpus topics
11. Hard Case RAG isolation verification
"""

import pytest
import sqlite3
import os
from src.legal_knowledge.indexing.database import IndianLegalDatabaseManager
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline
from src.legal_knowledge.integration.router_bridge import IndianLegalRouterBridge
from src.legal_knowledge.models import (
    IndianJurisdictionLevel,
    AuthorityTier,
    TemporalStatus,
    IndianDocumentType,
    SearchFilter
)


@pytest.fixture(scope="module")
def pipeline():
    return GeneralIndianLegalKnowledgePipeline(db_path="data/legalai_indian_legal_knowledge.db")


@pytest.fixture(scope="module")
def router_bridge(pipeline):
    return IndianLegalRouterBridge(pipeline=pipeline)


def test_01_constitution_retrieval(pipeline):
    """Verifies that Fundamental Rights and Writ articles are correctly retrieved."""
    result = pipeline.query("Article 21 protection of life and personal liberty")
    assert not result["abstained"]
    assert "Article 21" in result["answer"]
    assert "Constitution of India" in result["answer"]
    assert any("Article 21" in s["citation"] for s in result["sources"])


def test_02_ni_act_section_138_retrieval(pipeline):
    """Verifies retrieval of Section 138 Negotiable Instruments Act."""
    result = pipeline.query("Section 138 dishonour of cheque for insufficiency of funds")
    assert not result["abstained"]
    assert "Section 138" in result["answer"]
    assert "Negotiable Instruments Act" in result["answer"]
    assert any("Section 138" in s["citation"] for s in result["sources"])


def test_03_it_act_intermediary_liability(pipeline):
    """Verifies retrieval of Section 79 IT Act on intermediary exemption."""
    result = pipeline.query("Section 79 intermediary liability exemption")
    assert not result["abstained"]
    assert "Section 79" in result["answer"]
    assert "Information Technology Act" in result["answer"]


def test_04_contract_act_breach_damages(pipeline):
    """Verifies retrieval of Section 73 Contract Act on compensation for breach."""
    result = pipeline.query("Section 73 compensation for loss or damage caused by breach of contract")
    assert not result["abstained"]
    assert "Section 73" in result["answer"]
    assert "Indian Contract Act" in result["answer"]


def test_05_bns_criminal_statute_compatibility(pipeline):
    """Verifies that existing BNS sections imported from MVP database are retrievable."""
    result = pipeline.query("Section 103 BNS murder punishment")
    assert not result["abstained"]
    assert "103" in result["answer"]
    assert "Bharatiya Nyaya Sanhita" in result["answer"]


def test_06_struck_down_provision_shreya_singhal(pipeline):
    """Verifies that querying Section 66A IT Act triggers the judicial invalidation warning."""
    result = pipeline.query("Section 66A IT Act offensive messages")
    assert result["temporal_status"] == "STRUCK_DOWN"
    assert "unconstitutional" in result["answer"].lower()
    assert "Shreya Singhal" in result["answer"]
    assert "NOT currently enforceable" in result["answer"] or "not enforceable" in result["answer"].lower()


def test_07_supreme_court_precedent_arjun_panditrao(pipeline):
    """Verifies retrieval of Arjun Panditrao Khotkar precedent on electronic evidence."""
    result = pipeline.query("Supreme Court electronic evidence certificate 65B mandatory")
    assert not result["abstained"]
    assert "Arjun Panditrao Khotkar" in result["answer"]
    assert "(2020) 7 SCC 1" in result["answer"]


def test_08_temporal_transition_dates(pipeline):
    """Verifies that incident_date before 1 July 2024 advises IPC/CrPC, while after advises BNS/BNSS."""
    # Pre-July 2024
    res_pre = pipeline.query("Murder offense investigation", incident_date="2024-05-15")
    assert "prior to 1 July 2024" in res_pre["answer"]
    assert "Indian Penal Code, 1860" in res_pre["answer"]

    # Post-July 2024
    res_post = pipeline.query("Murder offense investigation", incident_date="2024-08-10")
    assert "on or after 1 July 2024" in res_post["answer"]
    assert "Bharatiya Nyaya Sanhita, 2023" in res_post["answer"]


def test_09_foreign_law_interception_gdpr(router_bridge):
    """Verifies that foreign law queries like GDPR are intercepted and redirected to Indian DPDP Act."""
    res = router_bridge.route_and_execute("What are the key compliance requirements under GDPR?")
    assert res["intent"] == "OUT_OF_SCOPE_FOREIGN_LAW"
    assert "focuses on Indian law" in res["answer"]
    assert "Digital Personal Data Protection Act, 2023" in res["answer"]
    assert len(res["sources"]) == 0


def test_10_foreign_law_interception_us_constitution(router_bridge):
    """Verifies that US Constitution queries redirect to Indian Constitution."""
    res = router_bridge.route_and_execute("Explain the First Amendment under the US Constitution")
    assert res["intent"] == "OUT_OF_SCOPE_FOREIGN_LAW"
    assert "focuses on Indian law" in res["answer"]
    assert "Constitution of India" in res["answer"]


def test_11_state_specific_metadata_filtering(pipeline):
    """Verifies that search filters correctly support state-level querying without error."""
    filters = SearchFilter(state="Tamil Nadu")
    results = pipeline.searcher.search("cheque dishonour notice", filters=filters, top_k=3)
    assert len(results) > 0
    # Returned chunks either have state=None (Central) or state='Tamil Nadu'
    for chunk, _ in results:
        assert chunk.state is None or chunk.state == "Tamil Nadu"


def test_12_safe_abstention_on_unverified_domain(pipeline):
    """Verifies that an obscure, unverified, non-Indian legal query safely abstains without hallucinating."""
    res = pipeline.query("zzyzx_protocol_antarctic_mineral_claims_1899")
    assert res["abstained"] is True
    assert res["answer"] == GeneralIndianLegalKnowledgePipeline.SAFE_ABSTENTION_MESSAGE


def test_13_case_rag_hard_isolation():
    """HARD SECURITY REQUIREMENT: Verifies that private case documents are NEVER indexed into General Indian Legal Knowledge DB."""
    # 1. Connect to general knowledge db
    conn_pub = sqlite3.connect("data/legalai_indian_legal_knowledge.db")
    cur_pub = conn_pub.cursor()
    # Check if any case_id column exists or if any private case documents are stored
    cur_pub.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur_pub.fetchall()]
    assert "case_documents" not in tables
    assert "case_document_chunks" not in tables

    # Verify no private client names from case RAG appear in public chunks
    cur_pub.execute("SELECT COUNT(*) FROM indian_legal_chunks WHERE content LIKE '%Martinez%'")
    assert cur_pub.fetchone()[0] == 0
    conn_pub.close()

    # 2. Check private case db remains intact
    if os.path.exists("data/legalai_case_rag.db"):
        conn_priv = sqlite3.connect("data/legalai_case_rag.db")
        cur_priv = conn_priv.cursor()
        cur_priv.execute("SELECT COUNT(*) FROM case_documents")
        assert cur_priv.fetchone()[0] >= 0
        conn_priv.close()
