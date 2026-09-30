import requests
import json

BASE_URL = "http://127.0.0.1:8008/api/v1/ai/chat"

tests = [
    # (label, query, case_id, expected_intent, expected_sub, expected_in_content, forbidden_in_content)
    ("Test 1: Typos identity", "what i syour name", "case-01", "CONVERSATIONAL", "ASSISTANT_IDENTITY", "LegalAI", ["LawSikho", "9/10", "<svg>"]),
    ("Test 1b: Identity clean", "who are you", None, "CONVERSATIONAL", "ASSISTANT_IDENTITY", "LegalAI", ["LawSikho"]),
    ("Test 2: Priority inside case", "what is the priority of this case", "case-01", "CASE_MANAGEMENT", "CASE_PRIORITY", "Priority Areas", ["9/10", "arbitrary"]),
    ("Test 2b: Importance inside case", "how important is this case", "case-01", "CASE_MANAGEMENT", "CASE_PRIORITY", "Priority Areas", ["9/10"]),
    ("Test 3: Key points typo inside case", "what is the kay points in this case", "case-01", "CASE_QUERY", "CASE_KEY_POINTS", "KEY POINTS", []),
    ("Test 3b: Key points informal", "what r the key pionts", "case-01", "CASE_QUERY", "CASE_KEY_POINTS", "KEY POINTS", []),
    ("Test 4: Technical AI with case open", "what is qwen", "case-01", "TECHNICAL_AI", "TECHNICAL_CONCEPT", "Qwen", ["Martinez"]),
    ("Test 4b: Technical AI RAG with case open", "what is rag", "case-01", "TECHNICAL_AI", "TECHNICAL_CONCEPT", "Retrieval", ["Martinez"]),
    ("Test 5: Statutory lookup with case open", "what is section 66c", "case-01", "EXACT_PROVISION_QUERY", "EXACT_STATUTORY_PROVISION", "Section 66C", ["Martinez"]),
    ("Test 5b: BNS 103 lookup", "what is bns 103", "case-01", "EXACT_PROVISION_QUERY", "EXACT_STATUTORY_PROVISION", "103", []),
    ("Test 6: Case summary typo", "waht is the matter", "case-01", "CASE_QUERY", "CASE_SUMMARY", "Martinez", []),
    ("Test 6b: Evidence typo", "what evidnce do we have", "case-01", "CASE_QUERY", "CASE_EVIDENCE", "EVIDENCE", []),
    ("Test 7: Focus outside case", "what should i focus on", None, "AMBIGUOUS", "CLARIFICATION_REQUIRED", "Which case or task would you like me to focus on?", []),
]

print("=========================================================")
print("LIVE HTTP ENDPOINT VALIDATION (http://127.0.0.1:8008)")
print("=========================================================")

all_passed = True

for label, query, cid, exp_intent, exp_sub, exp_in_content, forbidden_list in tests:
    payload = {
        "content": query,
        "mode": "SINGLE_CASE" if cid else "GENERAL",
        "caseId": cid,
        "selectedCases": [cid] if cid else []
    }
    
    try:
        resp = requests.post(BASE_URL, json=payload, timeout=180)
        if resp.status_code != 200:
            print(f"FAILED {label}: HTTP status {resp.status_code} - {resp.text}")
            all_passed = False
            continue
            
        data = resp.json()
        got_intent = data.get("intent") or data.get("query_type")
        got_sub = data.get("sub_intent")
        content = data.get("content", "")
        
        # Check intent
        intent_match = (got_intent == exp_intent)
        sub_match = (got_sub == exp_sub) if exp_sub else True
        content_match = (exp_in_content.lower() in content.lower())
        forbidden_clean = not any(f.lower() in content.lower() for f in forbidden_list)
        
        passed = intent_match and sub_match and content_match and forbidden_clean
        status_str = "PASS" if passed else "FAIL"
        
        if not passed:
            all_passed = False
            
        print(f"[{status_str}] {label}")
        print(f"       Query: '{query}' (caseId={cid})")
        print(f"       Intent: got {got_intent} (exp {exp_intent}), sub: got {got_sub} (exp {exp_sub})")
        print(f"       Content Snippet: {content[:100].replace(chr(10), ' ')}...")
        if not forbidden_clean:
            print(f"       [ERROR] Forbidden words found in content!")
        print()
    except Exception as e:
        print(f"[ERROR] {label}: {e}")
        all_passed = False

if all_passed:
    print("ALL LIVE ENDPOINT VALIDATION TESTS PASSED 100%!")
else:
    print("SOME TESTS FAILED - REVIEW LOG ABOVE.")
