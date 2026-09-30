test_path = "/home/sece2026-student07/legalai-finetuning/tests/test_query_router.py"
with open(test_path, "r", encoding="utf-8") as f:
    code = f.read()

new_tests = """
def test_follow_up_context_tracking():
    router = QueryRouter()
    
    # Sequence B: write a python code -> for odd or even
    history_python = [
        {"role": "user", "content": "write a python code"},
        {"role": "assistant", "content": "Absolutely! 😊 What Python program would you like to build?", "query_type": "GENERAL_NON_LEGAL"}
    ]
    res_followup = router.classify("for odd or even", conversation_history=history_python)
    assert res_followup.intent == QueryIntent.GENERAL_NON_LEGAL, (
        f"Expected GENERAL_NON_LEGAL for 'for odd or even', got {res_followup.intent} (reason: {res_followup.reason})"
    )
    print("PASS: test_follow_up_context_tracking (for odd or even -> GENERAL_NON_LEGAL)")

    # Sequence C: context switch to legal (what is BNS section 103?)
    history_after_odd_even = history_python + [
        {"role": "user", "content": "for odd or even"},
        {"role": "assistant", "content": "Sure! Here is a python program...", "query_type": "GENERAL_NON_LEGAL"}
    ]
    res_legal_switch = router.classify("what is BNS section 103?", conversation_history=history_after_odd_even)
    assert res_legal_switch.intent == QueryIntent.LEGAL_QUERY, (
        f"Expected LEGAL_QUERY for 'what is BNS section 103?' after coding history, got {res_legal_switch.intent}"
    )
    print("PASS: test_follow_up_context_tracking (context switch to legal -> LEGAL_QUERY)")

    # Sequence E: Out of scope inquiry
    res_movie = router.classify("recommend me a movie")
    assert res_movie.intent == QueryIntent.GENERAL_NON_LEGAL, (
        f"Expected GENERAL_NON_LEGAL for 'recommend me a movie', got {res_movie.intent}"
    )
    assert "OUT_OF_SCOPE" in res_movie.matched_patterns, (
        f"Expected OUT_OF_SCOPE pattern match, got {res_movie.matched_patterns}"
    )
    print("PASS: test_follow_up_context_tracking (out-of-scope movie recommendation)")

    # Sequence E2: Other out of scope inquiries
    for oos in ["plan a trip to Paris", "suggest a good restaurant", "who won the cricket match today?"]:
        res_oos = router.classify(oos)
        assert res_oos.intent == QueryIntent.GENERAL_NON_LEGAL, f"Expected GENERAL_NON_LEGAL for '{oos}', got {res_oos.intent}"
        assert "OUT_OF_SCOPE" in res_oos.matched_patterns, f"Expected OUT_OF_SCOPE for '{oos}', got {res_oos.matched_patterns}"
    print("PASS: test_follow_up_context_tracking (all out-of-scope samples)")
"""

if "def test_follow_up_context_tracking" not in code:
    code = code.replace("if __name__ == \"__main__\":", new_tests + "\nif __name__ == \"__main__\":\n    test_follow_up_context_tracking()")
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Added test_follow_up_context_tracking to tests/test_query_router.py")
else:
    print("test_follow_up_context_tracking already present")
