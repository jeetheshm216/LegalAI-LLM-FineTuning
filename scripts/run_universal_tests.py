import requests
import json
import time

BASE_URL = "http://127.0.0.1:8008"

def test_query(title, content, expected_type, expected_route, case_id=None, mode=None, history=None):
    payload = {
        "content": content,
        "mode": mode or "GENERAL",
        "caseId": case_id,
        "selectedCases": [case_id] if case_id else [],
        "history": history or []
    }
    t0 = time.time()
    resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=240)
    dur = round(time.time() - t0, 3)
    if resp.status_code != 200:
        print(f"  [ERROR] {title}: HTTP {resp.status_code} - {resp.text}")
        return False
    data = resp.json()
    q_type = data.get("query_type")
    route = data.get("route")
    sources = data.get("sources", [])
    content_preview = data.get("content", "").replace("\n", " ")[:100]
    
    type_ok = (q_type == expected_type)
    route_ok = (route == expected_route)
    passed = type_ok and route_ok
    status_str = "PASS" if passed else "FAIL"
    print(f"  [{status_str}] {title} ({dur}s)")
    print(f"         Query: '{content}'")
    print(f"         Result: type={q_type} (exp {expected_type}), route={route} (exp {expected_route}), sources={len(sources)}")
    print(f"         Preview: {content_preview}...")
    return passed

def run_all():
    print("=========================================================")
    print("RUNNING EXTENSIVE LIVE TEST MATRIX FOR UNIVERSAL WORKFLOW")
    print("=========================================================")
    failures = 0
    total = 0

    # Section A: Technical AI
    print("\n--- Section A: Technical AI (Base Qwen, No Case RAG, No Legal RAG) ---")
    tech_queries = [
        ("Tech: Qwen explanation", "What is Qwen?", "TECHNICAL_AI", "TECHNICAL_AI"),
        ("Tech: Explain Qwen variation", "Can you explain Qwen", "TECHNICAL_AI", "TECHNICAL_AI"),
        ("Tech: LLM explanation", "What is an LLM?", "TECHNICAL_AI", "TECHNICAL_AI"),
        ("Tech: RAG explanation", "Explain retrieval augmented generation.", "TECHNICAL_AI", "TECHNICAL_AI"),
        ("Tech: LoRA explanation", "What does LoRA mean?", "TECHNICAL_AI", "TECHNICAL_AI"),
        ("Tech: Fine-tuning explanation", "Why do people fine-tune language models?", "TECHNICAL_AI", "TECHNICAL_AI"),
        ("Tech: RAG vs Fine-tuning", "How does RAG differ from fine-tuning?", "TECHNICAL_AI", "TECHNICAL_AI"),
    ]
    for title, q, exp_t, exp_r in tech_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r, case_id="case-01", mode="SINGLE_CASE"):
            failures += 1

    # Section B: System Information
    print("\n--- Section B: System Information (Verified Architecture Context, No MODEL_AI) ---")
    sys_queries = [
        ("System: Model powering LegalAI", "What model powers LegalAI?", "SYSTEM_INFO", "SYSTEM_INFO"),
        ("System: Powers assistant", "What powers this assistant?", "SYSTEM_INFO", "SYSTEM_INFO"),
        ("System: How built", "How was LegalAI built?", "SYSTEM_INFO", "SYSTEM_INFO"),
        ("System: Technologies behind", "What technologies are behind this system?", "SYSTEM_INFO", "SYSTEM_INFO"),
    ]
    for title, q, exp_t, exp_r in sys_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r, case_id="case-01", mode="SINGLE_CASE"):
            failures += 1

    # Section C: Legal Concepts (Without word 'legal' or 'law')
    print("\n--- Section C: Legal Concepts (Substantive Indian Law) ---")
    legal_concept_queries = [
        ("Legal Concept: Negligence", "What is negligence?", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Legal Concept: Bail", "What is bail?", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Legal Concept: Self-defence", "Explain self-defence.", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Legal Concept: Post-FIR procedure", "What happens after an FIR?", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Legal Concept: Consideration", "What is consideration?", "LEGAL_QUERY", "LEGAL_QUERY"),
    ]
    for title, q, exp_t, exp_r in legal_concept_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r):
            failures += 1

    # Section D: Exact Provisions (Authoritative Statutory RAG)
    print("\n--- Section D: Exact Statutory Provisions (Strict Statutory Grounding) ---")
    stat_queries = [
        ("Statute: IT Act 66C", "What is Section 66C of the IT Act?", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Statute: BNS Section 103", "What does BNS Section 103 cover?", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Statute: BSA Section 63", "Explain Section 63 of BSA.", "LEGAL_QUERY", "LEGAL_QUERY"),
        ("Statute: Constitution Article 21", "What does Article 21 provide?", "LEGAL_QUERY", "LEGAL_QUERY"),
    ]
    for title, q, exp_t, exp_r in stat_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r):
            failures += 1

    # Section E: Case Analysis (Evidentiary Inquiries & Document RAG)
    print("\n--- Section E: Case Analysis (Evidentiary Inquiries & Case RAG) ---")
    case_queries = [
        ("Case: Missing evidence", "What evidence is missing?", "CASE_QUERY", "CASE_QUERY"),
        ("Case: Key facts", "What are the key facts in my case?", "CASE_QUERY", "CASE_QUERY"),
        ("Case: Contradictions", "What contradictions are present?", "CASE_QUERY", "CASE_QUERY"),
    ]
    for title, q, exp_t, exp_r in case_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r, case_id="case-01", mode="SINGLE_CASE"):
            failures += 1

    # Section F: Case Management (Existing Application Database cases table)
    print("\n--- Section F: Case Management (Portfolio DB queries) ---")
    mgmt_queries = [
        ("Case Mgmt: Focus case", "Which case should I focus on?", "CASE_MANAGEMENT", "CASE_MANAGEMENT"),
        ("Case Mgmt: Highest priority", "Which case has the highest priority?", "CASE_MANAGEMENT", "CASE_MANAGEMENT"),
        ("Case Mgmt: Upcoming hearings", "What hearings are coming up?", "CASE_MANAGEMENT", "CASE_MANAGEMENT"),
        ("Case Mgmt: Next hearing", "When is my next hearing?", "CASE_MANAGEMENT", "CASE_MANAGEMENT"),
        ("Case Mgmt: Urgent matters", "Which matters are urgent?", "CASE_MANAGEMENT", "CASE_MANAGEMENT"),
    ]
    for title, q, exp_t, exp_r in mgmt_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r, case_id="case-01", mode="SINGLE_CASE"):
            failures += 1

    # Section G: Out of Scope
    print("\n--- Section G: Out of Scope (Clear non-legal boundary) ---")
    oos_queries = [
        ("OOS: Python game", "Write a Python game.", "OUT_OF_SCOPE", "OUT_OF_SCOPE"),
        ("OOS: Football match", "Who won yesterday's football match?", "OUT_OF_SCOPE", "OUT_OF_SCOPE"),
        ("OOS: Recommend laptop", "Recommend a laptop.", "OUT_OF_SCOPE", "OUT_OF_SCOPE"),
        ("OOS: Movie plot", "Tell me a movie plot.", "OUT_OF_SCOPE", "OUT_OF_SCOPE"),
        ("OOS: Recipe", "Give me a recipe.", "OUT_OF_SCOPE", "OUT_OF_SCOPE"),
    ]
    for title, q, exp_t, exp_r in oos_queries:
        total += 1
        if not test_query(title, q, exp_t, exp_r):
            failures += 1

    # Section H: Context Isolation Sequences
    print("\n--- Section H: Context Isolation Sequences (Independent Semantic Understanding) ---")
    isolation_tests = [
        ("Isolation: CASE -> TECHNICAL ('What evidence is missing?' -> 'What is Qwen?')",
         "What is Qwen?", "TECHNICAL_AI", "TECHNICAL_AI",
         [{"role": "user", "content": "What evidence is missing?", "query_type": "CASE_QUERY"}]),
        ("Isolation: LEGAL -> TECHNICAL ('What is Section 66C?' -> 'What is Qwen?')",
         "What is Qwen?", "TECHNICAL_AI", "TECHNICAL_AI",
         [{"role": "user", "content": "What is Section 66C of the IT Act?", "query_type": "LEGAL_QUERY"}]),
        ("Isolation: CASE -> CASE MGMT ('What is the Martinez case about?' -> 'Which case should I focus on?')",
         "Which case should I focus on?", "CASE_MANAGEMENT", "CASE_MANAGEMENT",
         [{"role": "user", "content": "What is the Martinez case about?", "query_type": "CASE_QUERY"}]),
        ("Isolation: TECHNICAL -> LEGAL ('What is RAG?' -> 'Explain Section 66C.')",
         "Explain Section 66C of IT Act.", "LEGAL_QUERY", "LEGAL_QUERY",
         [{"role": "user", "content": "What is RAG?", "query_type": "TECHNICAL_AI"}]),
        ("Isolation: SYSTEM -> LEGAL ('What model powers LegalAI?' -> 'Explain Section 66C.')",
         "Explain Section 66C of IT Act.", "LEGAL_QUERY", "LEGAL_QUERY",
         [{"role": "user", "content": "What model powers LegalAI?", "query_type": "SYSTEM_INFO"}]),
        ("Isolation: TECHNICAL -> CASE ('What is LoRA?' -> 'What evidence is missing?')",
         "What evidence is missing?", "CASE_QUERY", "CASE_QUERY",
         [{"role": "user", "content": "What is LoRA?", "query_type": "TECHNICAL_AI"}]),
    ]
    for title, q, exp_t, exp_r, hist in isolation_tests:
        total += 1
        if not test_query(title, q, exp_t, exp_r, case_id="case-01", mode="SINGLE_CASE", history=hist):
            failures += 1

    print("\n=========================================================")
    print(f"LIVE TEST MATRIX RESULTS: {total - failures} / {total} PASSED")
    if failures == 0:
        print("ALL TESTS PASSED PERFECTLY!")
    else:
        print(f"FAILURES DETECTED: {failures}")
    print("=========================================================")
    return failures == 0

if __name__ == "__main__":
    run_all()
