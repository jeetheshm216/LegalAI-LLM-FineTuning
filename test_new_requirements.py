import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.query_router import UniversalQueryRouter, QueryIntent
from src.api.query_understanding.goals import SubIntent, OutputPlan

router = UniversalQueryRouter()

print("--- 35. CONVERSATIONAL REGRESSION ---")
conv_queries = [
    "what is your name",
    "what i syour name",
    "wat is your name",
    "wht is ur name",
    "who are you",
    "tell me your name",
    "what can you do",
    "hello",
    "hi",
    "thanks",
    "thank you"
]
for q in conv_queries:
    # Test both without case and WITH Martinez active!
    dec = router.classify(q, case_id="case-01")
    assert dec.intent == QueryIntent.CONVERSATIONAL, f"Failed for '{q}': got {dec.intent}"
    print(f"  [OK] '{q}' -> intent={dec.intent.value}, sub={dec.sub_intent}")

print("\n--- 36. CASE MANAGEMENT REGRESSION ---")
cm_queries = [
    "what is the priority of this case",
    "how important is this case",
    "what matters most in this case",
    "what is the important thing i have to consider in this case",
    "what needs my attention in this case",
    "what should i deal with first"
]
for q in cm_queries:
    dec = router.classify(q, case_id="case-01")
    assert dec.intent == QueryIntent.CASE_MANAGEMENT, f"Failed for '{q}': got {dec.intent}"
    assert dec.sub_intent == SubIntent.CASE_PRIORITY.value, f"Failed sub for '{q}': got {dec.sub_intent}"
    print(f"  [OK] '{q}' -> intent={dec.intent.value}, sub={dec.sub_intent}")

print("\n--- 37. TYPO UNDERSTANDING SEMANTIC CONVERGENCE ---")
typo_tests = [
    ("what i syour name", QueryIntent.CONVERSATIONAL, SubIntent.ASSISTANT_IDENTITY.value),
    ("what is the kay points in this case", QueryIntent.CASE_QUERY, SubIntent.CASE_KEY_POINTS.value),
    ("waht is the matter", QueryIntent.CASE_QUERY, SubIntent.CASE_SUMMARY.value),
    ("wht is the matter", QueryIntent.CASE_QUERY, SubIntent.CASE_SUMMARY.value),
    ("what evidnce do we have", QueryIntent.CASE_QUERY, SubIntent.CASE_EVIDENCE.value),
    ("what r the key pionts", QueryIntent.CASE_QUERY, SubIntent.CASE_KEY_POINTS.value),
]
for q, exp_intent, exp_sub in typo_tests:
    dec = router.classify(q, case_id="case-01")
    assert dec.intent == exp_intent, f"Failed intent for '{q}': exp {exp_intent}, got {dec.intent}"
    assert dec.sub_intent == exp_sub, f"Failed sub for '{q}': exp {exp_sub}, got {dec.sub_intent}"
    print(f"  [OK] '{q}' (norm: '{dec.normalized_query}') -> intent={dec.intent.value}, sub={dec.sub_intent}")

print("\n--- 38. CROSS CONTEXT INDEPENDENCE (Martinez Active) ---")
cross_tests = [
    ("what is your name", QueryIntent.CONVERSATIONAL),
    ("what is qwen", QueryIntent.TECHNICAL_AI),
    ("what is rag", QueryIntent.TECHNICAL_AI),
    ("what is section 66c", QueryIntent.EXACT_PROVISION_QUERY),
    ("what is the matter", QueryIntent.CASE_QUERY),
    ("what are the key points", QueryIntent.CASE_QUERY),
    ("what is the priority of this case", QueryIntent.CASE_MANAGEMENT),
]
for q, exp_intent in cross_tests:
    dec = router.classify(q, case_id="case-01")
    assert dec.intent == exp_intent, f"Cross test failed for '{q}': exp {exp_intent}, got {dec.intent}"
    print(f"  [OK] '{q}' -> {dec.intent.value}")

print("\n--- 47. VERIFY THE FOUR SPECIFIC TESTS ---")
# Test 1: what i syour name
d1 = router.classify("what i syour name", case_id="case-01")
assert d1.intent == QueryIntent.CONVERSATIONAL and d1.sub_intent == SubIntent.ASSISTANT_IDENTITY.value
print("  Test 1: 'what i syour name' -> CONVERSATIONAL / ASSISTANT_IDENTITY [PASS]")

# Test 2: what is the priority of this case
d2 = router.classify("what is the priority of this case", case_id="case-01")
assert d2.intent == QueryIntent.CASE_MANAGEMENT and d2.sub_intent == SubIntent.CASE_PRIORITY.value
print("  Test 2: 'what is the priority of this case' -> CASE_MANAGEMENT / CASE_PRIORITY [PASS]")

# Test 3: what is the kay points in this case
d3 = router.classify("what is the kay points in this case", case_id="case-01")
assert d3.intent == QueryIntent.CASE_QUERY and d3.sub_intent == SubIntent.CASE_KEY_POINTS.value
print("  Test 3: 'what is the kay points in this case' -> CASE_QUERY / CASE_KEY_POINTS [PASS]")

# Test 4: what is qwen
d4 = router.classify("what is qwen", case_id="case-01")
assert d4.intent == QueryIntent.TECHNICAL_AI
print("  Test 4: 'what is qwen' -> TECHNICAL_AI [PASS]")

print("\nALL NEW REQUIREMENT REGRESSION TESTS PASSED 100%!")
