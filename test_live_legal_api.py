#!/usr/bin/env python3
"""Live integration test suite verifying FastAPI /api/v1/ai/chat endpoints."""

import urllib.request
import json
import sys


def post_chat(content, history=None):
    url = "http://localhost:8008/api/v1/ai/chat"
    payload = {
        "content": content,
        "conversationId": "test-conv-e2e",
        "history": history or []
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_tests():
    print("==================================================================")
    print("LEGALAI ??? LIVE FRONTEND/API ENDPOINT VERIFICATION")
    print("==================================================================")

    # 1. Exact Section 89 Companies Act
    print("\n[TEST 1] Query: 'What is Section 89 of the Companies Act, 2013?'")
    r1 = post_chat("What is Section 89 of the Companies Act, 2013?")
    resp_text1 = r1.get("content", "")
    sources1 = r1.get("sources", [])
    print(f"Response preview: {resp_text1[:150]}...")
    print(f"Sources: {[s.get('section_number') for s in sources1]}")
    assert any("Section 89" in str(s.get("section_number")) for s in sources1), "Section 89 missing from sources"
    assert "Section 89" in resp_text1, "Section 89 missing from response text"
    assert r1.get("requires_verification") is False, "Exact provision should not require verification"
    print("??? TEST 1 PASSED: Exact Section 89 retrieved cleanly.")

    # 2. Sequential turn (Inherits Companies Act)
    print("\n[TEST 2] Sequential Query: 'What about Section 90?'")
    h1 = [
        {"role": "user", "content": "What is Section 89 of the Companies Act, 2013?"},
        {"role": "assistant", "content": resp_text1}
    ]
    r2 = post_chat("What about Section 90?", history=h1)
    resp_text2 = r2.get("content", "")
    sources2 = r2.get("sources", [])
    print(f"Response preview: {resp_text2[:150]}...")
    print(f"Sources: {[s.get('section_number') for s in sources2]}")
    assert any("Section 90" in str(s.get("section_number")) for s in sources2), "Section 90 missing from sources"
    assert "Section 90" in resp_text2, "Section 90 missing from response text"
    print("??? TEST 2 PASSED: Context inherited Companies Act and retrieved Section 90.")

    # 3. Explicit Act Override
    print("\n[TEST 3] Override Query: 'What about Section 21 of the POCSO Act?'")
    r3 = post_chat("What about Section 21 of the POCSO Act?", history=h1)
    resp_text3 = r3.get("content", "")
    sources3 = r3.get("sources", [])
    print(f"Response preview: {resp_text3[:150]}...")
    print(f"Sources: {[s.get('section_number') for s in sources3]}")
    assert any("Protection of Children" in str(s.get("act_name", "")) or "Protection of Children" in str(s.get("section_number", "")) for s in sources3), "POCSO Act not in sources"
    print("??? TEST 3 PASSED: Context correctly overridden by explicit POCSO Act.")

    # 4. Ambiguous Provision Clarification
    print("\n[TEST 4] Ambiguous Query: 'Tell me about Section 49A.'")
    r4 = post_chat("Tell me about Section 49A.")
    resp_text4 = r4.get("content", "")
    print(f"Response preview: {resp_text4[:150]}...")
    assert "Which Act or Code" in resp_text4 or "Clarification" in resp_text4, "Ambiguity clarification prompt missing"
    assert len(r4.get("sources", [])) == 0, "Ambiguous query should not return unverified sources"
    print("??? TEST 4 PASSED: Ambiguous query cleanly requested clarification without guessing.")

    # 5. Verified Absence / Safe Abstention
    print("\n[TEST 5] Absence Query: 'What is Section 49A of the Companies Act, 2013?'")
    r5 = post_chat("What is Section 49A of the Companies Act, 2013?")
    resp_text5 = r5.get("content", "")
    print(f"Response preview: {resp_text5[:150]}...")
    assert "Section 49A could not be verified" in resp_text5 or "not exist" in resp_text5 or "Absence Notice" in resp_text5, "Absence notice missing"
    assert len(r5.get("sources", [])) == 0, "Missing section should not hallucinate sources"
    assert r5.get("requires_verification") is True, "Absence should require verification"
    print("??? TEST 5 PASSED: Safe abstention triggered without hallucinating.")

    # 6. Order 39 Rule 1 CPC (Order-Rule namespace)
    print("\n[TEST 6] Procedural Rule: 'Explain Order 39 Rule 1 CPC'")
    r6 = post_chat("Explain Order 39 Rule 1 CPC")
    resp_text6 = r6.get("content", "")
    sources6 = r6.get("sources", [])
    print(f"Response preview: {resp_text6[:150]}...")
    print(f"Sources: {[s.get('section_number') for s in sources6]}")
    assert any("Civil Procedure" in str(s.get("act_name", "")) or "Rule" in str(s.get("section_number", "")) for s in sources6), "CPC Order Rule missing"
    print("??? TEST 6 PASSED: Order-Rule namespace retrieved.")

    # 7. Constitutional Article (Article 21)
    print("\n[TEST 7] Constitutional Article: 'What is Article 21 of the Constitution of India?'")
    r7 = post_chat("What is Article 21 of the Constitution of India?")
    resp_text7 = r7.get("content", "")
    sources7 = r7.get("sources", [])
    print(f"Response preview: {resp_text7[:150]}...")
    print(f"Sources: {[s.get('section_number') for s in sources7]}")
    assert any("Article 21" in str(s.get("section_number", "")) or "Constitution" in str(s.get("act_name", "")) for s in sources7), "Article 21 missing"
    print("??? TEST 7 PASSED: Article namespace retrieved.")

    print("\n==================================================================")
    print("ALL 7 LIVE INTEGRATION TESTS PASSED (7/7)!")
    print("==================================================================")


if __name__ == "__main__":
    run_tests()

