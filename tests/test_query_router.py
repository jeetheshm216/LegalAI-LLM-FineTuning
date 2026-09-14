"""
tests/test_query_router.py

Unit tests for LegalAI QueryRouter.
Validates:
1. Conversational classification for pure greetings, gratitude, and assistant capability queries.
2. Legal query classification for in-corpus (BNS, BNSS, BSA) and out-of-corpus statutes (NI Act, RERA, Constitution).
3. Case query classification for matter-specific, client, evidence, and document inquiries.
4. Adversarial / mixed queries ensuring legal and case intent NEVER get classified as conversational.
5. Conversation history contextual follow-up handling.
"""

import sys
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.api.query_router import QueryRouter, QueryIntent


def test_conversational_queries():
    router = QueryRouter()
    conversational_inputs = [
        "Hello",
        "Hi",
        "hey",
        "Good morning",
        "good evening",
        "Thanks",
        "Thank you",
        "thank you so much",
        "Who are you?",
        "What can you do?",
        "Are you an AI?",
        "Tell me about yourself",
        "tell me about LegalAI",
        "How are you?",
        "help",
        "Tell me a joke about lawyers.",
    ]

    for q in conversational_inputs:
        result = router.classify(q)
        assert result.intent == QueryIntent.CONVERSATIONAL, (
            f"Expected CONVERSATIONAL for '{q}', got {result.intent} (reason: {result.reason})"
        )
    print("PASS: test_conversational_queries (all 16 passed)")


def test_legal_queries():
    router = QueryRouter()
    legal_inputs = [
        # In-corpus
        ("What is BNS Section 103?", QueryIntent.LEGAL_QUERY),
        ("What does BSA Section 63 say?", QueryIntent.LEGAL_QUERY),
        ("What is the punishment for theft?", QueryIntent.LEGAL_QUERY),
        ("Can an accused get anticipatory bail?", QueryIntent.LEGAL_QUERY),
        ("What is the procedure for filing an appeal?", QueryIntent.LEGAL_QUERY),
        ("What law applies to a substantive offence committed on June 15, 2024?", QueryIntent.LEGAL_QUERY),
        ("What is the limitation period?", QueryIntent.LEGAL_QUERY),
        ("Is murder a bailable offence?", QueryIntent.LEGAL_QUERY),
        # Out-of-corpus (CRITICAL SAFETY)
        ("What is Section 138 of the Negotiable Instruments Act?", QueryIntent.LEGAL_QUERY),
        ("What is Section 138 of the NI Act?", QueryIntent.LEGAL_QUERY),
        ("What is RERA?", QueryIntent.LEGAL_QUERY),
        ("Explain RERA Section 11.", QueryIntent.LEGAL_QUERY),
        ("What is Article 21 of the Constitution?", QueryIntent.LEGAL_QUERY),
        ("What is Article 21?", QueryIntent.LEGAL_QUERY),
        ("What is the limitation period under the Limitation Act?", QueryIntent.LEGAL_QUERY),
        ("Explain intermediary liability under Section 79 of the IT Act.", QueryIntent.LEGAL_QUERY),
        ("What are the grounds for divorce under Hindu Marriage Act?", QueryIntent.LEGAL_QUERY),
        ("Can a company issue bonus shares under Companies Act?", QueryIntent.LEGAL_QUERY),
    ]

    for q, expected in legal_inputs:
        result = router.classify(q)
        assert result.intent == expected, (
            f"Expected {expected} for '{q}', got {result.intent} (reason: {result.reason})"
        )
    print(f"PASS: test_legal_queries (all {len(legal_inputs)} passed)")


def test_case_queries():
    router = QueryRouter()
    case_inputs = [
        "Analyze my case.",
        "What are the strongest points in my client's case?",
        "What are the weaknesses in this case?",
        "What evidence supports our argument?",
        "Summarize this judgment.",
        "What are the risks of pursuing this argument?",
        "What documents are missing?",
        "What happened at the last hearing?",
        "What happened in my case?",
        "Are there inconsistencies in the witness statements?",
        "What arguments can the opposing counsel make?",
        "What should we challenge in this petition?",
        "Analyze this FIR.",
        "Review the attached document.",
    ]

    for q in case_inputs:
        result = router.classify(q)
        assert result.intent == QueryIntent.CASE_QUERY, (
            f"Expected CASE_QUERY for '{q}', got {result.intent} (reason: {result.reason})"
        )
    print(f"PASS: test_case_queries (all {len(case_inputs)} passed)")


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


def test_contextual_follow_up():
    router = QueryRouter()
    # History with legal query
    history = [
        {"role": "user", "content": "What is Section 103 BNS?"},
        {"role": "assistant", "content": "Section 103 of Bharatiya Nyaya Sanhita defines punishment for murder..."}
    ]
    follow_up = "What about the punishment?"
    result = router.classify(follow_up, conversation_history=history)
    assert result.intent == QueryIntent.LEGAL_QUERY, (
        f"Expected LEGAL_QUERY for follow-up '{follow_up}', got {result.intent}"
    )
    print("PASS: test_contextual_follow_up")


if __name__ == "__main__":
    test_conversational_queries()
    test_legal_queries()
    test_case_queries()
    test_adversarial_mixed_queries()
    test_contextual_follow_up()
    print("\nALL ROUTER TESTS PASSED SUCCESSFULLY!")
