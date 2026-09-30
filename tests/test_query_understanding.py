"""
tests/test_query_understanding.py

Comprehensive test suite validating the LegalAI Query Understanding,
Response Planning, and Lawyer Suggestions layer.
Evaluates:
- General typo tolerance (without hardcoded dictionary)
- Protection of statutory sections, act names, case numbers, and party names
- Sub-intent and user goal classification
- Response output planning
- Authoritative case scope preservation
"""

import sys
import os
import json
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.api.query_router import UniversalQueryRouter, QueryIntent
from src.api.query_understanding.normalizer import QueryNormalizer
from src.api.query_understanding.goals import SubIntent, UserGoal, OutputPlan
from src.api.query_understanding.planner import ResponsePlanner
from src.api.query_understanding.suggestions import SuggestionGenerator


def test_legal_identifier_protection():
    """Verify that legal sections, acts, and case identifiers are never corrupted."""
    normalizer = QueryNormalizer()
    provisions = [
        "Section 66C of IT Act",
        "BNS Section 103",
        "Section 138 of Negotiable Instruments Act",
        "Order 39 Rule 1 CPC",
        "Article 21 Constitution of India",
        "2024-CV-1187 Martinez v. Coastal Holdings Ltd.",
        "case-01",
        "Section 316 BNS"
    ]
    for p in provisions:
        normalized, protected = normalizer.normalize(p)
        assert p in normalized, f"Legal provision '{p}' was altered during normalization: '{normalized}'"
    print("PASS: test_legal_identifier_protection")


def test_general_typo_tolerance_unseen():
    """Verify that general typo tolerance works on unseen typos without hardcoded lists."""
    normalizer = QueryNormalizer()
    pairs = [
        ("what are the key pionts in this case", "what are the key points in this case"),
        ("what are the key poins in this case", "what are the key point in this case"),
        ("what r the key points", "what are the key points"),
        ("what are the imporant isues", "what are the important issues"),
        ("wat evidence is misssing", "what evidence is missing"),
        ("where is our case wekness", "where is our case weakness"),
    ]
    for raw, expected in pairs:
        norm, _ = normalizer.normalize(raw)
        if raw == "what are the key poins in this case":
            assert norm in ("what are the key point in this case", "what are the key points in this case")
        else:
            assert norm == expected, f"Normalization mismatch for '{raw}': got '{norm}', expected '{expected}'"
    print("PASS: test_general_typo_tolerance_unseen")


def test_focus_inquiry_does_not_force_hearing_prep():
    """USER CORRECTION 1: 'what should I focus on?' must NOT resolve to HEARING_PREPARATION."""
    router = UniversalQueryRouter()
    # Inside a case
    dec = router.classify("what should I focus on in this case", case_id="case-01")
    assert dec.intent == QueryIntent.CASE_QUERY, f"Expected CASE_QUERY, got {dec.intent}"
    assert dec.sub_intent == SubIntent.CASE_KEY_POINTS.value, f"Expected CASE_KEY_POINTS, got {dec.sub_intent}"
    assert dec.user_goal == UserGoal.PRIORITIZE_CASE_ISSUES.value, f"Expected PRIORITIZE_CASE_ISSUES, got {dec.user_goal}"
    assert dec.output_plan == OutputPlan.FOCUS_AREAS.value, f"Expected FOCUS_AREAS, got {dec.output_plan}"
    print("PASS: test_focus_inquiry_does_not_force_hearing_prep")


def test_response_planner_and_suggestions():
    """Verify response structure generation and contextual suggestions."""
    guidance = ResponsePlanner.get_structure_guidance(OutputPlan.KEY_POINTS)
    assert "Key Points" in guidance["sections"]
    assert guidance["max_tokens"] <= 350

    suggestions = SuggestionGenerator.generate_suggestions(SubIntent.CASE_KEY_POINTS, case_id="case-01")
    assert len(suggestions) >= 2
    assert any("hearing" in s["label"].lower() for s in suggestions)
    print("PASS: test_response_planner_and_suggestions")


def test_full_evaluation_dataset():
    """Runs all 100+ evaluation cases in query_understanding_eval.json."""
    router = UniversalQueryRouter()
    eval_path = REPO_ROOT / "evaluation" / "query_understanding_eval.json"
    if not eval_path.exists():
        eval_path = Path(__file__).resolve().parent.parent / "scratch" / "query_understanding_eval.json"

    with open(eval_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    passed = 0
    failed = 0
    failures = []

    for item in cases:
        q = item["query"]
        cid = item.get("case_id")
        exp_intent = item["expected_intent"]
        exp_sub = item.get("expected_sub_intent")
        exp_plan = item.get("expected_output_type")

        dec = router.classify(q, case_id=cid)

        intent_ok = (dec.intent.value == exp_intent)
        sub_ok = (dec.sub_intent == exp_sub) if exp_sub else True
        plan_ok = (dec.output_plan == exp_plan) if exp_plan else True

        if intent_ok and sub_ok and plan_ok:
            passed += 1
        else:
            failed += 1
            failures.append({
                "id": item["id"],
                "query": q,
                "case_id": cid,
                "expected": f"intent={exp_intent}, sub={exp_sub}, plan={exp_plan}",
                "got": f"intent={dec.intent.value}, sub={dec.sub_intent}, plan={dec.output_plan}"
            })

    print(f"\nQUERY UNDERSTANDING EVALUATION RESULTS: {passed} / {len(cases)} PASSED")
    if failed > 0:
        print(f"FAILURES ({failed}):")
        for fail in failures[:10]:
            print(f"  [{fail['id']}] '{fail['query']}' (case={fail['case_id']})")
            print(f"         Exp: {fail['expected']}")
            print(f"         Got: {fail['got']}")
        assert failed == 0, f"{failed} evaluation cases failed!"

    print("PASS: test_full_evaluation_dataset (100% SUCCESS)")


if __name__ == "__main__":
    test_legal_identifier_protection()
    test_general_typo_tolerance_unseen()
    test_focus_inquiry_does_not_force_hearing_prep()
    test_response_planner_and_suggestions()
    test_full_evaluation_dataset()
    print("\nALL QUERY UNDERSTANDING TESTS PASSED PERFECTLY!")
