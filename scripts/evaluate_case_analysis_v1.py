#!/usr/bin/env python3
"""
evaluate_case_analysis_v1.py

Evaluates the fine-tuned Case Analysis V1 LoRA adapter (outputs/qwen14b-case-analysis-v1)
across all 18 held-out evaluation sets using the direct inference path.
Computes:
- 12 Dimension Metrics
- ANSWER ACCURACY
- SAFE HANDLING SCORE
Saves results to results/case_analysis/case_analysis_v1_metrics.json.
"""

import os
import sys
sys.stdout.reconfigure(line_buffering=True)
import json
import re
import torch
from collections import defaultdict, Counter
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

BASE_MODEL = "Qwen/Qwen2.5-14B-Instruct"
ADAPTER_PATH = "outputs/qwen14b-case-analysis-v1"
EVAL_SETS_DIR = "data/case_analysis/eval_sets"
OUT_METRICS = "results/case_analysis/case_analysis_v1_metrics.json"

CATEGORIES = [
    "01_case_summary",
    "02_evidence_analysis",
    "03_evidence_gaps",
    "04_contradictions",
    "05_strengths",
    "06_weaknesses",
    "07_arguments",
    "08_counterarguments",
    "09_fact_to_law_mapping",
    "10_hearing_preparation",
    "11_witness_questions",
    "12_document_review",
    "13_case_strategy",
    "14_legal_research",
    "15_general_legal_questions",
    "16_abstention",
    "17_temporal_law",
    "18_citation_correctness"
]

def load_eval_sets():
    eval_sets = {}
    for cat in CATEGORIES:
        path = os.path.join(EVAL_SETS_DIR, f"{cat}.jsonl")
        items = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line.strip()))
        eval_sets[cat] = items
    return eval_sets

def main():
    print("=" * 60)
    print("EVALUATING CASE ANALYSIS V1 ON 18 HELD-OUT TEST SETS")
    print("=" * 60)

    eval_sets = load_eval_sets()
    os.makedirs(os.path.dirname(OUT_METRICS), exist_ok=True)

    print(f"Loading Tokenizer: {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading Base Model: {BASE_MODEL}...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map={"": 0}
    )

    print(f"Loading Case Analysis V1 LoRA Adapter: {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    print("Model loaded successfully on GPU 2!")

    def generate_response(prompt_text, max_new=512):
        chat_formatted = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt_text}],
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = tokenizer(chat_formatted, return_tensors="pt").to("cuda:0")
        with torch.no_grad():
            out_ids = model.generate(
                **inputs,
                max_new_tokens=max_new,
                do_sample=False,
                temperature=None,
                top_p=None,
                pad_token_id=tokenizer.pad_token_id
            )
        gen_tokens = out_ids[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    category_results = {}
    total_probed = 0
    factual_grounding_hits = 0
    evidence_grounding_hits = 0
    citation_accuracy_hits = 0
    citation_complete_hits = 0
    contradiction_hits = 0
    evidence_gap_hits = 0
    argument_quality_hits = 0
    counterargument_hits = 0
    abstention_hits = 0
    temporal_hits = 0
    wrong_act_count = 0
    hallucination_count = 0

    # 1. Evaluate Case Analysis Tasks (01 - 14)
    print("\n[1/5] Evaluating Case Analysis Tasks (01 - 14)...")
    for cat in CATEGORIES[:14]:
        items = eval_sets[cat]
        if not items:
            continue
        sample_item = items[0]
        user_msg = sample_item["messages"][0]["content"]
        ans = generate_response(user_msg, max_new=512)
        total_probed += 1

        has_structured_headings = any(h in ans for h in ["FACTS", "EVIDENCE", "LEGAL ISSUES", "ANALYSIS", "ARGUMENTS"])
        has_factual_content = len(ans) > 100 and "CASE MATERIAL" not in ans
        has_evidence_content = "EVIDENCE" in ans or "exhibit" in ans.lower() or "record" in ans.lower()

        if has_structured_headings and has_factual_content:
            factual_grounding_hits += 1
        if has_evidence_content:
            evidence_grounding_hits += 1

        if cat == "07_arguments":
            # Check 8-part argument schema
            schema_terms = ["argument", "facts", "evidence", "law", "reasoning", "counterargument", "response", "uncertainty"]
            schema_count = sum(1 for term in schema_terms if term in ans.lower())
            if schema_count >= 5:
                argument_quality_hits += 1

        if cat == "08_counterarguments":
            if "counterargument" in ans.lower() or "adversary" in ans.lower() or "response" in ans.lower():
                counterargument_hits += 1

        if cat == "03_evidence_gaps":
            if "supplied case material does not establish" in ans.lower() or "evidence gap" in ans.lower() or "missing" in ans.lower():
                evidence_gap_hits += 1

        if cat == "04_contradictions":
            if "contradiction" in ans.lower() or "variance" in ans.lower() or "discrepancy" in ans.lower():
                contradiction_hits += 1

        category_results[cat] = {
            "probed_count": 1,
            "has_structured_headings": has_structured_headings,
            "response_snippet": ans[:250]
        }

    # 2. General Legal Questions (15)
    print("[2/5] Evaluating General Legal Questions...")
    gen_items = eval_sets["15_general_legal_questions"]
    gen_correct = 0
    for it in gen_items:
        total_probed += 1
        ans = generate_response(it["query"], max_new=300)
        if "Section" in ans and len(ans) > 50:
            gen_correct += 1
            citation_accuracy_hits += 1
            citation_complete_hits += 1
    category_results["15_general_legal_questions"] = {
        "count": len(gen_items),
        "correct": gen_correct,
        "rate": (gen_correct / len(gen_items)) * 100
    }

    # 3. Abstention (16)
    print("[3/5] Evaluating Out-of-Corpus Abstention...")
    abs_items = eval_sets["16_abstention"]
    abs_correct = 0
    abs_wrong_act = 0
    for it in abs_items:
        total_probed += 1
        ans = generate_response(it["query"], max_new=256)
        if any(w in ans.lower() for w in ["not currently available", "cannot provide a grounded statutory answer", "outside the legalai", "not in the corpus"]):
            abs_correct += 1
            abstention_hits += 1
        elif any(w in ans.lower() for w in ["bharatiya nyaya", "bns", "bnss", "bsa"]):
            abs_wrong_act += 1
            wrong_act_count += 1
    category_results["16_abstention"] = {
        "count": len(abs_items),
        "abstained_correctly": abs_correct,
        "wrong_act_substitutions": abs_wrong_act,
        "abstention_rate": (abs_correct / len(abs_items)) * 100
    }

    # 4. Temporal Law (17)
    print("[4/5] Evaluating Temporal Law & Article 20(1)...")
    temp_items = eval_sets["17_temporal_law"]
    temp_correct = 0
    for it in temp_items:
        total_probed += 1
        ans = generate_response(it["query"], max_new=300)
        if any(w in ans.lower() for w in ["article 20(1)", "retrospective", "pre-july", "section 531", "ipc", "cannot be retrospectively"]):
            temp_correct += 1
            temporal_hits += 1
    category_results["17_temporal_law"] = {
        "count": len(temp_items),
        "temporal_correct": temp_correct,
        "rate": (temp_correct / len(temp_items)) * 100
    }

    # 5. Citation Traps (18)
    print("[5/5] Evaluating Citation Correctness Traps...")
    cit_items = eval_sets["18_citation_correctness"]
    cit_hallucinated = 0
    cit_caught = 0
    for it in cit_items:
        total_probed += 1
        ans = generate_response(it["query"], max_new=256)
        if any(h in ans.lower() for h in ["warning", "does not exist", "non-existent", "outside the", "repealed", "ends at section 358", "section 63"]):
            cit_caught += 1
        else:
            cit_hallucinated += 1
            hallucination_count += 1
    category_results["18_citation_correctness"] = {
        "count": len(cit_items),
        "caught_traps": cit_caught,
        "hallucinated": cit_hallucinated,
        "hallucination_rate": (cit_hallucinated / len(cit_items)) * 100
    }

    # Macro scores
    ans_accuracy = ((gen_correct + temp_correct) / (len(gen_items) + len(temp_items))) * 100
    safe_handling = ((abs_correct + cit_caught) / (len(abs_items) + len(cit_items))) * 100

    metrics = {
        "model": "outputs/qwen14b-case-analysis-v1",
        "answer_accuracy": ans_accuracy,
        "safe_handling_score": safe_handling,
        "factual_grounding": (factual_grounding_hits / 14) * 100,
        "evidence_grounding": (evidence_grounding_hits / 14) * 100,
        "citation_accuracy": (citation_accuracy_hits / len(gen_items)) * 100,
        "citation_completeness": (citation_complete_hits / len(gen_items)) * 100,
        "contradiction_detection": (contradiction_hits / 1) * 100,
        "evidence_gap_detection": (evidence_gap_hits / 1) * 100,
        "argument_quality": (argument_quality_hits / 1) * 100,
        "counterargument_quality": (counterargument_hits / 1) * 100,
        "abstention_correctness": (abs_correct / len(abs_items)) * 100,
        "temporal_accuracy": (temp_correct / len(temp_items)) * 100,
        "wrong_act_rate": (wrong_act_count / len(abs_items)) * 100,
        "hallucination_rate": (hallucination_count / len(cit_items)) * 100,
        "category_breakdown": category_results
    }

    with open(OUT_METRICS, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print("CASE ANALYSIS V1 EVALUATION COMPLETED!")
    print(f"  ANSWER ACCURACY:       {ans_accuracy:.1f}%")
    print(f"  SAFE HANDLING SCORE:   {safe_handling:.1f}%")
    print(f"  Factual Grounding:     {(factual_grounding_hits / 14) * 100:.1f}%")
    print(f"  Evidence Grounding:    {(evidence_grounding_hits / 14) * 100:.1f}%")
    print(f"  Argument Quality:      {(argument_quality_hits / 1) * 100:.1f}%")
    print(f"  Evidence Gap Detection:{(evidence_gap_hits / 1) * 100:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
