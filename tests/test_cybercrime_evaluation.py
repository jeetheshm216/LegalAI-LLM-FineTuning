"""Comprehensive Cybercrime Legal Knowledge RAG Evaluation Suite.

Validates:
1. Exact provision retrieval for Information Technology Act, 2000
2. Multi-Act Cybercrime synthesis (IT Act + BNS + BNSS + BSA + Regulations + Guidance)
3. Electronic Evidence distinction: Current BSA Section 63 vs Historical IEA Section 65B
4. Binding Precedents: Shreya Singhal, Arjun Panditrao Khotkar, Anvar PV, Selvi, Christian Louboutin
5. Deterministic exact-provision safety & safe abstention on non-existent provisions
6. Source-type separation (STATUTE vs JUDGMENT vs REGULATION vs GUIDANCE vs ADVISORY)
7. Temporal validation (pre-July 1, 2024 vs post-July 1, 2024 offences)
8. Namespace isolation and collision prevention
"""

import pytest
import sys
import os

REPO_ROOT = "/home/sece2026-student07/legalai-finetuning"
sys.path.insert(0, REPO_ROOT)

from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline
from src.legal_knowledge.indexing.database import IndianLegalDatabaseManager


@pytest.fixture(scope="module")
def pipeline():
    return GeneralIndianLegalKnowledgePipeline()


@pytest.fixture(scope="module")
def db_mgr():
    return IndianLegalDatabaseManager()


def test_01_it_act_exact_section_66d(pipeline):
    """Verifies deterministic retrieval of IT Act Section 66D (cheating by personation)."""
    res = pipeline.query("Section 66D of Information Technology Act, 2000")
    assert not res["abstained"], "Query should not abstain"
    assert "66D" in res["answer"]
    assert "personation" in res["answer"].lower() or "cheating" in res["answer"].lower()
    assert res["response_type"] in ["EXACT_PROVISION", "PROVISION_GROUNDED", "EXACT_VERIFIED"]
    assert any("IT_ACT" in s["chunk_id"] for s in res["sources"])


def test_02_it_act_exact_section_43(pipeline):
    """Verifies deterministic retrieval of IT Act Section 43 (penalty for damage to computer system)."""
    res = pipeline.query("Section 43 Information Technology Act")
    assert not res["abstained"]
    assert "Section 43" in res["answer"]
    assert "damage to computer" in res["answer"].lower() or "computer system" in res["answer"].lower()


def test_03_it_act_section_79_intermediary_liability(pipeline):
    """Verifies retrieval of Section 79 IT Act safe harbor and intermediary protection."""
    res = pipeline.query("Section 79 IT Act intermediary liability safe harbor")
    assert not res["abstained"]
    assert "Section 79" in res["answer"]
    assert "intermediary" in res["answer"].lower()


def test_04_electronic_evidence_bsa_vs_iea(pipeline):
    """Verifies separation of BSA Section 63 from historical IEA Section 65B."""
    # Current law query
    res_curr = pipeline.query("admissibility of electronic records under Section 63 BSA")
    assert not res_curr["abstained"]
    assert "Section 63" in res_curr["answer"]
    assert any("BSA" in s["act_prefix"] for s in res_curr["sources"])
    
    # Historical law query
    res_hist = pipeline.query("Section 65B Indian Evidence Act 1872 certificate requirements")
    assert not res_hist["abstained"]
    assert "65B" in res_hist["answer"]


def test_05_precedent_arjun_panditrao(pipeline):
    """Verifies retrieval of binding Supreme Court 3-Judge Bench ratio in Arjun Panditrao Khotkar."""
    res = pipeline.query("Arjun Panditrao Khotkar Section 65B electronic certificate mandatory")
    assert not res["abstained"]
    assert "Arjun Panditrao" in res["answer"]
    assert "(2020) 7 SCC 1" in res["answer"]
    assert any("JUDGMENT" in s.get("source_type", "") or "JUDGMENT" in s.get("document_type", "") for s in res["sources"])


def test_06_precedent_shreya_singhal_section_66a(pipeline):
    """Verifies precedent Shreya Singhal striking down Section 66A and reading down Section 79(3)(b)."""
    res = pipeline.query("Shreya Singhal v Union of India Section 66A unconstitutional")
    assert not res["abstained"]
    assert "Shreya Singhal" in res["answer"]
    assert "66A" in res["answer"]
    assert "(2015) 5 SCC 1" in res["answer"]


def test_07_multi_act_cyber_fraud_framework(pipeline):
    """Verifies multi-act synthesis for financial cybercrime / online fraud."""
    res = pipeline.query("How is online phishing financial cyber fraud dealt under Indian law?")
    assert not res["abstained"]
    ans = res["answer"]
    assert "IT Act" in ans or "Information Technology Act" in ans
    # Check that sources span multiple acts
    act_prefixes = {s.get("act_prefix") for s in res["sources"]}
    assert len(act_prefixes) >= 2, f"Expected multi-act sources, got: {act_prefixes}"


def test_08_investigation_procedure_bnss(pipeline):
    """Verifies BNSS procedural requirements (audio-video electronic search/seizure & e-FIR)."""
    res = pipeline.query("procedure for search and seizure of electronic devices under BNSS 2023")
    assert not res["abstained"]
    ans = res["answer"]
    assert "BNSS" in ans or "Bharatiya Nagarik Suraksha" in ans
    assert any("BNSS" in s.get("act_prefix", "") for s in res["sources"])


def test_09_subordinate_it_rules_2021(pipeline):
    """Verifies retrieval of IT Rules 2021 due diligence and 24/36 hour takedown requirements."""
    res = pipeline.query("Rule 3 IT Rules 2021 intermediary due diligence")
    assert not res["abstained"]
    assert "Rule 3" in res["answer"] or "IT Rules 2021" in res["answer"]


def test_10_government_guidance_separation(pipeline):
    """Verifies that official guidance and advisories are explicitly marked as non-statutory."""
    res = pipeline.query("MHA cybercrime portal 1930 reporting SOP")
    assert not res["abstained"]
    # Check that guidance is marked
    source_types = {s.get("source_type") for s in res["sources"]}
    assert "GOVERNMENT_GUIDANCE" in source_types or "REGULATION" in source_types or "ADVISORY" in source_types


def test_11_safe_abstention_non_existent_section(pipeline):
    """Verifies deterministic safe abstention when querying non-existent provisions."""
    res = pipeline.query("Section 9999 Information Technology Act")
    assert res["abstained"] is True
    assert res["requires_verification"] is True
    assert res["response_type"] == "EXACT_NOT_VERIFIED"
    assert "EXACT_NOT_VERIFIED" in res.get("response_type", "")


def test_12_temporal_offence_date_validation(pipeline):
    """Verifies Article 20(1) non-retroactivity: 2022 offence governed by IPC/CrPC, 2025 by BNS/BNSS."""
    # 2022 incident -> Historical law
    res_2022 = pipeline.query("online impersonation cheating offence committed on 15 March 2022")
    assert not res_2022["abstained"]
    assert "IPC" in res_2022["answer"] or "Indian Penal Code" in res_2022["answer"] or "2024" in res_2022["answer"]
    
    # 2025 incident -> Current law
    res_2025 = pipeline.query("online impersonation cheating offence committed on 10 August 2025")
    assert not res_2025["abstained"]
    assert "BNS" in res_2025["answer"] or "Bharatiya Nyaya" in res_2025["answer"] or "2023" in res_2025["answer"]


def test_13_namespace_isolation(db_mgr):
    """Verifies 0 chunk ID collisions across all documents in SQLite."""
    with db_mgr._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT chunk_id, COUNT(*) FROM indian_legal_chunks GROUP BY chunk_id HAVING COUNT(*) > 1")
        duplicates = c.fetchall()
        assert len(duplicates) == 0, f"Found duplicate chunk IDs: {duplicates}"

