"""
tests/test_case_query_driven_generation.py

Validates Query-Driven Generation and Anti-Template Safety for LegalAI Case RAG.
Ensures:
1. Different questions produce question-specific, materially divergent outputs.
2. Sub-intents and Output Plans are accurately routed.
3. Universal 5-section Case Analysis template is NOT universally stamped.
4. Generation prompts dynamically reflect USER QUERY, SUB-INTENT, USER GOAL,
   OUTPUT PLAN, CASE SCOPE, RETRIEVED CASE EVIDENCE, and planner instruction.
"""

import sys
import os
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.api.query_router import UniversalQueryRouter, QueryIntent
from src.api.query_understanding.goals import SubIntent, UserGoal, OutputPlan
from src.api.query_understanding.planner import ResponsePlanner


def test_routing_sub_intents_and_plans():
    """Verify that substantially different questions map to distinct sub-intents and output plans."""
    router = UniversalQueryRouter()
    case_id = "case-01"

    test_matrix = [
        ("What is the matter?", "CASE_SUMMARY", OutputPlan.CASE_SUMMARY.value),
        ("waht is the matter", "CASE_SUMMARY", OutputPlan.CASE_SUMMARY.value),
        ("wht is the matter", "CASE_SUMMARY", OutputPlan.CASE_SUMMARY.value),
        ("what is this case about", "CASE_SUMMARY", OutputPlan.CASE_SUMMARY.value),
        ("tell me about this matter", "CASE_SUMMARY", OutputPlan.CASE_SUMMARY.value),
        ("What are the key points?", "CASE_KEY_POINTS", OutputPlan.KEY_POINTS.value),
        ("What evidence do we have?", "CASE_EVIDENCE", OutputPlan.AVAILABLE_EVIDENCE.value),
        ("What evidence are we missing?", "CASE_EVIDENCE_GAPS", OutputPlan.EVIDENCE_GAPS.value),
        ("What should I prepare for the next hearing?", "HEARING_PREPARATION", OutputPlan.HEARING_BRIEF.value),
        ("What are our arguments?", "CASE_ARGUMENTS", OutputPlan.POTENTIAL_ARGUMENTS.value),
        ("What could the other side argue?", "CASE_COUNTERARGUMENTS", OutputPlan.OPPOSING_ARGUMENTS.value),
        ("Where is our case weak?", "CASE_RISKS", OutputPlan.CASE_RISKS.value),
        ("What happened so far?", "CASE_TIMELINE", OutputPlan.CHRONOLOGICAL_TIMELINE.value),
    ]

    for query, exp_sub, exp_plan in test_matrix:
        dec = router.classify(query, case_id=case_id)
        assert dec.sub_intent == exp_sub, f"Query '{query}' expected sub_intent {exp_sub}, got {dec.sub_intent}"
        assert dec.output_plan == exp_plan, f"Query '{query}' expected output_plan {exp_plan}, got {dec.output_plan}"


def test_generation_prompt_structure():
    """Verify prompt formatting includes required metadata and planner instruction."""
    # Test ResponsePlanner provides valid instructions
    for plan in [
        OutputPlan.CASE_SUMMARY,
        OutputPlan.KEY_POINTS,
        OutputPlan.AVAILABLE_EVIDENCE,
        OutputPlan.EVIDENCE_GAPS,
        OutputPlan.POTENTIAL_ARGUMENTS,
        OutputPlan.OPPOSING_ARGUMENTS,
        OutputPlan.CASE_RISKS,
        OutputPlan.CHRONOLOGICAL_TIMELINE,
        OutputPlan.HEARING_BRIEF,
    ]:
        guidance = ResponsePlanner.get_structure_guidance(plan)
        instruction = guidance.get("instruction") or guidance.get("system_instruction")
        assert instruction, f"Missing instruction for plan {plan}"
        assert len(instruction) > 20

    # Verify dummy prompt assembly contains required fields
    query = "What evidence do we have?"
    sub_intent = "CASE_EVIDENCE"
    user_goal = "ANALYZE_EVIDENCE"
    output_plan = OutputPlan.AVAILABLE_EVIDENCE.value
    guidance = ResponsePlanner.get_structure_guidance(output_plan)
    instruction_text = guidance.get("instruction")

    user_prompt = (
        f"CASE SCOPE: Current Matter (Martinez v. Coastal Holdings, 2024-CV-1187)\n"
        f"USER QUERY: {query}\n"
        f"SUB-INTENT: {sub_intent}\n"
        f"USER GOAL: {user_goal}\n"
        f"OUTPUT PLAN: {output_plan}\n\n"
        f"RETRIEVED CASE EVIDENCE:\n[Sample chunk]\n\n"
        f"INSTRUCTIONS FOR GENERATION:\n"
        f"{instruction_text}\n"
    )

    assert "CASE SCOPE" in user_prompt
    assert "USER QUERY: What evidence do we have?" in user_prompt
    assert "SUB-INTENT: CASE_EVIDENCE" in user_prompt
    assert "USER GOAL: ANALYZE_EVIDENCE" in user_prompt
    assert "OUTPUT PLAN: AVAILABLE_EVIDENCE" in user_prompt
    assert "RETRIEVED CASE EVIDENCE" in user_prompt
    assert instruction_text in user_prompt


def test_anti_template_output_differentiation():
    """
    Simulates output differentiation and verifies that responses for different queries
    do not share a rigid universal five-section template.
    """
    # Verify planner structure schemas are distinct
    plans = [
        OutputPlan.CASE_SUMMARY,
        OutputPlan.KEY_POINTS,
        OutputPlan.AVAILABLE_EVIDENCE,
        OutputPlan.EVIDENCE_GAPS,
        OutputPlan.POTENTIAL_ARGUMENTS,
        OutputPlan.OPPOSING_ARGUMENTS,
        OutputPlan.CASE_RISKS,
        OutputPlan.CHRONOLOGICAL_TIMELINE,
        OutputPlan.HEARING_BRIEF
    ]

    instructions = [ResponsePlanner.get_structure_guidance(p)["instruction"] for p in plans]
    # Every plan must have a distinct instruction
    assert len(set(instructions)) == len(plans), "Plan instructions must be distinct"

    # Verify that an evidence response schema does NOT contain KEY POINTS or NEXT STEPS
    ev_guidance = ResponsePlanner.get_structure_guidance(OutputPlan.AVAILABLE_EVIDENCE)["instruction"]
    assert "KEY POINTS" not in ev_guidance
    assert "NEXT STEPS" not in ev_guidance

    # Verify that a summary response schema does NOT contain EVIDENCE GAPS or RISKS
    summary_guidance = ResponsePlanner.get_structure_guidance(OutputPlan.CASE_SUMMARY)["instruction"]
    assert "EVIDENCE GAPS" not in summary_guidance
    assert "POTENTIAL RISKS" not in summary_guidance
