#!/usr/bin/env python3
"""
evaluate_legalai_v2.py

Automated evaluation harness for fine-tuned LegalAI v2 (Qwen2.5-14B-Instruct + LoRA).
Evaluates the model on the held-out benchmark: data/legal_eval_125.jsonl.

Strict Prompt Isolation:
  The model prompt receives ONLY the user question and the system prompt.
  No reference answer, key points, category, or source information is ever passed to the model.

Outputs are saved with '_v2' filenames to strictly prevent overwriting v1 evaluation files:
  - results/legal_eval_125_v2_results.jsonl
  - results/legal_eval_125_v2_results.csv
  - results/legal_eval_125_v2_EVALUATION_REPORT.md
  - results/legal_eval_125_v2_HUMAN_REVIEW_REQUIRED.md
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-14B-Instruct"
DEFAULT_ADAPTER_DIR = "outputs/qwen14b-legalai-v2"
DEFAULT_EVAL_FILE = "data/legal_eval_125.jsonl"
DEFAULT_RESULTS_DIR = "results"

SYSTEM_PROMPT = (
    "You are LegalAI, an AI assistant focused on Indian law. Provide accurate, cautious, and clearly "
    "explained legal information. Do not invent statutes, sections, cases, penalties, or legal principles. "
    "When the available facts are insufficient, clearly say that more information is needed. Distinguish "
    "between current law and historical law where relevant. This response is for informational purposes "
    "and is not a substitute for advice from a qualified lawyer."
)


def load_evaluation_dataset(eval_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(eval_path):
        raise FileNotFoundError(f"Evaluation file not found: {eval_path}")
    
    records = []
    with open(eval_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError as e:
                raise ValueError(f"Line {line_num} in {eval_path} is invalid JSON: {e}")
    return records


def load_model_and_tokenizer(base_model_path: str, adapter_path: str):
    print("=" * 65)
    print("LEGALAI V2 EVALUATION HARNESS — MODEL INITIALIZATION")
    print("=" * 65)
    print(f"Base Model:        {base_model_path}")
    print(f"LoRA Adapter:      {adapter_path}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32

    print(f"Primary Device:    {device_name}")
    print(f"Torch Precision:   {dtype}")
    print("=" * 65)

    tokenizer_dir = adapter_path if os.path.exists(os.path.join(adapter_path, "tokenizer_config.json")) else base_model_path
    print(f"Loading tokenizer from: {tokenizer_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading base model in {dtype}...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=False,
    )

    if os.path.exists(adapter_path):
        print(f"Attaching LoRA adapter from: {adapter_path}...")
        model = PeftModel.from_pretrained(base_model, adapter_path)
    else:
        raise FileNotFoundError(f"LoRA adapter directory not found: {adapter_path}")

    model.eval()
    print("Model loaded and set to evaluation mode.\n")
    return model, tokenizer


def generate_answer(
    model,
    tokenizer,
    question: str,
    max_new_tokens: int = 512,
) -> Tuple[str, float, int]:
    """
    STRICT PROMPT ISOLATION:
    Only system prompt and the user question are supplied.
    Deterministic greedy generation (do_sample=False).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    rendered_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    model_device = getattr(model, "device", next(model.parameters()).device)
    inputs = tokenizer(rendered_prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(model_device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    t0 = time.time()
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    gen_time = time.time() - t0

    generated_tokens = output_ids[0][input_length:]
    num_tokens = len(generated_tokens)
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    return response_text, gen_time, num_tokens


def evaluate_response(
    rec: Dict[str, Any],
    model_answer: str,
) -> Dict[str, Any]:
    """
    Evaluates model answer against reference answer and key points using rubric (0-11).
    """
    rec_id = rec["id"]
    category = rec["category"]
    question = rec["question"]
    ref_answer = rec["reference_answer"]
    key_points = rec.get("key_points", [])
    src_sec = str(rec.get("source_section", "")).lower()

    m_low = model_answer.lower()
    ref_low = ref_answer.lower()

    # 1. Relevance check
    relevance_score = 1 if len(model_answer.strip()) > 30 else 0

    # 2. Key points coverage
    covered_points = 0
    total_points = max(len(key_points), 1)
    for kp in key_points:
        kp_words = [w.lower() for w in re.findall(r'\b\w{4,}\b', kp)]
        matches = sum(1 for w in kp_words if w in m_low)
        if matches >= max(len(kp_words) // 2, 1):
            covered_points += 1
    
    completeness_ratio = covered_points / total_points
    if completeness_ratio >= 0.7:
        completeness_score = 2
    elif completeness_ratio >= 0.35:
        completeness_score = 1
    else:
        completeness_score = 0

    # 3. Current-law correctness
    current_law_score = 2
    outdated_law_flag = "false"
    
    # Check for specific transitional checks
    if any(term in question.lower() for term in ["replace", "substantive", "current law", "1 july 2024", "bns", "bnss", "bsa"]):
        # Should mention new criminal acts if asking about current law
        if "replaced the indian penal code" in question.lower() or "replaced the code of criminal procedure" in question.lower() or "replaced the indian evidence act" in question.lower():
            if "bharatiya" in m_low or "bns" in m_low or "bnss" in m_low or "bsa" in m_low:
                current_law_score = 2
            else:
                current_law_score = 0
                outdated_law_flag = "clear"

    # If the question asks about pre-July 2024 offence vs post-July 2024
    if "15 june 2024" in question.lower() or "may 2024" in question.lower() or "june 2024" in question.lower():
        if "ipc" in m_low or "article 20" in m_low or "retrospective" in m_low:
            current_law_score = 2
        else:
            current_law_score = 1

    # 4. Hallucination Detection
    hallucination_flag = "false"
    hallucination_penalty = 0
    hallucination_reason = ""

    # Specific trap questions
    if rec_id == "eval_110":  # Trap section 505A BNS
        if "punishable" in m_low and ("years" in m_low or "fine of" in m_low or "imprisonment" in m_low) and not ("verify" in m_low or "check" in m_low or "does not exist" in m_low or "no specific" in m_low or "not exist" in m_low):
            hallucination_flag = "clear"
            hallucination_penalty = 2
            hallucination_reason = "Fabricated penalty for non-existent Section 505A of BNS."
        else:
            hallucination_flag = "false"

    elif rec_id == "eval_111":  # Trap Wi-Fi fundamental right case
        if "v." in m_low or "versus" in m_low or "held that" in m_low:
            if "wi-fi" in m_low and ("supreme court" in m_low or "held" in m_low) and not ("anuradha" in m_low or "no such" in m_low or "no case" in m_low or "not recognized" in m_low or "cannot verify" in m_low or "never held" in m_low):
                hallucination_flag = "clear"
                hallucination_penalty = 2
                hallucination_reason = "Fabricated case holding Wi-Fi access as Art 21 Fundamental Right."
        else:
            hallucination_flag = "false"

    elif rec_id == "eval_112":  # Trap single flat GST rate
        if re.search(r'\b(is \d{1,2}%|single rate of \d{1,2}%|flat rate of \d{1,2}%)\b', m_low) and not ("multi" in m_low or "slab" in m_low or "no single" in m_low or "different rates" in m_low or "not a single" in m_low or "multiple" in m_low):
            hallucination_flag = "clear"
            hallucination_penalty = 2
            hallucination_reason = "Claimed a single flat GST rate across India."
        else:
            hallucination_flag = "false"

    elif rec_id == "eval_113":  # Trap Section 302B BNS verbatim quote
        if "section 302b" in m_low and ("whoever commits" in m_low or "punished with" in m_low) and not ("verify" in m_low or "does not exist" in m_low or "not present" in m_low or "does not have" in m_low):
            hallucination_flag = "clear"
            hallucination_penalty = 2
            hallucination_reason = "Fabricated quotation of Section 302B BNS."
        else:
            hallucination_flag = "false"

    elif rec_id == "eval_114":  # Trap first-time offenders always get probation
        if "always" in m_low and "probation" in m_low and not ("discretionary" in m_low or "not always" in m_low or "not automatic" in m_low or "court may" in m_low or "misconception" in m_low):
            hallucination_flag = "possible"
            hallucination_penalty = 1
            hallucination_reason = "Accepted sweeping false generalization that probation is mandatory."
        else:
            hallucination_flag = "false"

    # 5. Uncertainty & Insufficient Information Handling
    uncertainty_score = 1
    if rec_id in ("eval_124", "eval_125", "eval_104", "eval_106"):
        if any(c in m_low for c in ["depends on", "insufficient", "more information", "consult", "without seeing", "without knowing", "specific circumstances", "cannot be determined"]):
            uncertainty_score = 2
        elif any(c in m_low for c in ["definitely", "certainly", "guaranteed"]):
            uncertainty_score = 0
            if hallucination_flag == "false":
                hallucination_flag = "possible"
        else:
            uncertainty_score = 1
    else:
        uncertainty_score = 2

    # 6. Legal Correctness
    if hallucination_flag == "clear":
        correctness_score = 0
    elif completeness_score == 2 and current_law_score >= 1:
        correctness_score = 2
    elif completeness_score >= 1 and current_law_score >= 1:
        correctness_score = 1
    else:
        correctness_score = 0

    hallucination_component = max(0, 2 - hallucination_penalty)
    total_score = (
        correctness_score +
        completeness_score +
        current_law_score +
        hallucination_component +
        uncertainty_score +
        relevance_score
    )

    human_review_required = False
    review_reasons = []
    if hallucination_flag in ("possible", "clear"):
        human_review_required = True
        review_reasons.append(f"Hallucination flag: {hallucination_flag} ({hallucination_reason})")
    if outdated_law_flag in ("possible", "clear"):
        human_review_required = True
        review_reasons.append(f"Outdated law flag: {outdated_law_flag}")
    if correctness_score == 0:
        human_review_required = True
        review_reasons.append("Correctness score is 0")
    if total_score < 6:
        human_review_required = True
        review_reasons.append(f"Low total score ({total_score}/11)")

    return {
        "correctness": "correct" if correctness_score == 2 else ("partial" if correctness_score == 1 else "incorrect"),
        "correctness_score": correctness_score,
        "completeness_score": completeness_score,
        "current_law_score": current_law_score,
        "hallucination_flag": hallucination_flag,
        "hallucination_reason": hallucination_reason,
        "outdated_law_flag": outdated_law_flag,
        "uncertainty_handling_score": uncertainty_score,
        "relevance_score": relevance_score,
        "total_score": total_score,
        "human_review_required": human_review_required,
        "review_reasons": "; ".join(review_reasons) if review_reasons else "None",
    }


def run_evaluation(
    eval_records: List[Dict[str, Any]],
    model,
    tokenizer,
    max_questions: int = None,
    smoke_test: bool = False,
) -> List[Dict[str, Any]]:
    target_records = eval_records[:max_questions] if max_questions else eval_records
    results = []

    print(f"Starting evaluation on {len(target_records)} questions...")
    for idx, rec in enumerate(target_records, 1):
        rec_id = rec["id"]
        question = rec["question"]
        category = rec["category"]
        difficulty = rec["difficulty"]

        print(f"[{idx:03d}/{len(target_records):03d}] Evaluating {rec_id} ({category} | {difficulty})...")
        
        try:
            model_answer, gen_time, num_tokens = generate_answer(
                model=model,
                tokenizer=tokenizer,
                question=question,
                max_new_tokens=512,
            )
            success = True
            error_msg = ""
        except Exception as e:
            model_answer = ""
            gen_time = 0.0
            num_tokens = 0
            success = False
            error_msg = str(e)
            print(f"  ERROR generating for {rec_id}: {e}")

        eval_metrics = evaluate_response(rec, model_answer)

        result_item = {
            "id": rec_id,
            "category": category,
            "difficulty": difficulty,
            "question": question,
            "model_answer": model_answer,
            "generation_success": success,
            "generation_time_sec": round(gen_time, 2),
            "generated_tokens": num_tokens,
            "error_msg": error_msg,
            "reference_answer": rec["reference_answer"],
            "key_points": rec.get("key_points", []),
            "source": rec.get("source", ""),
            "source_section": rec.get("source_section", ""),
            **eval_metrics,
        }
        results.append(result_item)

        if smoke_test:
            print("-" * 65)
            print(f"ID: {rec_id}")
            print(f"Question: {question}")
            print(f"Generated Answer:\n{model_answer}")
            print(f"Scoring: Correctness={eval_metrics['correctness_score']}/2, Total={eval_metrics['total_score']}/11")
            print("-" * 65)

    return results


def save_results_v2(results: List[Dict[str, Any]], results_dir: str):
    os.makedirs(results_dir, exist_ok=True)
    jsonl_path = os.path.join(results_dir, "legal_eval_125_v2_results.jsonl")
    csv_path = os.path.join(results_dir, "legal_eval_125_v2_results.csv")

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved results JSONL: {jsonl_path}")

    fieldnames = [
        "id", "category", "difficulty", "question", "model_answer",
        "correctness", "correctness_score", "completeness_score", "current_law_score",
        "hallucination_flag", "outdated_law_flag", "uncertainty_handling_score",
        "relevance_score", "total_score", "human_review_required"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"Saved results CSV:   {csv_path}")


def generate_reports_v2(
    results: List[Dict[str, Any]],
    results_dir: str,
    base_model_name: str,
    adapter_dir: str,
    eval_filepath: str,
):
    os.makedirs(results_dir, exist_ok=True)
    report_path = os.path.join(results_dir, "legal_eval_125_v2_EVALUATION_REPORT.md")
    human_path = os.path.join(results_dir, "legal_eval_125_v2_HUMAN_REVIEW_REQUIRED.md")

    total_q = len(results)
    gen_success = sum(1 for r in results if r["generation_success"])
    correct_count = sum(1 for r in results if r["correctness_score"] == 2)
    partial_count = sum(1 for r in results if r["correctness_score"] == 1)
    incorrect_count = sum(1 for r in results if r["correctness_score"] == 0)

    accuracy_pct = round(((correct_count + 0.5 * partial_count) / max(total_q, 1)) * 100, 1)

    hallucination_clear = sum(1 for r in results if r["hallucination_flag"] == "clear")
    hallucination_possible = sum(1 for r in results if r["hallucination_flag"] == "possible")
    hallucination_rate_pct = round(((hallucination_clear + hallucination_possible) / max(total_q, 1)) * 100, 1)

    outdated_count = sum(1 for r in results if r["outdated_law_flag"] in ("possible", "clear"))
    outdated_rate_pct = round((outdated_count / max(total_q, 1)) * 100, 1)

    human_review_list = [r for r in results if r["human_review_required"]]

    categories = sorted(list(set(r["category"] for r in results)))
    cat_stats = []
    for c in categories:
        c_items = [r for r in results if r["category"] == c]
        tot = len(c_items)
        cor = sum(1 for r in c_items if r["correctness_score"] == 2)
        par = sum(1 for r in c_items if r["correctness_score"] == 1)
        inc = sum(1 for r in c_items if r["correctness_score"] == 0)
        hal = sum(1 for r in c_items if r["hallucination_flag"] in ("possible", "clear"))
        acc = round(((cor + 0.5 * par) / max(tot, 1)) * 100, 1)
        cat_stats.append((c, tot, cor, par, inc, hal, acc))

    diff_levels = ["easy", "medium", "hard"]
    diff_stats = []
    for d in diff_levels:
        d_items = [r for r in results if r["difficulty"] == d]
        tot = len(d_items)
        cor = sum(1 for r in d_items if r["correctness_score"] == 2)
        par = sum(1 for r in d_items if r["correctness_score"] == 1)
        inc = sum(1 for r in d_items if r["correctness_score"] == 0)
        acc = round(((cor + 0.5 * par) / max(tot, 1)) * 100, 1)
        diff_stats.append((d.capitalize(), tot, cor, par, inc, acc))

    top_10 = sorted(results, key=lambda x: (x["total_score"], x["correctness_score"]), reverse=True)[:10]
    bottom_10 = sorted(results, key=lambda x: (x["total_score"], x["correctness_score"]))[:10]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LegalAI v2: 125-Question Evaluation Report\n\n")
        f.write(f"**Execution Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Base Model:** `{base_model_name}`\n")
        f.write(f"**LoRA Adapter:** `{adapter_dir}`\n")
        f.write(f"**Evaluation Benchmark:** `{eval_filepath}` (Total: {total_q})\n\n")

        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Total Questions:** `{total_q}`\n")
        f.write(f"- **Generation Completed:** `{gen_success}/{total_q}`\n")
        f.write(f"- **Preliminary Accuracy:** **`{accuracy_pct}%`**\n")
        f.write(f"- **Overall Hallucination Rate:** **`{hallucination_rate_pct}%`** (Clear: {hallucination_clear}, Possible: {hallucination_possible})\n")
        f.write(f"- **Outdated Law Rate:** **`{outdated_rate_pct}%`** ({outdated_count}/{total_q})\n")
        f.write(f"- **Cases Requiring Human Review:** `{len(human_review_list)}`\n\n")

        f.write("## 2. Overall Performance Breakdown\n\n")
        f.write(f"- Substantially Correct (Score 2): `{correct_count}` ({correct_count/total_q*100:.1f}%)\n")
        f.write(f"- Partially Correct (Score 1): `{partial_count}` ({partial_count/total_q*100:.1f}%)\n")
        f.write(f"- Incorrect (Score 0): `{incorrect_count}` ({incorrect_count/total_q*100:.1f}%)\n\n")

        f.write("## 3. Category Performance\n\n")
        f.write("| Category | Questions | Correct | Partial | Incorrect | Hallucinations | Accuracy |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for c, tot, cor, par, inc, hal, acc in cat_stats:
            f.write(f"| {c} | {tot} | {cor} | {par} | {inc} | {hal} | {acc}% |\n")
        f.write("\n")

        f.write("## 4. Difficulty Performance\n\n")
        f.write("| Difficulty | Questions | Correct | Partial | Incorrect | Accuracy |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for d, tot, cor, par, inc, acc in diff_stats:
            f.write(f"| {d} | {tot} | {cor} | {par} | {inc} | {acc}% |\n")
        f.write("\n")

        f.write("## 5. Current-Law Performance\n\n")
        f.write(f"- **Total Criminal Law Questions:** `{sum(1 for r in results if r['category'] == 'Criminal Law')}`\n")
        f.write(f"- **Accurate Current/Transitional Law Citations:** `{sum(1 for r in results if r['category'] == 'Criminal Law' and r['current_law_score'] == 2)}`\n")
        f.write(f"- **Outdated Statute Citations Detected:** `{sum(1 for r in results if r['category'] == 'Criminal Law' and r['outdated_law_flag'] != 'false')}`\n\n")

        f.write("## 6. Hallucination Analysis\n\n")
        clear_hallucinations = [r for r in results if r["hallucination_flag"] == "clear"]
        if clear_hallucinations:
            for ch in clear_hallucinations:
                f.write(f"### Question [{ch['id']}]\n")
                f.write(f"- **Question:** {ch['question']}\n")
                f.write(f"- **Model Claim:** {ch['model_answer'][:250]}...\n")
                f.write(f"- **Expected Legal Position:** {ch['reference_answer'][:250]}...\n")
                f.write(f"- **Hallucination Diagnosis:** {ch['hallucination_reason']}\n\n")
        else:
            f.write("No clear hallucinations were detected during automated scoring.\n\n")

        f.write("## 7. Outdated-Law Analysis\n\n")
        outdated_items = [r for r in results if r["outdated_law_flag"] != "false"]
        if outdated_items:
            for oi in outdated_items:
                f.write(f"- **[{oi['id']}] {oi['question']}**: Cites legacy provisions without noting BNS/BNSS/BSA transition.\n")
        else:
            f.write("No problematic reliance on outdated criminal law was detected.\n\n")

        f.write("## 8. Sample Strongest Responses (Top 10)\n\n")
        for idx, item in enumerate(top_10, 1):
            f.write(f"### {idx}. [{item['id']}] ({item['category']} | Score: {item['total_score']}/11)\n")
            f.write(f"- **Question:** {item['question']}\n")
            f.write(f"- **Model Answer:** {item['model_answer'][:300]}...\n\n")

        f.write("## 9. Sample Weakest Responses (Bottom 10)\n\n")
        for idx, item in enumerate(bottom_10, 1):
            f.write(f"### {idx}. [{item['id']}] ({item['category']} | Score: {item['total_score']}/11)\n")
            f.write(f"- **Question:** {item['question']}\n")
            f.write(f"- **Model Answer:** {item['model_answer'][:300]}...\n")
            f.write(f"- **Review Reason:** {item['review_reasons']}\n\n")

    print(f"Saved evaluation report: {report_path}")

    with open(human_path, "w", encoding="utf-8") as f:
        f.write("# LegalAI v2 125-Question Benchmark: Human Review Required\n\n")
        f.write(f"**Total Records Flagged:** {len(human_review_list)}\n\n")
        for r in human_review_list:
            f.write(f"## [{r['id']}] {r['category']} (Difficulty: {r['difficulty']})\n\n")
            f.write(f"**Question:**\n{r['question']}\n\n")
            f.write(f"**Model Answer:**\n{r['model_answer']}\n\n")
            f.write(f"**Reference Answer:**\n{r['reference_answer']}\n\n")
            f.write(f"**Key Points:**\n")
            for kp in r.get("key_points", []):
                f.write(f"- {kp}\n")
            f.write(f"\n**Reason for Human Review:**\n{r['review_reasons']}\n\n")
            f.write("---\n\n")
    print(f"Saved human review file: {human_path}")


def main():
    parser = argparse.ArgumentParser(description="LegalAI v2 125-Question Automated Evaluation Harness.")
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL, help="Base model Hugging Face ID.")
    parser.add_argument("--adapter-dir", default=DEFAULT_ADAPTER_DIR, help="Path to LoRA adapter.")
    parser.add_argument("--eval-file", default=DEFAULT_EVAL_FILE, help="Path to held-out evaluation dataset.")
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR, help="Output directory for results.")
    parser.add_argument("--smoke-test", action="store_true", help="Run only first 5 questions for verification.")
    parser.add_argument("--max-questions", type=int, default=None, help="Limit number of questions to evaluate.")
    args = parser.parse_args()

    print(f"Loading evaluation dataset from: {args.eval_file}...")
    eval_records = load_evaluation_dataset(args.eval_file)
    print(f"Loaded {len(eval_records)} evaluation records.")

    model, tokenizer = load_model_and_tokenizer(
        base_model_path=args.base_model,
        adapter_path=args.adapter_dir,
    )

    if args.smoke_test:
        print("\n>>> RUNNING SMOKE TEST (First 5 questions only) <<<\n")
        results = run_evaluation(
            eval_records=eval_records,
            model=model,
            tokenizer=tokenizer,
            max_questions=5,
            smoke_test=True,
        )
        print("\n>>> SMOKE TEST COMPLETED SUCCESSFULLY <<<\n")
        return

    print(f"\n>>> RUNNING FULL BENCHMARK EVALUATION ({len(eval_records)} questions) <<<\n")
    results = run_evaluation(
        eval_records=eval_records,
        model=model,
        tokenizer=tokenizer,
        max_questions=args.max_questions,
        smoke_test=False,
    )

    save_results_v2(results, args.results_dir)
    generate_reports_v2(
        results=results,
        results_dir=args.results_dir,
        base_model_name=args.base_model,
        adapter_dir=args.adapter_dir,
        eval_filepath=args.eval_file,
    )
    print("\n>>> FULL V2 EVALUATION COMPLETE <<<")


if __name__ == "__main__":
    main()
