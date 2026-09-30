import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.api.query_router import QueryRouter, QueryIntent
from src.api.server import generate_out_of_scope_response, generate_ambiguous_response

def run_tests():
    router = QueryRouter()
    print("=== TEST 1: CHATBOT / META INQUIRIES ===")
    meta_queries = [
        "what can you do",
        "what can you do for me",
        "why aren't you working as a normal chatbot",
        "why are you not acting like a normal chatbot",
        "can you act like a normal chatbot",
        "who are you",
        "what are you",
        "how do you work",
        "can you talk normally",
        "why do you answer like this"
    ]
    for q in meta_queries:
        res = router.classify(q)
        print(f"Query: \"{q}\" -> Intent: {res.intent.value}, SubIntent: {res.sub_intent}")
        assert res.intent == QueryIntent.CONVERSATIONAL, f"Failed for {q}: got {res.intent}"
    print("PASS: Chatbot / Meta queries all classified as CONVERSATIONAL\n")

    print("=== TEST 2: STRICT OUT-OF-SCOPE NON-LEGAL REDIRECTION ===")
    non_legal_queries = [
        "how to bake a chocolate cake",
        "write a python script to parse json",
        "who won the cricket world cup",
        "tell me a bedtime story about dragons",
        "what is the capital of France",
        "explain quantum entanglement"
    ]
    expected_resp = (
        "I am a Legal AI assistant. I can only assist with legal matters, case analysis, "
        "and legal research. If you have any legal related questions or cases to discuss, we can discuss that."
    )
    for q in non_legal_queries:
        res = router.classify(q)
        print(f"Query: \"{q}\" -> Intent: {res.intent.value}")
        assert res.intent == QueryIntent.OUT_OF_SCOPE, f"Failed for {q}: got {res.intent}"
        resp = generate_out_of_scope_response(q)
        assert resp == expected_resp, f"Response mismatch for {q}:\nGot: {resp}"
    print("PASS: Non-legal queries strictly routed to OUT_OF_SCOPE with exact redirection text\n")

    print("=== TEST 3: AMBIGUOUS SHORT FRAGMENTS ===")
    ambiguous_queries = ["49p", "xyz", "what about that?"]
    for q in ambiguous_queries:
        res = router.classify(q)
        print(f"Query: \"{q}\" -> Intent: {res.intent.value}")
        assert res.intent == QueryIntent.AMBIGUOUS, f"Failed for {q}: got {res.intent}"
    print("PASS: Ambiguous short queries routed to AMBIGUOUS\n")

    print("=== TEST 4: CONTEXTUAL FOLLOW-UPS, REFORMATTING AND MULTI-TURN RECALL ===")
    case_history = [
        {"role": "user", "content": "summarize the port strike dispute in Martinez matter", "query_type": "CASE_QUERY"},
        {"role": "assistant", "content": "In Martinez v Coastal Holdings, the dispute concerns...", "query_type": "CASE_QUERY"}
    ]
    
    follow_up_queries = [
        "tell me clearly about the previous response",
        "can you reformat that as a comparison table with bullet points?",
        "from the first message, what issues were found?",
        "explain that in simpler terms",
        "break it down line by line",
        "what about that?"
    ]
    for q in follow_up_queries:
        res = router.classify(q, conversation_history=case_history)
        print(f"Case Follow-up: \"{q}\" -> Intent: {res.intent.value}, SubIntent: {res.sub_intent}")
        assert res.intent == QueryIntent.CASE_QUERY, f"Failed for {q}: got {res.intent}"
    print("PASS: Contextual follow-ups and reformatting inherited CASE_QUERY\n")

    legal_history = [
        {"role": "user", "content": "what is BNS Section 103?", "query_type": "EXACT_PROVISION_QUERY"},
        {"role": "assistant", "content": "Section 103 of BNS defines murder...", "query_type": "EXACT_PROVISION_QUERY"}
    ]
    legal_follow_ups = [
        "what about that?",
        "explain that clearly",
        "tell me clearly about the previous response",
        "can you put this in simpler terms?"
    ]
    for q in legal_follow_ups:
        res = router.classify(q, conversation_history=legal_history)
        print(f"Legal Follow-up: \"{q}\" -> Intent: {res.intent.value}, SubIntent: {res.sub_intent}")
        assert res.intent == QueryIntent.LEGAL_QUERY, f"Failed for {q}: got {res.intent}"
    print("PASS: Contextual follow-ups inherited LEGAL_QUERY\n")

    print("=== ALL SYSTEM ROUTING AND DOMAIN TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
