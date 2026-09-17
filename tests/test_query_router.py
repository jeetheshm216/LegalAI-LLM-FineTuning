"""
tests/test_query_router.py

Unit tests for LegalAI QueryRouter.
Validates:
1. Conversational classification for pure greetings, gratitude, and assistant capability queries.
2. Legal query classification for in-corpus (BNS, BNSS, BSA) and out-of-corpus statutes (NI Act, RERA, Constitution) + legal practice.
3. Case query classification for matter-specific, client, evidence, and document inquiries.
4. Out-of-scope non-legal classification for programming, movies, sports, tech shopping, recipes, etc.
5. Contextual follow-up tracking (Conversations 1, 2, 3, 4).
6. Exact Section 20 Routing Test Matrix.
"""

import sys
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.api.query_router import QueryRouter, QueryIntent


def test_section_20_matrix():
    router = QueryRouter()

    # 1. CONVERSATIONAL
    conversational = [
        "hi",
        "hey",
        "hello",
        "hey hi",
        "good morning",
        "how are you",
        "thanks",
        "thank you"
    ]
    for q in conversational:
        res = router.classify(q)
        assert res.intent == QueryIntent.CONVERSATIONAL, f"Expected CONVERSATIONAL for '{q}', got {res.intent}"

    # 2. LEGAL
    legal = [
        "what is BNS section 103",
        "what is BNSS section 482",
        "what is BSA section 63",
        "explain BNS section 103"
    ]
    for q in legal:
        res = router.classify(q)
        assert res.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY for '{q}', got {res.intent}"

    # 3. CASE
    case_queries = [
        "what happened in my case",
        "summarize this case",
        "what evidence is missing in my case"
    ]
    for q in case_queries:
        res = router.classify(q)
        assert res.intent == QueryIntent.CASE_QUERY, f"Expected CASE_QUERY for '{q}', got {res.intent}"

    # 4. OUT OF SCOPE
    out_of_scope = [
        "what is Python",
        "write a python code",
        "write C++ code",
        "for odd or even",
        "what is the last Vijay movie",
        "who won yesterday's cricket match",
        "recommend me a movie",
        "what laptop should I buy",
        "how do I cook biryani"
    ]
    for q in out_of_scope:
        res = router.classify(q)
        assert res.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for '{q}', got {res.intent}"

    print("PASS: test_section_20_matrix")


def test_section_20_context_conversations():
    router = QueryRouter()

    # Conversation 1: Programming follow-ups
    # User: "write a python code" -> OUT_OF_SCOPE
    res1 = router.classify("write a python code")
    assert res1.intent == QueryIntent.OUT_OF_SCOPE
    history1 = [
        {"role": "user", "content": "write a python code", "query_type": "OUT_OF_SCOPE"},
        {"role": "assistant", "content": "Programming isn't my area, buddy...", "query_type": "OUT_OF_SCOPE"}
    ]
    # User: "for odd or even" -> OUT_OF_SCOPE
    res2 = router.classify("for odd or even", conversation_history=history1)
    assert res2.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for 'for odd or even', got {res2.intent}"
    history1.extend([
        {"role": "user", "content": "for odd or even", "query_type": "OUT_OF_SCOPE"},
        {"role": "assistant", "content": "That's still a programming request...", "query_type": "OUT_OF_SCOPE"}
    ])
    # User: "can you make it shorter?" -> OUT_OF_SCOPE
    res3 = router.classify("can you make it shorter?", conversation_history=history1)
    assert res3.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for 'can you make it shorter?', got {res3.intent}"

    # Conversation 2: Legal follow-up
    # User: "what is BNS section 103?" -> LEGAL_QUERY
    res4 = router.classify("what is BNS section 103?")
    assert res4.intent == QueryIntent.LEGAL_QUERY
    history2 = [
        {"role": "user", "content": "what is BNS section 103?", "query_type": "LEGAL_QUERY"},
        {"role": "assistant", "content": "Section 103 of BNS...", "query_type": "LEGAL_QUERY"}
    ]
    # User: "what punishment applies?" -> LEGAL_QUERY
    res5 = router.classify("what punishment applies?", conversation_history=history2)
    assert res5.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY for 'what punishment applies?', got {res5.intent}"

    # Conversation 3: Out-of-scope then Legal override
    # User: "what is the last Vijay movie?" -> OUT_OF_SCOPE
    res6 = router.classify("what is the last Vijay movie?")
    assert res6.intent == QueryIntent.OUT_OF_SCOPE
    history3 = [
        {"role": "user", "content": "what is the last Vijay movie?", "query_type": "OUT_OF_SCOPE"},
        {"role": "assistant", "content": "That's outside my legal scope...", "query_type": "OUT_OF_SCOPE"}
    ]
    # User: "what about the previous one?" -> OUT_OF_SCOPE
    res_prev = router.classify("what about the previous one?", conversation_history=history3)
    assert res_prev.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for follow-up, got {res_prev.intent}"
    # User: "what is BNS section 103?" -> LEGAL_QUERY (override!)
    res7 = router.classify("what is BNS section 103?", conversation_history=history3)
    assert res7.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY override, got {res7.intent}"

    # Conversation 4: Case follow-up
    # User: "what happened in my case?" -> CASE_QUERY
    res8 = router.classify("what happened in my case?")
    assert res8.intent == QueryIntent.CASE_QUERY
    history4 = [
        {"role": "user", "content": "what happened in my case?", "query_type": "CASE_QUERY"},
        {"role": "assistant", "content": "In your case...", "query_type": "CASE_QUERY"}
    ]
    # User: "what evidence is missing?" -> CASE_QUERY
    res9 = router.classify("what evidence is missing?", conversation_history=history4)
    assert res9.intent == QueryIntent.CASE_QUERY, f"Expected CASE_QUERY for 'what evidence is missing?', got {res9.intent}"

    print("PASS: test_section_20_context_conversations")


def test_mixed_greeting_queries():
    router = QueryRouter()
    # Greeting + Legal -> LEGAL_QUERY
    res1 = router.classify("Hey, what is BNS Section 103?")
    assert res1.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY for greeting + legal, got {res1.intent}"

    # Greeting + Out of Scope -> OUT_OF_SCOPE
    res2 = router.classify("Hey, what is the latest Vijay movie?")
    assert res2.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for greeting + movie, got {res2.intent}"

    # Greeting + C++ Code -> OUT_OF_SCOPE
    res3 = router.classify("Hi, write C++ code for creating python file")
    assert res3.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for greeting + code, got {res3.intent}"

    print("PASS: test_mixed_greeting_queries")


def test_legal_related_general_questions():
    router = QueryRouter()
    questions = [
        "What is a bail application?",
        "How should I prepare for cross-examination?",
        "How should a legal notice be structured?",
        "What is the difference between civil and criminal proceedings?"
    ]
    for q in questions:
        res = router.classify(q)
        assert res.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY for '{q}', got {res.intent}"

    print("PASS: test_legal_related_general_questions")


def test_adversarial_mixed_queries():
    router = QueryRouter()
    mixed_cases = [
        ("Hi, what is Section 103 BNS?", QueryIntent.LEGAL_QUERY),
        ("Thanks. Explain Section 138 NI Act.", QueryIntent.LEGAL_QUERY),
        ("Hello, analyze my client's FIR.", QueryIntent.CASE_QUERY),
        ("What can you do with this judgment?", QueryIntent.CASE_QUERY),
        ("Good morning. Can you explain anticipatory bail?", QueryIntent.LEGAL_QUERY),
        ("Hi! What is the punishment for murder under BNS?", QueryIntent.LEGAL_QUERY),
        ("Thank you. Is this offence cognizable?", QueryIntent.LEGAL_QUERY),
        ("Hello, what documents are missing in this case?", QueryIntent.CASE_QUERY),
    ]

    for q, expected in mixed_cases:
        result = router.classify(q)
        assert result.intent == expected, (
            f"Expected {expected} for '{q}', got {result.intent} (matched: {result.matched_patterns})"
        )
    print(f"PASS: test_adversarial_mixed_queries (all {len(mixed_cases)} passed)")


def test_social_profanity_messages():
    router = QueryRouter()
    # Interpersonal/frustration/profanity messages must be CONVERSATIONAL, NEVER OUT_OF_SCOPE!
    messages = [
        "fuck you",
        "you're useless",
        "this is stupid",
        "damn",
        "what the hell",
        "you suck"
    ]
    for q in messages:
        res = router.classify(q)
        assert res.intent == QueryIntent.CONVERSATIONAL, (
            f"Expected CONVERSATIONAL for social/profanity '{q}', got {res.intent}"
        )
    print("PASS: test_social_profanity_messages (all classified as CONVERSATIONAL)")


def test_ambiguous_queries():
    router = QueryRouter()
    # Ambiguous queries without context
    ambiguous_cases = [
        "49p",
        "xyz",
        "what about that?"
    ]
    for q in ambiguous_cases:
        res = router.classify(q)
        assert res.intent == QueryIntent.AMBIGUOUS, (
            f"Expected AMBIGUOUS for '{q}', got {res.intent}"
        )

    # But with legal context, "what about that?" inherits legal intent!
    history = [
        {"role": "user", "content": "what is BNS section 103?", "query_type": "LEGAL_QUERY"},
        {"role": "assistant", "content": "Section 103 of BNS...", "query_type": "LEGAL_QUERY"}
    ]
    res_context = router.classify("what about that?", conversation_history=history)
    assert res_context.intent == QueryIntent.LEGAL_QUERY, (
        f"Expected LEGAL_QUERY for 'what about that?' with legal context, got {res_context.intent}"
    )

    print("PASS: test_ambiguous_queries (both isolated and contextual)")


def test_section_14_suite():
    router = QueryRouter()

    # Out of scope specific checks from prompt
    oos_queries = [
        "what is Python?",
        "write C++ hello world",
        "give me odd/even Python code",
        "latest Vijay movie",
        "cricket result",
        "laptop recommendation"
    ]
    for q in oos_queries:
        res = router.classify(q)
        assert res.intent == QueryIntent.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for '{q}', got {res.intent}"

    # Legal queries from prompt
    legal_queries = [
        "what is BNS Section 103?",
        "what is BNSS Section 482?",
        "what is BSA Section 63?",
        "what punishment applies?"
    ]
    for q in legal_queries:
        res = router.classify(q)
        assert res.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY for '{q}', got {res.intent}"

    # Legal follow-up
    hist = [
        {"role": "user", "content": "what is BNS Section 103?", "query_type": "LEGAL_QUERY"},
        {"role": "assistant", "content": "Section 103...", "query_type": "LEGAL_QUERY"}
    ]
    res_evid = router.classify("what evidence is required?", conversation_history=hist)
    assert res_evid.intent == QueryIntent.LEGAL_QUERY, f"Expected LEGAL_QUERY for legal follow-up, got {res_evid.intent}"

    print("PASS: test_section_14_suite")


if __name__ == "__main__":
    test_section_20_matrix()
    test_section_20_context_conversations()
    test_mixed_greeting_queries()
    test_legal_related_general_questions()
    test_adversarial_mixed_queries()
    test_social_profanity_messages()
    test_ambiguous_queries()
    test_section_14_suite()
    print("\nALL QUERY ROUTER UNIT TESTS PASSED SUCCESSFULLY!")

