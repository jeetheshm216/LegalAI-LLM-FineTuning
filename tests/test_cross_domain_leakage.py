"""Automated cross-domain collision tests proving that section-number collisions
cannot cause wrong-domain retrieval in General Indian Legal Knowledge RAG.
"""

import pytest
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline


@pytest.fixture(scope="module")
def pipeline():
    return GeneralIndianLegalKnowledgePipeline(db_path="data/legalai_indian_legal_knowledge.db")


COLLISION_PAIRS = [
    # (Query, Expected Act Prefix, Forbidden Act Prefix, Expected Section)
    ("What does Section 19 of the POCSO Act require?", "POCSO_ACT_2012", "BNS", "19"),
    ("What does Section 19 of BNS provide?", "BNS", "POCSO_ACT_2012", "19"),

    ("What are the bail conditions under Section 45 of PMLA?", "PMLA_2002", "BNS", "45"),
    ("What does Section 45 of BNS provide?", "BNS", "PMLA_2002", "45"),

    ("What are the search conditions under Section 50 of NDPS Act?", "NDPS_ACT_1985", "BNS", "50"),
    ("What does Section 50 of BNS state?", "BNS", "NDPS_ACT_1985", "50"),

    ("What is the scope of first appeal under Section 96 of CPC?", "CPC_1908", "COMPANIES_ACT_2013", "96"),
    ("What does Section 96 of the Companies Act, 2013 provide regarding annual general meetings?", "COMPANIES_ACT_2013", "CPC_1908", "96"),

    ("What are the requirements for application by operational creditor under Section 9 of IBC?", "IBC_2016", "ARBITRATION_ACT_1996", "9"),
    ("What interim relief can the Court grant under Section 9 of the Arbitration and Conciliation Act?", "ARBITRATION_ACT_1996", "IBC_2016", "9"),
]


@pytest.mark.parametrize("query_str,expected_act,forbidden_act,expected_sec", COLLISION_PAIRS)
def test_cross_domain_section_collision(pipeline, query_str, expected_act, forbidden_act, expected_sec):
    res = pipeline.query(query_str)

    # 1. Pipeline must not abstain for indexed provisions
    assert not res["abstained"], f"Query '{query_str}' abstained unexpectedly"
    assert len(res["sources"]) > 0, f"Query '{query_str}' returned no sources"

    # 2. Assert candidates strictly belong to requested Act
    for src in res["sources"]:
        cid = src["chunk_id"]
        assert forbidden_act not in cid, f"Cross-domain leakage detected: found forbidden '{forbidden_act}' in chunk '{cid}' for query '{query_str}'"
        assert expected_act in cid or "SC_" in cid, f"Unexpected Act in chunk '{cid}' for query '{query_str}'"

    # 3. Assert top retrieved chunk is the exact target section from requested Act
    top_chunk = res["sources"][0]
    assert expected_act in top_chunk["chunk_id"], f"Top source '{top_chunk['chunk_id']}' does not match expected Act '{expected_act}'"
    assert expected_sec in top_chunk["chunk_id"] or expected_sec in top_chunk["citation"], f"Top source does not contain Section {expected_sec}"

    # 4. Assert citation and answer text match the requested Act
    assert expected_sec in res["answer"], f"Section {expected_sec} missing from synthesized answer text"
    assert any(expected_act in s["chunk_id"] for s in res["sources"])
