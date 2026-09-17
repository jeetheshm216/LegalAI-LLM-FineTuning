"""
tests/test_backend_routing_integration.py

Comprehensive End-to-End Integration Tests for LegalAI Query Routing:
1. Conversational Queries ("hi", "what can you do?", "thanks") -> Qwen conversational mode.
2. In-Corpus Legal Queries (BNS §103, BSA §63) -> Full RAG grounding.
3. Out-of-Corpus Legal Queries (NI Act §138) -> Strict RAG abstention (OUT_OF_CORPUS / Requires verification).
4. Temporal Law Queries (June 15, 2024) -> Temporal guard transition.
5. Case Queries ("Analyze my case") -> Case guidance without hallucinating facts.
6. Adversarial Mixed Queries ("Hi, what is Section 103 BNS?") -> Strictly routed to LEGAL_QUERY.
7. SSE Streaming endpoint verification for both CONVERSATIONAL and LEGAL_QUERY routes.
"""

import sys
import json
import requests
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8008"


def test_health():
    print("--- 1. Health Endpoint ---")
    resp = requests.get(f"{BASE_URL}/api/v1/health", timeout=15)
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    data = resp.json()
    print(f"Health status: {data.get('status')}")
    print(f"Model: {data.get('model', {}).get('base_model')}")
    print(f"GPU device: {data.get('gpu', {}).get('device')}")
    assert data.get("status") == "healthy"
    print("PASS: Health check\n")


def test_conversational_chat():
    print("--- 2. Conversational Chat (Non-streaming) ---")
    conv_queries = [
        "hi",
        "what can you do?",
        "thanks"
    ]
    for q in conv_queries:
        payload = {"content": q}
        resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=45)
        assert resp.status_code == 200, f"Chat failed for '{q}': {resp.status_code} {resp.text}"
        data = resp.json()
        print(f"Query: '{q}'")
        print(f"  Route Query Type: {data.get('query_type')}")
        print(f"  Reliability: {data.get('reliability')} ({data.get('reliabilityLabel')})")
        print(f"  Sources Count: {len(data.get('sources', []))}")
        print(f"  Answer Preview: {data.get('content', '')[:120]}...")
        assert data.get("query_type") == "CONVERSATIONAL"
        assert len(data.get("sources", [])) == 0
        assert len(data.get("citations", [])) == 0
        assert data.get("requires_verification") is False
        assert len(data.get("content", "").strip()) > 10
    print("PASS: Conversational Chat\n")


def test_in_corpus_legal_chat():
    print("--- 3. In-Corpus Legal Queries (BNS §103, BSA §63) ---")
    legal_queries = [
        ("What is BNS Section 103?", "103"),
        ("What does BSA Section 63 say?", "63"),
    ]
    for q, expected_sec in legal_queries:
        payload = {"content": q}
        resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=120)
        assert resp.status_code == 200, f"Chat failed for '{q}': {resp.status_code} {resp.text}"
        data = resp.json()
        print(f"Query: '{q}'")
        print(f"  Route Query Type: {data.get('query_type')}")
        print(f"  Reliability: {data.get('reliability')} ({data.get('reliabilityLabel')})")
        print(f"  Sources Count: {len(data.get('sources', []))}")
        print(f"  Answer Preview: {data.get('content', '')[:140]}...")
        assert data.get("query_type") == "LEGAL_QUERY"
        assert len(data.get("sources", [])) > 0
        assert data.get("reliability") == "supported"
    print("PASS: In-Corpus Legal Queries\n")


def test_out_of_corpus_legal_chat():
    print("--- 4. Out-of-Corpus Legal Query (NI Act §138) ---")
    q = "What is Section 4 of the Marine Insurance Act, 1963?"
    payload = {"content": q}
    resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=60)
    assert resp.status_code == 200, f"Chat failed for '{q}': {resp.status_code} {resp.text}"
    data = resp.json()
    print(f"Query: '{q}'")
    print(f"  Route Query Type: {data.get('query_type')}")
    print(f"  Evidence Status: {data.get('evidence_status')}")
    print(f"  Confidence Status: {data.get('confidence_status')}")
    print(f"  Reliability: {data.get('reliability')} ({data.get('reliabilityLabel')})")
    print(f"  Requires Verification: {data.get('requires_verification')}")
    print(f"  Answer Preview: {data.get('content', '')[:140]}...")
    assert data.get("query_type") == "LEGAL_QUERY"
    assert data.get("evidence_status") == "OUT_OF_CORPUS"
    assert data.get("requires_verification") is True
    assert data.get("reliability") == "verify"
    print("PASS: Out-of-Corpus Abstention Preserved\n")


def test_temporal_legal_chat():
    print("--- 5. Temporal Legal Query (June 15, 2024 Conduct) ---")
    q = "What law applies to a substantive offence committed on June 15, 2024?"
    payload = {"content": q}
    resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=60)
    assert resp.status_code == 200, f"Chat failed for '{q}': {resp.status_code} {resp.text}"
    data = resp.json()
    print(f"Query: '{q}'")
    print(f"  Route Query Type: {data.get('query_type')}")
    print(f"  Confidence Status: {data.get('confidence_status')}")
    print(f"  Reliability: {data.get('reliability')} ({data.get('reliabilityLabel')})")
    print(f"  Answer Preview: {data.get('content', '')[:140]}...")
    assert data.get("query_type") == "LEGAL_QUERY"
    assert data.get("confidence_status") == "TEMPORAL_TRANSITION_APPLIED"
    print("PASS: Temporal Transition Preserved\n")


def test_case_query():
    print("--- 6. Case Query ('Analyze my case') ---")
    q = "Analyze my case."
    payload = {"content": q, "caseId": "case-01"}
    resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=60)
    assert resp.status_code == 200, f"Chat failed for '{q}': {resp.status_code} {resp.text}"
    data = resp.json()
    print(f"Query: '{q}'")
    print(f"  Route Query Type: {data.get('query_type')}")
    print(f"  Reliability: {data.get('reliability')} ({data.get('reliabilityLabel')})")
    print(f"  Content: {data.get('content')[:140]}...")
    assert data.get("query_type") == "CASE_QUERY"
    assert "Martinez v. Coastal Holdings" in data.get("content", "")
    print("PASS: Case Query\n")


def test_adversarial_mixed_chat():
    print("--- 7. Adversarial Mixed Query ('Hi, what is Section 103 BNS?') ---")
    q = "Hi, what is Section 103 BNS?"
    payload = {"content": q}
    resp = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=60)
    assert resp.status_code == 200, f"Chat failed for '{q}': {resp.status_code} {resp.text}"
    data = resp.json()
    print(f"Query: '{q}'")
    print(f"  Route Query Type: {data.get('query_type')}")
    print(f"  Sources Count: {len(data.get('sources', []))}")
    assert data.get("query_type") == "LEGAL_QUERY"
    assert len(data.get("sources", [])) > 0
    print("PASS: Adversarial Mixed Query Strictly Routed to LEGAL_QUERY\n")


def test_streaming():
    print("--- 8. SSE Streaming Endpoint ---")
    # Stream Conversational
    payload_conv = {"content": "hello"}
    resp_conv = requests.post(f"{BASE_URL}/api/v1/ai/chat/stream", json=payload_conv, stream=True, timeout=45)
    assert resp_conv.status_code == 200
    complete_conv = None
    current_event = None
    for line in resp_conv.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("event:"):
                current_event = decoded.replace("event:", "").strip()
            elif decoded.startswith("data:") and current_event == "complete":
                json_str = decoded.replace("data:", "").strip()
                try:
                    complete_conv = json.loads(json_str)
                except Exception as e:
                    print("JSON parse error:", e)
    print("SSE Conversational Complete Event:")
    print(f"  Query Type: {complete_conv.get('query_type') if complete_conv else 'N/A'}")
    print(f"  Content: {complete_conv.get('content')[:100] if complete_conv else 'N/A'}...")
    assert complete_conv is not None
    assert complete_conv.get("query_type") == "CONVERSATIONAL"
    assert len(complete_conv.get("sources", [])) == 0

    # Stream Legal
    payload_legal = {"content": "What is BNS Section 103?"}
    resp_legal = requests.post(f"{BASE_URL}/api/v1/ai/chat/stream", json=payload_legal, stream=True, timeout=90)
    assert resp_legal.status_code == 200
    complete_legal = None
    current_event = None
    for line in resp_legal.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("event:"):
                current_event = decoded.replace("event:", "").strip()
            elif decoded.startswith("data:") and current_event == "complete":
                json_str = decoded.replace("data:", "").strip()
                try:
                    complete_legal = json.loads(json_str)
                except Exception as e:
                    print("JSON parse error:", e)
    print("SSE Legal Complete Event:")
    print(f"  Query Type: {complete_legal.get('query_type') if complete_legal else 'N/A'}")
    print(f"  Sources: {len(complete_legal.get('sources', [])) if complete_legal else 'N/A'}")
    assert complete_legal is not None
    assert complete_legal.get("query_type") == "LEGAL_QUERY"
    assert len(complete_legal.get("sources", [])) > 0
    print("PASS: Streaming for both Conversational and Legal routes\n")


if __name__ == "__main__":
    test_health()
    test_conversational_chat()
    test_in_corpus_legal_chat()
    test_out_of_corpus_legal_chat()
    test_temporal_legal_chat()
    test_case_query()
    test_adversarial_mixed_chat()
    test_streaming()
    print("=" * 60)
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
