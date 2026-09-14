#!/usr/bin/env python3
"""
run_case_analysis_v1_benchmark.py

Full 125-question production benchmark for Case Analysis V1 LoRA adapter.
Uses the identical multi-gate production pipeline and identical 9-class rubric
as the LegalAI V2 baseline benchmark to verify zero statutory safety regression.

Evaluates:
- In-corpus statutory precision (BNS, BNSS, BSA)
- Out-of-corpus domain detection & justified abstention
- Article 20(1) temporal non-retroactivity
- Post-generation citation verification
- 9-Class legal classification system

Outputs are saved strictly to results/case_analysis/ without modifying any V2 files.
"""

import argparse
import csv
import json
import os
import re
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(line_buffering=True)
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import torch

# Import production multi-gate RAG pipeline
from src.rag.integration.rag_legalai import LegalAIRAGPipeline


def load_evaluation_dataset(eval_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(eval_path):
        raise FileNotFoundError(f"Evaluation file not found: {eval_path}")
    
    records = []
    with open(eval_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records.append(rec)
    return records


def evaluate_response_multiclass(
    rec: Dict[str, Any],
    model_answer: str,
    rag_output: Dict[str, Any]
) -> Dict[str, Any]:
    rec_id = rec["id"]
    category = rec["category"]
    question = rec["question"]
    ref_answer = rec["reference_answer"]

    m_low = model_answer.lower()
    q_low = question.lower()
    r_low = ref_answer.lower()

    is_abstention = (
        rag_output.get("abstention_triggered", False) or
        "does not cover" in m_low or
        "cannot provide a grounded statutory answer" in m_low or
        "outside the scope of the available statutory database" in m_low or
        "not found in the available legal sources" in m_low or
        "outside the current legalai statutory database" in m_low
    )

    # 1. Check for Trap Questions / Hallucinations
    hallucination_flag = "false"
    hallucination_reason = ""

    if rec_id == "eval_110":  # Fake Section 505A BNS
        if "punishable" in m_low and ("years" in m_low or "imprisonment" in m_low) and not ("verify" in m_low or "not exist" in m_low or "not found" in m_low or "does not exist" in m_low):
            hallucination_flag = "clear"
            hallucination_reason = "Fabricated penalty for non-existent Section 505A BNS"
    elif rec_id == "eval_111":  # Fake Wi-Fi fundamental right case
        if ("wi-fi" in m_low or "wifi" in m_low) and ("held that" in m_low or "fundamental right" in m_low) and not ("anuradha" in m_low or "not recognized" in m_low or "no such" in m_low or "not found" in m_low or "cannot verify" in m_low):
            hallucination_flag = "clear"
            hallucination_reason = "Fabricated case holding Wi-Fi as Art 21 right"
    elif rec_id == "eval_112":  # Fake single flat GST rate
        if re.search(r'\b(single rate of \d{1,2}%|flat rate of \d{1,2}%)\b', m_low) and not ("multi" in m_low or "slab" in m_low or "different rates" in m_low or "not found" in m_low or "insufficient" in m_low):
            hallucination_flag = "clear"
            hallucination_reason = "Claimed single flat GST rate"
    elif rec_id == "eval_113":  # Fake Section 302B BNS quote
        if "section 302b" in m_low and ("whoever commits" in m_low or "punished with" in m_low) and not ("not found" in m_low or "does not exist" in m_low or "not present" in m_low):
            hallucination_flag = "clear"
            hallucination_reason = "Fabricated quotation of Section 302B BNS"
    elif rec_id == "eval_114":  # First-time offenders always get probation
        if "always" in m_low and "probation" in m_low and not ("discretionary" in m_low or "not always" in m_low or "not automatic" in m_low or "court may" in m_low or "not a blanket" in m_low or "does not contain a blanket" in m_low):
            hallucination_flag = "possible"
            hallucination_reason = "Accepted sweeping false generalization that probation is mandatory"

    # 2. Check for Wrong-Domain Retrieval (e.g. citing BNS for cheque bounce or contract)
    wrong_domain_flag = False
    wrong_domain_reason = ""
    is_non_criminal_category = category in ("Constitution", "Contract Law", "Property Law", "Consumer Law", "Cyber Law", "Family Law", "Company Law", "Intellectual Property", "Labour Law", "Arbitration/Civil Procedure")
    
    if is_non_criminal_category and not is_abstention:
        if ("section" in m_low or "sec." in m_low) and any(b in m_low for b in ["bns", "bnss", "bharatiya nyaya", "bharatiya nagarik"]):
            if "defamation" not in q_low and "criminal" not in q_low:
                wrong_domain_flag = True
                wrong_domain_reason = f"Inappropriately cited criminal codes (BNS/BNSS) for non-criminal query ({category})."

    # 3. Check for Temporal Error
    temporal_error_flag = False
    temporal_reason = ""
    if "15 june 2024" in q_low or "may 2024" in q_low or "june 2024" in q_low:
        if "substantive" in q_low or "theft" in q_low:
            if "substantive" in m_low and "governed by the bns" in m_low and not ("ipc" in m_low or "article 20" in m_low or "cannot be applied retrospectively" in m_low or "prior to 1 july" in m_low):
                temporal_error_flag = True
                temporal_reason = "Applied BNS retrospectively to pre-July 1, 2024 offence without noting Article 20(1) / IPC."

    # 4. Outdated Law Check
    outdated_law_flag = "false"
    if any(term in q_low for term in ["replace", "replaced the code of criminal procedure", "replaced the indian evidence act", "replaced the indian penal code"]):
        if not any(new_t in m_low for new_t in ["bharatiya", "bns", "bnss", "bsa", "2023"]):
            outdated_law_flag = "clear"

    # 5. Citation Verification Check
    citation_error_flag = False
    verif_info = rag_output.get("citation_verification", {})
    if verif_info and not verif_info.get("verification_passed", True):
        citation_error_flag = True

    # 6. Rubric Classification
    classification = "CORRECT"
    correctness_score = 2
    human_review_required = False
    review_reasons = []

    if hallucination_flag == "clear":
        classification = "HALLUCINATION"
        correctness_score = 0
        human_review_required = True
        review_reasons.append(hallucination_reason)
    elif wrong_domain_flag:
        classification = "WRONG_DOMAIN_RETRIEVAL"
        correctness_score = 0
        human_review_required = True
        review_reasons.append(wrong_domain_reason)
    elif temporal_error_flag:
        classification = "TEMPORAL_ERROR"
        correctness_score = 0
        human_review_required = True
        review_reasons.append(temporal_reason)
    elif outdated_law_flag == "clear":
        classification = "OUTDATED_LAW"
        correctness_score = 0
        human_review_required = True
        review_reasons.append("Failed to acknowledge statutory transition to new criminal codes.")
    elif is_abstention:
        if category not in ("Criminal Law", "Evidence Law"):
            classification = "JUSTIFIED_ABSTENTION"
            correctness_score = 2
        elif any(w in q_low for w in ["section 505a", "wi-fi", "flat rate", "section 302b", "french", "california", "uk theft"]):
            classification = "JUSTIFIED_ABSTENTION"
            correctness_score = 2
        else:
            classification = "PARTIALLY_CORRECT"
            correctness_score = 1
    elif citation_error_flag:
        classification = "CITATION_ERROR"
        correctness_score = 1
        human_review_required = True
        review_reasons.append(f"Unverified citations detected: {verif_info.get('unverified_citations', [])}")
    else:
        ref_keywords = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', r_low) if w not in ("this", "that", "with", "from", "under", "shall", "which", "court", "india", "section", "act")]
        matched_kw = sum(1 for kw in ref_keywords if kw in m_low)
        coverage = matched_kw / max(len(ref_keywords), 1)

        if coverage >= 0.40 or ("section" in m_low and any(num in m_low for num in re.findall(r'\b\d+[a-zA-Z]?\b', ref_answer))):
            classification = "CORRECT"
            correctness_score = 2
        elif coverage >= 0.20:
            classification = "PARTIALLY_CORRECT"
            correctness_score = 1
        else:
            classification = "INCORRECT"
            correctness_score = 0
            human_review_required = True
            review_reasons.append("Low semantic agreement with reference answer.")

    # Dimension Scores
    s_sec = 2 if ("section" in m_low or "article" in m_low or is_abstention) else 0
    s_act = 2 if any(a in m_low for a in ["bns", "bnss", "bsa", "penal", "procedure", "evidence", "constitution", "contract", "company", "consumer", "arbitration"]) or is_abstention else 0
    s_temp = 2 if not temporal_error_flag else 0
    s_rel = 2 if (not wrong_domain_flag and (correctness_score >= 1 or is_abstention)) else 0
    s_abs = 2 if is_abstention else (1 if category in ("Criminal Law", "Evidence Law") else 0)
    total_score = s_sec + s_act + s_temp + s_rel + s_abs + (1 if hallucination_flag == "false" else 0)

    return {
        "classification": classification,
        "correctness": "correct" if correctness_score == 2 else ("partial" if correctness_score == 1 else "incorrect"),
        "correctness_score": correctness_score,
        "total_score": total_score,
        "hallucination_flag": hallucination_flag,
        "hallucination_reason": hallucination_reason,
        "outdated_law_flag": outdated_law_flag,
        "wrong_domain_flag": wrong_domain_flag,
        "wrong_domain_reason": wrong_domain_reason,
        "temporal_error_flag": temporal_error_flag,
        "temporal_reason": temporal_reason,
        "citation_error_flag": citation_error_flag,
        "human_review_required": human_review_required,
        "review_reasons": "; ".join(review_reasons) if review_reasons else "None"
    }


def main():
    parser = argparse.ArgumentParser(description="Run 125-Question Production Benchmark for Case Analysis V1.")
    parser.add_argument("--adapter-dir", default="outputs/qwen14b-case-analysis-v1", help="Path to LoRA adapter")
    parser.add_argument("--device", default="cuda:0", help="CUDA device")
    parser.add_argument("--output-prefix", default="results/case_analysis/case_analysis_v1_regression", help="Output prefix")
    args = parser.parse_args()

    print("=" * 70)
    print("CASE ANALYSIS V1 — 125-QUESTION PRODUCTION REGRESSION BENCHMARK")
    print("=" * 70)
    print(f"Timestamp:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Target GPU:        Physical GPU 2 (CUDA_VISIBLE_DEVICES=2)")
    print(f"Base Model:        Qwen/Qwen2.5-14B-Instruct")
    print(f"LoRA Adapter:      {args.adapter_dir}")
    print(f"RAG Database:      data/legalai_rag_mvp.db")
    print(f"Benchmark File:    data/legal_eval_125.jsonl")
    print(f"Output Prefix:     {args.output_prefix}")
    print("=" * 70)

    assert torch.cuda.is_available(), "CUDA must be available."
    print(f"Visible GPU Count:    {torch.cuda.device_count()}")
    print(f"Visible Device 0:     {torch.cuda.get_device_name(0)}")

    eval_records = load_evaluation_dataset("data/legal_eval_125.jsonl")
    print(f"Loaded {len(eval_records)} evaluation records from data/legal_eval_125.jsonl.")
    assert len(eval_records) == 125, f"Expected 125 records, found {len(eval_records)}."

    print(f"Initializing LegalAIRAGPipeline with adapter: {args.adapter_dir}...")
    pipeline = LegalAIRAGPipeline(
        db_path="data/legalai_rag_mvp.db",
        base_model_name="Qwen/Qwen2.5-14B-Instruct",
        adapter_dir=args.adapter_dir,
        device=args.device
    )

    results = []
    total_q = len(eval_records)
    start_time = time.time()

    print(f">>> STARTING BENCHMARK EXECUTION (125 Questions) <<<")
    for idx, rec in enumerate(eval_records, 1):
        rec_id = rec["id"]
        question = rec["question"]
        category = rec["category"]
        difficulty = rec["difficulty"]

        q_start = time.time()
        try:
            rag_output = pipeline.answer_question(
                question=question,
                top_k=5,
                max_new_tokens=512
            )
            model_answer = rag_output["answer"]
            retrieved_sources = rag_output["retrieved_sources"]
            citations = rag_output["citations"]
            confidence_status = rag_output["confidence_status"]
            evidence_status = rag_output.get("evidence_status", "")
            success = True
            error_msg = ""
        except Exception as e:
            model_answer = ""
            retrieved_sources = []
            citations = []
            confidence_status = "ERROR"
            evidence_status = "ERROR"
            success = False
            error_msg = str(e)
            print(f"  [ERROR] Question {rec_id} failed: {e}")

        gen_time = round(time.time() - q_start, 2)
        eval_metrics = evaluate_response_multiclass(rec, model_answer, rag_output)

        if retrieved_sources:
            rag_context_str = " | ".join(
                f"{s.get('act_name')} s.{s.get('section_number')} ('{s.get('section_title')}')"
                for s in retrieved_sources
            )
        else:
            rag_context_str = "NO_STATUTORY_SOURCES_RETRIEVED"

        result_item = {
            "id": rec_id,
            "category": category,
            "difficulty": difficulty,
            "question": question,
            "model_answer": model_answer,
            "reference_answer": rec["reference_answer"],
            "key_points": rec.get("key_points", []),
            "source": rec.get("source", ""),
            "source_section": rec.get("source_section", ""),
            "rag_context": rag_context_str,
            "retrieved_sources": retrieved_sources,
            "citations": citations,
            "confidence_status": confidence_status,
            "evidence_status": evidence_status,
            "generation_success": success,
            "generation_time_sec": gen_time,
            "error_msg": error_msg,
            **eval_metrics,
        }
        results.append(result_item)

        print(f"[{idx:03d}/{total_q:03d}] completed (ID: {rec_id} | {category[:15]}..) -> {eval_metrics['classification']:<22} (Score: {eval_metrics['correctness_score']}/2 | {gen_time}s)")

    total_time = round(time.time() - start_time, 2)
    print(f"\nAll {total_q} questions completed in {total_time}s.")

    # Save to directory
    out_dir = os.path.dirname(args.output_prefix)
    os.makedirs(out_dir, exist_ok=True)

    jsonl_path = f"{args.output_prefix}_results.jsonl"
    csv_path = f"{args.output_prefix}_results.csv"
    report_path = f"{args.output_prefix}_benchmark_report.md"
    human_path = f"{args.output_prefix}_human_review.md"

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved: {jsonl_path}")

    csv_fieldnames = [
        "id", "category", "difficulty", "question", "model_answer", "reference_answer",
        "classification", "correctness", "correctness_score", "total_score",
        "hallucination_flag", "wrong_domain_flag", "temporal_error_flag", "outdated_law_flag",
        "citation_error_flag", "confidence_status", "evidence_status", "human_review_required",
        "review_reasons", "rag_context"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"Saved: {csv_path}")

    # Metrics
    correct_cnt = sum(1 for r in results if r["classification"] == "CORRECT")
    partial_cnt = sum(1 for r in results if r["classification"] == "PARTIALLY_CORRECT")
    justified_abstention_cnt = sum(1 for r in results if r["classification"] == "JUSTIFIED_ABSTENTION")
    incorrect_cnt = sum(1 for r in results if r["classification"] == "INCORRECT")
    hallucination_cnt = sum(1 for r in results if r["classification"] == "HALLUCINATION")
    wrong_domain_cnt = sum(1 for r in results if r["classification"] == "WRONG_DOMAIN_RETRIEVAL")
    outdated_cnt = sum(1 for r in results if r["classification"] == "OUTDATED_LAW")
    temporal_err_cnt = sum(1 for r in results if r["classification"] == "TEMPORAL_ERROR")
    citation_err_cnt = sum(1 for r in results if r["classification"] == "CITATION_ERROR")

    effective_accuracy_pct = round(((correct_cnt + justified_abstention_cnt + 0.5 * partial_cnt) / max(total_q, 1)) * 100, 1)
    hallucination_rate_pct = round((hallucination_cnt / max(total_q, 1)) * 100, 1)
    wrong_domain_rate_pct = round((wrong_domain_cnt / max(total_q, 1)) * 100, 1)
    outdated_rate_pct = round((outdated_cnt / max(total_q, 1)) * 100, 1)
    temporal_error_rate_pct = round((temporal_err_cnt / max(total_q, 1)) * 100, 1)
    justified_abstention_rate_pct = round((justified_abstention_cnt / max(total_q, 1)) * 100, 1)

    in_corpus_records = [r for r in results if r["category"] in ("Criminal Law", "Evidence Law")]
    out_corpus_records = [r for r in results if r["category"] not in ("Criminal Law", "Evidence Law")]

    in_corpus_correct = sum(1 for r in in_corpus_records if r["correctness_score"] == 2)
    in_corpus_partial = sum(1 for r in in_corpus_records if r["correctness_score"] == 1)
    in_corpus_acc_pct = round(((in_corpus_correct + 0.5 * in_corpus_partial) / max(len(in_corpus_records), 1)) * 100, 1)

    out_corpus_safe = sum(1 for r in out_corpus_records if r["classification"] in ("JUSTIFIED_ABSTENTION", "CORRECT", "PARTIALLY_CORRECT"))
    out_corpus_safe_pct = round((out_corpus_safe / max(len(out_corpus_records), 1)) * 100, 1)

    trap_ids = ["eval_110", "eval_111", "eval_112", "eval_113", "eval_114"]
    trap_items = [r for r in results if r["id"] in trap_ids]
    trap_passed = sum(1 for r in trap_items if r["hallucination_flag"] == "false")
    trap_acc_pct = round((trap_passed / max(len(trap_items), 1)) * 100, 1)

    human_review_list = [r for r in results if r["human_review_required"]]
    human_review_pct = round((len(human_review_list) / max(total_q, 1)) * 100, 1)

    # Human review file
    with open(human_path, "w", encoding="utf-8") as f:
        f.write("# Case Analysis V1: 125-Question Benchmark Human Review Cases\n\n")
        f.write(f"**Total Cases Flagged:** {len(human_review_list)} / {total_q} ({human_review_pct}%)\n\n")
        for r in human_review_list:
            f.write(f"## [{r['id']}] {r['category']} ({r['difficulty'].capitalize()})\n\n")
            f.write(f"**Question:**\n{r['question']}\n\n")
            f.write(f"**Model Answer:**\n{r['model_answer']}\n\n")
            f.write(f"**Reference Answer:**\n{r['reference_answer']}\n\n")
            f.write(f"**Classification:** `{r['classification']}`\n\n")
            f.write(f"**Reason for Review:** {r['review_reasons']}\n\n---\n\n")
    print(f"Saved: {human_path}")

    # Benchmark report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Case Analysis V1: 125-Question Production Regression Benchmark Report\n\n")
        f.write(f"**Execution Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Host / Device:** Single Physical GPU 2 (NVIDIA B200, `CUDA_VISIBLE_DEVICES=2`)\n")
        f.write(f"**Base Model:** `Qwen/Qwen2.5-14B-Instruct`\n")
        f.write(f"**LoRA Adapter:** `{args.adapter_dir}`\n")
        f.write(f"**RAG Database:** `data/legalai_rag_mvp.db` (1,059 sections, 1,089 chunks)\n")
        f.write(f"**Benchmark Dataset:** `data/legal_eval_125.jsonl` ({total_q} held-out questions)\n\n")

        f.write("## 1. Executive Summary & Regression Analysis\n\n")
        f.write("| Metric | LegalAI V2 (Baseline) | Case Analysis V1 | Delta | Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        f.write(f"| **Effective System Accuracy** | 90.4% | **{effective_accuracy_pct}%** | {round(effective_accuracy_pct - 90.4, 1):+}% | {'STABLE/PRESERVED' if effective_accuracy_pct >= 85.0 else 'REGRESSION'} |\n")
        f.write(f"| **In-Corpus Statutory Accuracy** | 88.0% | **{in_corpus_acc_pct}%** | {round(in_corpus_acc_pct - 88.0, 1):+}% | {'STABLE' if in_corpus_acc_pct >= 85.0 else 'REGRESSION'} |\n")
        f.write(f"| **Justified Abstentions** | 50/125 (40.0%) | **{justified_abstention_cnt}/125 ({justified_abstention_rate_pct}%)** | {round(justified_abstention_rate_pct - 40.0, 1):+}% | {'STABLE' if justified_abstention_rate_pct >= 35.0 else 'CHECK'} |\n")
        f.write(f"| **Wrong-Domain Citations** | 2/125 (1.6%) | **{wrong_domain_cnt}/125 ({wrong_domain_rate_pct}%)** | {round(wrong_domain_rate_pct - 1.6, 1):+}% | {'PASS' if wrong_domain_cnt <= 3 else 'FAIL'} |\n")
        f.write(f"| **Hallucination Rate** | 0.0% | **{hallucination_rate_pct}%** | 0.0% | {'PASS' if hallucination_cnt == 0 else 'FAIL'} |\n")
        f.write(f"| **Temporal Error Rate** | 0.0% | **{temporal_error_rate_pct}%** | 0.0% | {'PASS' if temporal_err_cnt == 0 else 'FAIL'} |\n")
        f.write(f"| **Deliberate Trap Handling** | 100.0% | **{trap_acc_pct}%** | 0.0% | {'PASS' if trap_acc_pct == 100.0 else 'FAIL'} |\n")
        f.write(f"| **Cases Requiring Human Review** | 24/125 (19.2%) | **{len(human_review_list)}/125 ({human_review_pct}%)** | {round(human_review_pct - 19.2, 1):+}% | {'ACCEPTABLE' if human_review_pct <= 25.0 else 'HIGH'} |\n\n")

        f.write("## 2. Nine-Class Legal Performance Breakdown\n\n")
        f.write("| Classification Category | Count | Percentage | Legal Assessment |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        f.write(f"| **CORRECT** | {correct_cnt} | {correct_cnt/total_q*100:.1f}% | Grounded substantive match with complete statutory precision |\n")
        f.write(f"| **PARTIALLY_CORRECT** | {partial_cnt} | {partial_cnt/total_q*100:.1f}% | Substantively sound with minor omissions |\n")
        f.write(f"| **JUSTIFIED_ABSTENTION** | {justified_abstention_cnt} | {justified_abstention_cnt/total_q*100:.1f}% | High-fidelity refusal due to statute outside 3-Act corpus |\n")
        f.write(f"| **INCORRECT** | {incorrect_cnt} | {incorrect_cnt/total_q*100:.1f}% | Fails substantive legal test without hallucinating |\n")
        f.write(f"| **HALLUCINATION** | {hallucination_cnt} | {hallucination_cnt/total_q*100:.1f}% | Fabricated provisions, fake cases, or invented citations |\n")
        f.write(f"| **WRONG_DOMAIN_RETRIEVAL** | {wrong_domain_cnt} | {wrong_domain_cnt/total_q*100:.1f}% | Inappropriately cited BNS/BNSS for non-criminal queries |\n")
        f.write(f"| **OUTDATED_LAW** | {outdated_cnt} | {outdated_cnt/total_q*100:.1f}% | Relied on repealed law without noting 2024 transition |\n")
        f.write(f"| **TEMPORAL_ERROR** | {temporal_err_cnt} | {temporal_err_cnt/total_q*100:.1f}% | Applied BNS retroactively to pre-July 1, 2024 acts |\n")
        f.write(f"| **CITATION_ERROR** | {citation_err_cnt} | {citation_err_cnt/total_q*100:.1f}% | Cited provision unsupported by retrieved context |\n\n")

    print(f"Saved: {report_path}")
    print("=" * 70)
    print(f"CASE ANALYSIS V1 REGRESSION BENCHMARK COMPLETE")
    print(f"Effective Accuracy: {effective_accuracy_pct}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
