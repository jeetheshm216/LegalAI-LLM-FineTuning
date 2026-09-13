"""End-to-end legal-specific smoke test suite for LegalAI Real-Data RAG MVP.

Executes hybrid and vector retrieval tests across the 5 benchmark failure modes:
1. Exact statutory section lookup
2. BNS vs BNSS vs BSA statutory separation
3. July 1, 2024 commencement and temporal applicability
4. BSA electronic evidence provision lookup
5. Predecessor-successor legal concordance and repeal status
"""

import os
import json
from src.rag.database.sqlite_adapter import SQLiteLegalDatabase
from src.rag.embeddings.embedder import LegalEmbedder
from src.rag.retrieval.retriever import LegalRetriever
from src.rag.citation.citation import format_legal_citation
from src.rag.concordance.concordance import ConcordanceRegistry

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "data/legalai_rag_mvp.db")


def run_smoke_tests():
    print("=" * 70)
    print("LEGALAI RAG MVP: END-TO-END LEGAL SMOKE TESTS")
    print("=" * 70)

    db = SQLiteLegalDatabase(DB_PATH)
    embedder = LegalEmbedder(device="cuda:0")
    retriever = LegalRetriever(db=db, embedder=embedder)
    concordance = ConcordanceRegistry()

    results_summary = []

    # -------------------------------------------------------------
    # Test Case 1: Exact Statutory Section Lookup
    # -------------------------------------------------------------
    print("\n--- TEST CASE 1: Exact Statutory Section Lookup ---")
    query_1 = "Section 103"
    res_1 = retriever.retrieve(query=query_1, act_filter="BNS", section_filter="103", mode="hybrid", top_k=1)
    assert len(res_1) > 0
    top_1 = res_1[0]
    cit_1 = format_legal_citation(top_1)
    print(f"Query: '{query_1}' (Act Filter: BNS, Section Filter: 103)")
    print(f"  Retrieved Chunk: {top_1.chunk_id}")
    print(f"  Section: Section {top_1.section} - {top_1.section_title}")
    print(f"  Citation: {cit_1.citation_text}")
    assert top_1.section == "103" and top_1.act_prefix == "BNS"
    results_summary.append({"test": "Exact Section Lookup", "status": "PASS", "details": cit_1.citation_text})

    # -------------------------------------------------------------
    # Test Case 2: BNS vs BNSS vs BSA Distinction
    # -------------------------------------------------------------
    print("\n--- TEST CASE 2: BNS vs BNSS vs BSA Distinction ---")
    
    # 2A: Substantive crime query
    q_bns = "Punishment for snatching by force or sudden grabbing"
    res_bns = retriever.retrieve(query=q_bns, mode="hybrid", top_k=3)
    print(f"Substantive Query: '{q_bns}'")
    for idx, r in enumerate(res_bns, 1):
        print(f"  [{idx}] {r.act_prefix} Sec {r.section}: {r.section_title} (Score: {r.relevance_score:.4f}, Act Type: {r.act_type})")
    assert res_bns[0].act_prefix == "BNS" and res_bns[0].act_type == "SUBSTANTIVE_CRIMINAL_LAW"

    # 2B: Procedural query
    q_bnss = "Grounds and conditions for grant of anticipatory bail by High Court"
    res_bnss = retriever.retrieve(query=q_bnss, mode="hybrid", top_k=3)
    print(f"\nProcedural Query: '{q_bnss}'")
    for idx, r in enumerate(res_bnss, 1):
        print(f"  [{idx}] {r.act_prefix} Sec {r.section}: {r.section_title} (Score: {r.relevance_score:.4f}, Act Type: {r.act_type})")
    assert res_bnss[0].act_prefix == "BNSS" and res_bnss[0].act_type == "CRIMINAL_PROCEDURE"
    assert "482" in [r.section for r in res_bnss]

    # 2C: Evidence query
    q_bsa = "Admissibility of electronic record produced by computer system"
    res_bsa = retriever.retrieve(query=q_bsa, mode="hybrid", top_k=3)
    print(f"\nEvidence Query: '{q_bsa}'")
    for idx, r in enumerate(res_bsa, 1):
        print(f"  [{idx}] {r.act_prefix} Sec {r.section}: {r.section_title} (Score: {r.relevance_score:.4f}, Act Type: {r.act_type})")
    assert res_bsa[0].act_prefix == "BSA" and res_bsa[0].act_type == "EVIDENCE_LAW"
    assert "63" in [r.section for r in res_bsa]

    results_summary.append({"test": "BNS/BNSS/BSA Separation", "status": "PASS", "details": "Substantive -> BNS, Procedural -> BNSS, Evidence -> BSA"})

    # -------------------------------------------------------------
    # Test Case 3: July 1, 2024 Commencement Boundary
    # -------------------------------------------------------------
    print("\n--- TEST CASE 3: July 1, 2024 Commencement Boundary ---")
    date_prior = "2024-05-15"
    date_post = "2024-08-01"

    # Incident before July 1, 2024
    res_prior = retriever.retrieve(query="murder", section_filter="103", effective_date=date_prior, mode="lexical")
    print(f"Effective Date Filter: '{date_prior}' (Pre-commencement) -> Retrieved {len(res_prior)} provisions.")
    assert len(res_prior) == 0, "BNS must not be returned for dates prior to 2024-07-01."

    # Incident after July 1, 2024
    res_post = retriever.retrieve(query="murder", section_filter="103", effective_date=date_post, mode="lexical")
    print(f"Effective Date Filter: '{date_post}' (Post-commencement) -> Retrieved {len(res_post)} provisions.")
    assert len(res_post) > 0 and res_post[0].section == "103"
    results_summary.append({"test": "Commencement Date Boundary", "status": "PASS", "details": "Pre-2024-07-01 -> 0, Post-2024-07-01 -> Active"})

    # -------------------------------------------------------------
    # Test Case 4: BSA Evidence Provision Lookup
    # -------------------------------------------------------------
    print("\n--- TEST CASE 4: BSA Evidence Provision Lookup ---")
    q_ev = "Conditions for admitting secondary evidence of electronic records and certificate requirement"
    res_ev = retriever.retrieve(query=q_ev, act_filter="BSA", mode="hybrid", top_k=3)
    print(f"Evidence Provision Query: '{q_ev}'")
    for idx, r in enumerate(res_ev, 1):
        cit = format_legal_citation(r)
        print(f"  [{idx}] {cit.citation_text}")
    assert any(r.section in ["63", "61", "57"] for r in res_ev)
    results_summary.append({"test": "BSA Evidence Provision Lookup", "status": "PASS", "details": "Retrieved BSA Section 63/61"})

    # -------------------------------------------------------------
    # Test Case 5: Concordance & Repealed Law Status
    # -------------------------------------------------------------
    print("\n--- TEST CASE 5: Concordance & Repealed Law Status ---")
    
    # IPC 302 -> BNS 103
    m_302 = concordance.lookup_legacy_to_modern("IPC", "302")
    print(f"Legacy Lookup 'IPC 302' -> {m_302.modern_act} Section {m_302.modern_section} ({m_302.verification_status})")
    assert m_302.modern_section == "103"

    # CrPC 438 -> BNSS 482
    m_438 = concordance.lookup_legacy_to_modern("CrPC", "438")
    print(f"Legacy Lookup 'CrPC 438' -> {m_438.modern_act} Section {m_438.modern_section} ({m_438.verification_status})")
    assert m_438.modern_section == "482"

    # IEA 65B -> BSA 63
    m_65b = concordance.lookup_legacy_to_modern("IEA", "65B")
    print(f"Legacy Lookup 'IEA 65B' -> {m_65b.modern_act} Section {m_65b.modern_section} ({m_65b.verification_status})")
    assert m_65b.modern_section == "63"

    # Repeal provision verification in database
    res_repeal = retriever.retrieve(query="The Code of Criminal Procedure 1973 is hereby repealed", act_filter="BNSS", section_filter="531", mode="lexical")
    assert len(res_repeal) > 0 and res_repeal[0].section == "531"
    print(f"Repeal Clause: BNSS Section 531 ('{res_repeal[0].section_title}') successfully verified in DB.")

    results_summary.append({"test": "Statutory Concordance & Repeals", "status": "PASS", "details": "IPC 302->103, CrPC 438->482, IEA 65B->63, BNSS 531 Repeal"})

    print("\n" + "=" * 70)
    print("ALL 5 LEGAL SMOKE TESTS PASSED WITH 100% GROUNDED STATUTORY ACCURACY")
    print("=" * 70)
    return results_summary


if __name__ == "__main__":
    run_smoke_tests()
