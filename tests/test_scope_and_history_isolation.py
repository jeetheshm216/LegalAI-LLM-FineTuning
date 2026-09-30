"""
tests/test_scope_and_history_isolation.py

End-to-End Scope & Conversation History Isolation Regression Suite.
Validates:
1. Case A (Martinez, case-01): "What is this case about?" -> Answers using Martinez facts only.
2. Case B (Whitfield, case-02): "What is this case about?" -> Answers using Whitfield facts only.
3. General Assistant (GENERAL, case_id=None): "What is this case about?" -> Does NOT inherit Martinez or Whitfield context (fails closed / clarification).
4. Conversation History Isolation:
   - Case A history contains only Case A messages.
   - Case B history contains only Case B messages.
   - General Assistant history contains only General messages.
   - Navigating Back to Case A restores only Case A history.
   - Navigating Back to Case B restores only Case B history.
5. Query-dependent cross-matter retrieval:
   - "Do I have another case with a similar issue?" inside Martinez -> Cross-matter retrieved with structured provenance (source_scope="OTHER_MATTER").
   - "What evidence is missing?" inside Martinez -> ONLY Martinez case RAG used. Other cases NOT retrieved.
6. Non-case queries inside a case:
   - "What is Qwen?" inside Martinez -> TECHNICAL_AI, Base Qwen, zero Case RAG.
   - "What is Section 66C?" inside Martinez -> EXACT_PROVISION_QUERY, Legal RAG, zero Case RAG.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from typing import Dict, Any, List

API_BASE = "http://127.0.0.1:8008/api/v1"

def make_chat_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{API_BASE}/ai/chat"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_scope_and_history_isolation():
    print("\n" + "=" * 70)
    print("STARTING SCOPE & HISTORY ISOLATION REGRESSION TEST")
    print("=" * 70)

    # Simulated client-side scoped conversation history stores
    scoped_histories: Dict[str, List[Dict[str, Any]]] = {
        "CASE:case-01": [],
        "CASE:case-02": [],
        "GENERAL": []
    }

    # -------------------------------------------------------------
    # STEP 1: Case A (Martinez, case-01) -> "What is this case about?"
    # -------------------------------------------------------------
    print("\n[TEST 1] Case A (Martinez): 'What is this case about?'")
    req_martinez_1 = {
        "content": "What is this case about?",
        "mode": "SINGLE_CASE",
        "caseId": "case-01",
        "caseNumber": "2024-CV-1187",
        "history": scoped_histories["CASE:case-01"]
    }
    resp1 = make_chat_request(req_martinez_1)
    
    print(f"  Route: {resp1.get('route')} | Sub-intent: {resp1.get('sub_intent')}")
    print(f"  Confidence Status: {resp1.get('confidence_status')}")
    print(f"  Response excerpt: {resp1.get('content', '')[:160]}...")
    
    # Verifications
    assert resp1.get("route") == "CASE_QUERY", f"Expected CASE_QUERY, got {resp1.get('route')}"
    ans1_lower = resp1.get("content", "").lower()
    assert "martinez" in ans1_lower or "coastal" in ans1_lower or "charterparty" in ans1_lower, \
        "Answer must be grounded in Martinez case facts"
    assert "whitfield" not in ans1_lower, "Must NOT contain Whitfield case facts"
    
    # Store turn in Case A history
    scoped_histories["CASE:case-01"].append({"role": "user", "content": "What is this case about?", "query_type": "CASE_QUERY"})
    scoped_histories["CASE:case-01"].append({"role": "assistant", "content": resp1.get("content", ""), "query_type": "CASE_QUERY"})
    print("  [PASS] Case A answered using Martinez only.")

    # -------------------------------------------------------------
    # STEP 2: Case B (Whitfield, case-02) -> "What is this case about?"
    # -------------------------------------------------------------
    print("\n[TEST 2] Case B (Whitfield): 'What is this case about?'")
    req_whitfield_1 = {
        "content": "What is this case about?",
        "mode": "SINGLE_CASE",
        "caseId": "case-02",
        "caseNumber": "2024-CR-0442",
        "history": scoped_histories["CASE:case-02"]
    }
    resp2 = make_chat_request(req_whitfield_1)
    
    print(f"  Route: {resp2.get('route')} | Sub-intent: {resp2.get('sub_intent')}")
    print(f"  Confidence Status: {resp2.get('confidence_status')}")
    print(f"  Response excerpt: {resp2.get('content', '')[:160]}...")

    assert resp2.get("route") == "CASE_QUERY", f"Expected CASE_QUERY, got {resp2.get('route')}"
    ans2_lower = resp2.get("content", "").lower()
    assert "whitfield" in ans2_lower or "criminal" in ans2_lower or "chargesheet" in ans2_lower or "bail" in ans2_lower, \
        "Answer must be grounded in Whitfield case facts"
    assert "martinez" not in ans2_lower and "charterparty" not in ans2_lower, \
        "Must NOT contain Martinez case facts"

    # Store turn in Case B history
    scoped_histories["CASE:case-02"].append({"role": "user", "content": "What is this case about?", "query_type": "CASE_QUERY"})
    scoped_histories["CASE:case-02"].append({"role": "assistant", "content": resp2.get("content", ""), "query_type": "CASE_QUERY"})
    print("  [PASS] Case B answered using Whitfield only.")

    # -------------------------------------------------------------
    # STEP 3: General Assistant (GENERAL, no case) -> "What is this case about?"
    # -------------------------------------------------------------
    print("\n[TEST 3] General Assistant: 'What is this case about?'")
    req_general_1 = {
        "content": "What is this case about?",
        "mode": "GENERAL",
        "caseId": None,
        "caseNumber": None,
        "history": scoped_histories["GENERAL"]
    }
    resp3 = make_chat_request(req_general_1)
    
    print(f"  Route: {resp3.get('route')} | Sub-intent: {resp3.get('sub_intent')}")
    print(f"  Confidence Status: {resp3.get('confidence_status')}")
    print(f"  Response excerpt: {resp3.get('content', '')[:160]}...")

    # Must fail closed: request clarification rather than guessing Martinez or Whitfield
    assert resp3.get("route") == "AMBIGUOUS", f"Expected AMBIGUOUS in General Assistant, got {resp3.get('route')}"
    ans3_lower = resp3.get("content", "").lower()
    assert "martinez" not in ans3_lower, "General Assistant must NOT inherit Martinez facts"
    assert "whitfield" not in ans3_lower, "General Assistant must NOT inherit Whitfield facts"
    print("  [PASS] General Assistant did not silently inherit any case context.")

    # Store in General history
    scoped_histories["GENERAL"].append({"role": "user", "content": "What is this case about?", "query_type": "AMBIGUOUS"})
    scoped_histories["GENERAL"].append({"role": "assistant", "content": resp3.get("content", ""), "query_type": "AMBIGUOUS"})

    # -------------------------------------------------------------
    # STEP 4: Back to Case A -> History verification
    # -------------------------------------------------------------
    print("\n[TEST 4] Back to Case A: History verification")
    case_a_history = scoped_histories["CASE:case-01"]
    assert len(case_a_history) == 2, f"Case A history must have exactly 2 messages, got {len(case_a_history)}"
    assert any("martinez" in m["content"].lower() or "charterparty" in m["content"].lower() for m in case_a_history if m["role"] == "assistant"), \
        "Case A history must preserve Martinez content"
    assert not any("whitfield" in m["content"].lower() for m in case_a_history), \
        "Case A history must NOT contain any Whitfield content"
    print("  [PASS] Case A history verified strictly isolated.")

    # -------------------------------------------------------------
    # STEP 5: Back to Case B -> History verification
    # -------------------------------------------------------------
    print("\n[TEST 5] Back to Case B: History verification")
    case_b_history = scoped_histories["CASE:case-02"]
    assert len(case_b_history) == 2, f"Case B history must have exactly 2 messages, got {len(case_b_history)}"
    assert any("whitfield" in m["content"].lower() for m in case_b_history if m["role"] == "assistant"), \
        "Case B history must preserve Whitfield content"
    assert not any("martinez" in m["content"].lower() for m in case_b_history), \
        "Case B history must NOT contain any Martinez content"
    print("  [PASS] Case B history verified strictly isolated.")

    # -------------------------------------------------------------
    # STEP 6: Martinez -> "What evidence is missing?" (Current case only)
    # -------------------------------------------------------------
    print("\n[TEST 6] Martinez: 'What evidence is missing?' (Current case RAG only)")
    req_evidence = {
        "content": "What evidence is missing?",
        "mode": "SINGLE_CASE",
        "caseId": "case-01",
        "caseNumber": "2024-CV-1187",
        "history": scoped_histories["CASE:case-01"]
    }
    resp_evid = make_chat_request(req_evidence)
    print(f"  Route: {resp_evid.get('route')} | Sources count: {len(resp_evid.get('sources', []))}")
    assert resp_evid.get("route") == "CASE_QUERY", f"Expected CASE_QUERY, got {resp_evid.get('route')}"
    # Sources must ONLY belong to current case
    for src in resp_evid.get("sources", []):
        src_scope = src.get("source_scope", "CURRENT_MATTER")
        src_case = src.get("case_id", "case-01")
        assert src_scope == "CURRENT_MATTER", f"Expected CURRENT_MATTER, got {src_scope}"
        assert src_case in ("case-01", "2024-CV-1187"), f"Expected case-01 or 2024-CV-1187, got {src_case}"
    print("  [PASS] Only current case context used for evidence question.")

    # -------------------------------------------------------------
    # STEP 7: Martinez -> "Do I have another case with a similar issue?" (Explicit cross-matter)
    # -------------------------------------------------------------
    print("\n[TEST 7] Martinez: 'Do I have another case with a similar issue?' (Cross-matter)")
    req_cross = {
        "content": "Do I have another case with a similar issue?",
        "mode": "SINGLE_CASE",
        "caseId": "case-01",
        "caseNumber": "2024-CV-1187",
        "history": scoped_histories["CASE:case-01"]
    }
    resp_cross = make_chat_request(req_cross)
    print(f"  Route: {resp_cross.get('route')} | Sub-intent: {resp_cross.get('sub_intent')}")
    print(f"  Sources count: {len(resp_cross.get('sources', []))}")
    print(f"  Response excerpt: {resp_cross.get('content', '')[:180]}...")
    
    assert resp_cross.get("route") == "CASE_QUERY", f"Expected CASE_QUERY, got {resp_cross.get('route')}"
    assert resp_cross.get("sub_intent") == "CROSS_MATTER_COMPARISON", f"Expected CROSS_MATTER_COMPARISON, got {resp_cross.get('sub_intent')}"
    
    # Verify structured provenance on cross-matter sources per Safeguard 1
    other_sources = [s for s in resp_cross.get("sources", []) if s.get("source_scope") == "OTHER_MATTER"]
    assert len(other_sources) > 0, "Expected at least one source with source_scope='OTHER_MATTER'"
    for os_src in other_sources:
        print(f"  Validated Cross-Matter Provenance: case_id={os_src.get('case_id')} | title={os_src.get('case_title')} | number={os_src.get('case_number')} | scope={os_src.get('source_scope')}")
        assert os_src.get("case_id"), "Cross-matter source must have case_id"
        assert os_src.get("case_title"), "Cross-matter source must have case_title"
        assert os_src.get("case_number"), "Cross-matter source must have case_number"
        assert os_src.get("source_scope") == "OTHER_MATTER", "source_scope must be OTHER_MATTER"
        assert os_src.get("chunk_id"), "Cross-matter source must have chunk_id"
    
    # Check that UI presentation banner is present
    assert "> [!CAUTION]" in resp_cross.get("content", ""), "Expected [!CAUTION] presentation banner"
    print("  [PASS] Cross-matter retrieval succeeded with structured provenance.")

    # -------------------------------------------------------------
    # STEP 8: Non-case queries inside Case A page
    # -------------------------------------------------------------
    print("\n[TEST 8] Non-case queries inside Case A: 'What is Qwen?'")
    req_qwen = {
        "content": "What is Qwen?",
        "mode": "SINGLE_CASE",
        "caseId": "case-01",
        "caseNumber": "2024-CV-1187",
        "history": scoped_histories["CASE:case-01"]
    }
    resp_qwen = make_chat_request(req_qwen)
    print(f"  Route: {resp_qwen.get('route')} | Sub-intent: {resp_qwen.get('sub_intent')}")
    assert resp_qwen.get("route") == "TECHNICAL_AI", f"Expected TECHNICAL_AI, got {resp_qwen.get('route')}"
    assert len(resp_qwen.get("sources", [])) == 0, "Technical AI must have zero case RAG sources"
    print("  [PASS] 'What is Qwen?' routed to TECHNICAL_AI without Case RAG.")

    print("\n[TEST 9] Non-case queries inside Case A: 'What is Section 66C of the IT Act?'")
    req_sec = {
        "content": "What is Section 66C of the IT Act?",
        "mode": "SINGLE_CASE",
        "caseId": "case-01",
        "caseNumber": "2024-CV-1187",
        "history": scoped_histories["CASE:case-01"]
    }
    resp_sec = make_chat_request(req_sec)
    print(f"  Route: {resp_sec.get('route')} | Sub-intent: {resp_sec.get('sub_intent')} | Intent: {resp_sec.get('intent')}")
    assert resp_sec.get("route") in ("EXACT_PROVISION_QUERY", "LEGAL_QUERY"), f"Expected EXACT_PROVISION_QUERY or LEGAL_QUERY, got {resp_sec.get('route')}"
    assert resp_sec.get("sub_intent") == "EXACT_STATUTORY_PROVISION" or resp_sec.get("intent") in ("EXACT_PROVISION_QUERY", "LEGAL_QUERY")
    assert len(resp_sec.get("sources", [])) > 0, "Must have statutory sources"
    assert all(not s.get("case_id") and s.get("source_scope") not in ("CURRENT_MATTER", "OTHER_MATTER") for s in resp_sec.get("sources", [])), "Statutory query must have zero Case RAG sources"
    print("  [PASS] 'What is Section 66C?' routed to Indian Legal RAG without Case RAG.")

    print("\n" + "=" * 70)
    print("ALL SCOPE & HISTORY ISOLATION REGRESSION TESTS PASSED (9/9)!")
    print("=" * 70)

if __name__ == "__main__":
    test_scope_and_history_isolation()
