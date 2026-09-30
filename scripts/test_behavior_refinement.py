import requests
import json

BASE_URL = "http://127.0.0.1:8008"

def test_conversational_refinements():
    print("=====================================================")
    print("LEGALAI CONVERSATIONAL BEHAVIOR REFINEMENT TESTS")
    print("=====================================================")

    # 1. Normal Conversation
    print("\n[1] NORMAL CONVERSATION")
    normal_convs = ["hi", "how are you doing?", "thanks", "okay", "cool", "nice", "great"]
    for q in normal_convs:
        r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}).json()
        print(f"Query: '{q}' -> Intent: {r.get('query_type')}")
        assert r.get("query_type") == "CONVERSATIONAL", f"Expected CONVERSATIONAL for '{q}', got {r.get('query_type')}"
        assert len(r.get("content", "")) > 0

    # 2. Social / Profanity / Interpersonal (Must be CONVERSATIONAL, NOT OUT_OF_SCOPE!)
    print("\n[2] SOCIAL / PROFANITY / INTERPERSONAL")
    social_cases = [
        ("fuck you", "That’s not appropriate"),
        ("you're useless", "I'm sorry"),
        ("this is stupid", "I hear your frustration"),
        ("damn", "I hear your frustration"),
        ("what the hell", "I hear your frustration"),
        ("you suck", "I'm sorry")
    ]
    for q, expected_snippet in social_cases:
        r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}).json()
        intent = r.get("query_type")
        content = r.get("content", "")
        print(f"Query: '{q}' -> Intent: {intent} | Response: {content}")
        assert intent == "CONVERSATIONAL", f"Expected CONVERSATIONAL for '{q}', got {intent}"
        assert "only answer legal" not in content.lower(), f"Must not cite scope boundary for purely social message: {content}"

    # 3. Ambiguous Queries
    print("\n[3] AMBIGUOUS QUERIES")
    ambiguous_cases = ["49p", "xyz", "what about that?"]
    for q in ambiguous_cases:
        r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}).json()
        intent = r.get("query_type")
        content = r.get("content", "")
        print(f"Query: '{q}' -> Intent: {intent} | Response: {content}")
        assert intent == "AMBIGUOUS", f"Expected AMBIGUOUS for '{q}', got {intent}"
        assert any(term in content.lower() for term in ["clarify", "context", "mean by", "detail"]), (
            f"Expected clarification request for '{q}', got {content}"
        )
        assert "only answer legal" not in content.lower(), "Must not use robotic scope refusal for ambiguous queries"

    # 4. Strict Out of Scope
    print("\n[4] STRICT NON-LEGAL OUT OF SCOPE")
    oos_cases = [
        "what is Python?",
        "write C++ hello world",
        "give me odd/even Python code",
        "what is the latest Vijay movie?",
        "who won yesterday's cricket match?",
        "recommend a laptop",
        "how do I cook biryani"
    ]
    for q in oos_cases:
        r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}).json()
        intent = r.get("query_type")
        content = r.get("content", "")
        print(f"Query: '{q}' -> Intent: {intent} | Response: {content[:120]}...")
        assert intent == "OUT_OF_SCOPE", f"Expected OUT_OF_SCOPE for '{q}', got {intent}"
        assert "scope" in content.lower() or "area" in content.lower()

    # 5. Legal Queries
    print("\n[5] LEGAL QUERIES")
    legal_cases = [
        "what is BNS Section 103?",
        "what is BNSS Section 482?",
        "what is BSA Section 63?",
        "what punishment applies?"
    ]
    for q in legal_cases:
        r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}).json()
        intent = r.get("query_type")
        content = r.get("content", "")
        print(f"Query: '{q}' -> Intent: {intent} | Response: {content[:100]}...")
        assert intent == "LEGAL_QUERY", f"Expected LEGAL_QUERY for '{q}', got {intent}"

    # 6. Case Queries
    print("\n[6] CASE QUERIES")
    case_cases = [
        "what happened in my case?",
        "what evidence is missing?",
        "summarize this case"
    ]
    for q in case_cases:
        r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}).json()
        intent = r.get("query_type")
        content = r.get("content", "")
        print(f"Query: '{q}' -> Intent: {intent} | Response: {content[:100]}...")
        assert intent == "CASE_QUERY", f"Expected CASE_QUERY for '{q}', got {intent}"

    # 7. Context Handling
    print("\n[7] CONTEXT HANDLING")
    # 7a. Non-legal follow-up
    r_py1 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "write a python code"}).json()
    assert r_py1.get("query_type") == "OUT_OF_SCOPE"
    hist_py = [
        {"role": "user", "content": "write a python code"},
        {"role": "assistant", "content": r_py1.get("content", "")}
    ]
    r_py2 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "for odd or even", "history": hist_py}).json()
    print("Python follow-up intent:", r_py2.get("query_type"))
    assert r_py2.get("query_type") == "OUT_OF_SCOPE", f"Expected OUT_OF_SCOPE for follow-up, got {r_py2.get('query_type')}"

    # 7b. Movie follow-up
    r_mov1 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "what is the latest Vijay movie?"}).json()
    assert r_mov1.get("query_type") == "OUT_OF_SCOPE"
    hist_mov = [
        {"role": "user", "content": "what is the latest Vijay movie?"},
        {"role": "assistant", "content": r_mov1.get("content", "")}
    ]
    r_mov2 = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "what about the previous one?", "history": hist_mov}).json()
    print("Movie follow-up intent:", r_mov2.get("query_type"))
    assert r_mov2.get("query_type") == "OUT_OF_SCOPE", f"Expected OUT_OF_SCOPE for movie follow-up, got {r_mov2.get('query_type')}"

    # 7c. Override movie context with explicit legal statute
    r_ovr = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "what is BNS Section 103?", "history": hist_mov}).json()
    print("Legal override intent:", r_ovr.get("query_type"))
    assert r_ovr.get("query_type") == "LEGAL_QUERY", f"Expected LEGAL_QUERY for override, got {r_ovr.get('query_type')}"

    # 7d. Legal follow-up with ambiguous question resolving via context
    hist_legal = [
        {"role": "user", "content": "what is BNS section 103?"},
        {"role": "assistant", "content": r_ovr.get("content", "")}
    ]
    r_leg_follow = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": "what about that?", "history": hist_legal}).json()
    print("'what about that?' with legal context intent:", r_leg_follow.get("query_type"))
    assert r_leg_follow.get("query_type") == "LEGAL_QUERY", f"Expected LEGAL_QUERY with legal context, got {r_leg_follow.get('query_type')}"

    print("\n=====================================================")
    print("ALL CONVERSATIONAL BEHAVIOR REFINEMENT TESTS PASSED!")
    print("=====================================================")

if __name__ == "__main__":
    test_conversational_refinements()
