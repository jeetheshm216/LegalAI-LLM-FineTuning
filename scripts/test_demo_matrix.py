import requests
import json

BASE_URL = "http://127.0.0.1:8008"

def test_demo_cases():
    print("=====================================================")
    print("LEGALAI DEMO MATRIX VERIFICATION (SECTION 26)")
    print("=====================================================")

    # Test 1: Greeting
    print('\n[TEST 1] User: "Hi"')
    r1 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "Hi"}).json()
    print("Intent:", r1.get("query_type"))
    print("Response:", r1.get("content", ""))
    assert r1.get("query_type") == "CONVERSATIONAL", f"Expected CONVERSATIONAL, got {r1.get('query_type')}"
    assert any(g in r1.get("content", "") for g in ["Hey", "Hello", "Good", "Hi"]), "Greeting expected"

    # Test 2: Vijay movie
    print('\n[TEST 2] User: "What is the last Vijay movie?"')
    r2 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "What is the last Vijay movie?"}).json()
    print("Intent:", r2.get("query_type"))
    resp2 = r2.get("content", "")
    print("Response:", resp2)
    assert r2.get("query_type") == "OUT_OF_SCOPE", f"Expected OUT_OF_SCOPE, got {r2.get('query_type')}"
    assert "scope" in resp2.lower() or "area" in resp2.lower()
    assert "Leo" not in resp2 and "GOAT" not in resp2 and "Varisu" not in resp2, "Must not answer movie question!"

    # Test 3: C++ code
    print('\n[TEST 3] User: "C++ code for creating a Python file"')
    r3 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "C++ code for creating a Python file"}).json()
    print("Intent:", r3.get("query_type"))
    resp3 = r3.get("content", "")
    print("Response:", resp3)
    assert r3.get("query_type") == "OUT_OF_SCOPE", f"Expected OUT_OF_SCOPE, got {r3.get('query_type')}"
    assert "#include" not in resp3 and "ofstream" not in resp3, "Must not provide C++ code!"

    # Test 4: BNS Section 103
    print('\n[TEST 4] User: "What is BNS Section 103?"')
    r4 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "What is BNS Section 103?"}).json()
    print("Intent:", r4.get("query_type"))
    resp4 = r4.get("content", "")
    print("Response (first 250 chars):", resp4[:250])
    assert r4.get("query_type") == "LEGAL_QUERY", f"Expected LEGAL_QUERY, got {r4.get('query_type')}"
    assert "103" in resp4 or "murder" in resp4.lower() or "bns" in resp4.lower()

    # Test 5: Case query
    print('\n[TEST 5] User: "What happened in my case?"')
    r5 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "What happened in my case?"}).json()
    print("Intent:", r5.get("query_type"))
    resp5 = r5.get("content", "")
    print("Response (first 250 chars):", resp5[:250])
    assert r5.get("query_type") == "CASE_QUERY", f"Expected CASE_QUERY, got {r5.get('query_type')}"

    # Test 6: Mixed Greeting + Legal Query
    print('\n[TEST 6] User: "Hey, what is BNS Section 103?"')
    r6 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "Hey, what is BNS Section 103?"}).json()
    print("Intent:", r6.get("query_type"))
    resp6 = r6.get("content", "")
    print("Response (first 250 chars):", resp6[:250])
    assert r6.get("query_type") == "LEGAL_QUERY", f"Expected LEGAL_QUERY, got {r6.get('query_type')}"

    # Test 7: Non-legal follow-up context
    print('\n[TEST 7] User: "Write a Python code" -> Follow-up: "for odd or even"')
    r7_1 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "Write a Python code"}).json()
    print("Turn 1 Intent:", r7_1.get("query_type"))
    assert r7_1.get("query_type") == "OUT_OF_SCOPE"

    history = [
        {"role": "user", "content": "Write a Python code"},
        {"role": "assistant", "content": r7_1.get("content", "")}
    ]
    r7_2 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={
        "content": "for odd or even",
        "history": history
    }).json()
    print("Turn 2 Intent:", r7_2.get("query_type"))
    resp7_2 = r7_2.get("content", "")
    print("Turn 2 Response:", resp7_2)
    assert r7_2.get("query_type") == "OUT_OF_SCOPE", f"Expected OUT_OF_SCOPE for follow-up, got {r7_2.get('query_type')}"
    assert "def " not in resp7_2 and "% 2" not in resp7_2, "Must not generate python code!"

    print("\n=====================================================")
    print("ALL 7 SECTION 26 DEMO TESTS PASSED WITH 100% SUCCESS!")
    print("=====================================================")

if __name__ == "__main__":
    test_demo_cases()
