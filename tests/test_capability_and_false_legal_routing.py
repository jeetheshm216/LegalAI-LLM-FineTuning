"""
tests/test_capability_and_false_legal_routing.py

Regression test suite ensuring:
1. Natural conversational capability inquiries route to CONVERSATIONAL with zero legal retrieval.
2. The critical negative test query 'what are the things you can able to do fro me' NEVER routes to Legal RAG.
3. Explicit legal anchors are required for LEGAL_QUERY.
4. Ambiguous demonstratives ('Tell me about this', 'What about this section?') route to AMBIGUOUS.
5. Mixed queries correctly prioritize legal/case anchors over conversational framing.
"""

import pytest
from src.api.query_router import QueryRouter, QueryIntent
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline


@pytest.fixture(scope="module")
def router():
    return QueryRouter()


class TestCapabilityRouting:
    """Verifies that conversational capability inquiries route strictly to CONVERSATIONAL."""

    CAPABILITY_QUERIES = [
        "hi",
        "hello",
        "hello, how are you doing?",
        "how are you",
        "what are you doing",
        "what can you do",
        "what can you do for me",
        "what are the things you can able to do for me",
        "what are the things you can able to do fro me",  # Critical negative test
        "what can you help me with",
        "how can you help me",
        "what can I ask you",
        "what kinds of questions can I ask",
        "what services do you provide",
        "what are your capabilities",
        "tell me what you can do",
        "what can I use you for",
        "what do you help with",
        "how can I use LegalAI",
        "what can LegalAI do",
        "What can you help me with regarding LegalAI?",
        "thank you",
        "thanks",
    ]

    @pytest.mark.parametrize("query", CAPABILITY_QUERIES)
    def test_capability_queries_route_to_conversational(self, router, query):
        res = router.classify(query)
        assert res.intent == QueryIntent.CONVERSATIONAL, f"Failed for query: {query}, got {res.intent}"


class TestCriticalNegativeTest:
    """Verifies that the observed bug query NEVER routes to LEGAL_QUERY or retrieves legal chunks."""

    def test_observed_bug_query_router(self, router):
        query = "what are the things you can able to do fro me"
        res = router.classify(query)
        assert res.intent == QueryIntent.CONVERSATIONAL
        assert res.sub_intent == "CAPABILITY_INQUIRY"
        assert res.legal_intent_confidence == 0.0

    def test_pipeline_secondary_relevance_gate(self):
        """Even if an ungrounded query reached pipeline.query(), the secondary gate must reject unrelated chunks."""
        pipeline = GeneralIndianLegalKnowledgePipeline()
        query = "what are the things you can able to do fro me"
        res = pipeline.query(query)
        # Must not return arbitrary CPC, BSA, or Companies Act chunks
        sources = res.get("sources", [])
        chunk_ids = [s.get("chunk_id", "") for s in sources]
        assert "CPC_ORDER_6_RULE_56" not in str(chunk_ids)
        assert "BSA_SECTION_99" not in str(chunk_ids)
        assert len(sources) == 0, f"Expected 0 sources, got: {chunk_ids}"
        assert res.get("qwen_invoked") is False


class TestLegalIntentAnchorRequirement:
    """Verifies that LEGAL_QUERY requires a valid legal anchor."""

    LEGAL_QUERIES = [
        "What is the Companies Act?",
        "What is the Information Technology Act?",
        "Section 66C of the IT Act",
        "What is Section 138 of the Negotiable Instruments Act?",
        "What is anticipatory bail?",
        "What law applies to phishing?",
        "Someone stole my UPI credentials. What Indian legal provisions may apply?",
        "Section 49A",
        "act 49A",
        "Section 9999 of the IT Act",
        "What is the Tamil Nadu Payment of Salaries Act?",
        "What is the Act number of the Tamil Nadu Payment of Salaries Act?",
    ]

    @pytest.mark.parametrize("query", LEGAL_QUERIES)
    def test_legal_queries_route_to_legal(self, router, query):
        res = router.classify(query)
        assert res.intent == QueryIntent.LEGAL_QUERY, f"Failed for query: {query}, got {res.intent}"


class TestAmbiguousQueries:
    """Verifies that inquiries lacking legal anchors and context route to AMBIGUOUS."""

    AMBIGUOUS_QUERIES = [
        "Tell me about this",
        "What about this?",
        "What about this section?",
        "Explain this",
        "49p",
        "xyz",
    ]

    @pytest.mark.parametrize("query", AMBIGUOUS_QUERIES)
    def test_ambiguous_queries_route_to_ambiguous(self, router, query):
        res = router.classify(query)
        assert res.intent == QueryIntent.AMBIGUOUS, f"Failed for query: {query}, got {res.intent}"


class TestMixedQueries:
    """Verifies that explicit legal or case anchors override conversational framing."""

    def test_mixed_legal_overrides_greeting(self, router):
        res1 = router.classify("Hi, can you explain Section 66C?")
        assert res1.intent == QueryIntent.LEGAL_QUERY

        res2 = router.classify("Hello, what is anticipatory bail?")
        assert res2.intent == QueryIntent.LEGAL_QUERY

    def test_mixed_capability_remains_conversational(self, router):
        res = router.classify("Hi, what can you do for me?")
        assert res.intent == QueryIntent.CONVERSATIONAL

    def test_case_queries_route_to_case(self, router):
        res1 = router.classify("What are the key points in this case?")
        assert res1.intent == QueryIntent.CASE_QUERY

        res2 = router.classify("What evidence is missing?")
        assert res2.intent == QueryIntent.CASE_QUERY

        res3 = router.classify("What should I prepare for the next hearing?")
        assert res3.intent == QueryIntent.CASE_QUERY
