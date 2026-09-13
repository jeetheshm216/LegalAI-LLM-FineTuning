#!/usr/bin/env python3
"""
dataset_stats.py

Prints summary statistics for the LegalAI dataset: sizes, length distributions,
question-type / domain / difficulty distributions, and duplicate counts.

Reads the .meta.jsonl side-car files (written by generate_legal_dataset.py)
for domain/type/difficulty info, and the .jsonl files themselves for the
actual message content and lengths. Falls back gracefully if meta files
are absent (still reports length-based stats and duplicate counts).

Usage:
    python dataset_stats.py
"""

import argparse
import json
import os
import re
from collections import Counter
from typing import Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TRAIN = os.path.join(SCRIPT_DIR, "data", "legal_train.jsonl")
DEFAULT_VAL = os.path.join(SCRIPT_DIR, "data", "legal_validation.jsonl")
DEFAULT_TRAIN_META = os.path.join(SCRIPT_DIR, "data", "legal_train.meta.jsonl")
DEFAULT_VAL_META = os.path.join(SCRIPT_DIR, "data", "legal_validation.meta.jsonl")


def normalize_question(q: str) -> str:
    q = q.lower().strip()
    q = re.sub(r"[^a-z0-9\s]", "", q)
    q = re.sub(r"\s+", " ", q)
    return q


def load_jsonl(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def extract_qa(records: List[Dict]):
    questions, answers = [], []
    for r in records:
        msgs = r.get("messages", [])
        q = next((m.get("content", "") for m in msgs if m.get("role") == "user"), "")
        a = next((m.get("content", "") for m in reversed(msgs) if m.get("role") == "assistant"), "")
        questions.append(q)
        answers.append(a)
    return questions, answers


def count_duplicates(questions: List[str]) -> int:
    norm = [normalize_question(q) for q in questions]
    counts = Counter(norm)
    return sum(c - 1 for c in counts.values() if c > 1)


def summarize_lengths(strings: List[str]):
    lengths = [len(s) for s in strings if s]
    if not lengths:
        return {"avg": 0, "min": 0, "max": 0}
    return {
        "avg": round(sum(lengths) / len(lengths), 1),
        "min": min(lengths),
        "max": max(lengths),
    }


def distribution(meta_records: List[Dict], field: str) -> Counter:
    return Counter(m.get(field, "unknown") for m in meta_records)


def print_distribution(title: str, counter: Counter, total: int):
    print(f"\n{title}:")
    if not counter:
        print("  (no metadata available)")
        return
    for key, count in counter.most_common():
        pct = (count / total * 100) if total else 0
        print(f"  {key:35s} {count:4d}  ({pct:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Print statistics for the LegalAI dataset.")
    parser.add_argument("--train", default=DEFAULT_TRAIN)
    parser.add_argument("--validation", default=DEFAULT_VAL)
    parser.add_argument("--train-meta", default=DEFAULT_TRAIN_META)
    parser.add_argument("--val-meta", default=DEFAULT_VAL_META)
    args = parser.parse_args()

    train_records = load_jsonl(args.train)
    val_records = load_jsonl(args.validation)
    train_meta = load_jsonl(args.train_meta)
    val_meta = load_jsonl(args.val_meta)

    train_q, train_a = extract_qa(train_records)
    val_q, val_a = extract_qa(val_records)

    all_q = train_q + val_q
    all_a = train_a + val_a
    all_meta = train_meta + val_meta

    total = len(train_records) + len(val_records)

    print("=" * 70)
    print("LegalAI Dataset Statistics")
    print("=" * 70)

    print(f"\nTotal examples:      {total}")
    print(f"Training examples:   {len(train_records)}")
    print(f"Validation examples: {len(val_records)}")

    q_len = summarize_lengths(all_q)
    a_len = summarize_lengths(all_a)

    print(f"\nQuestion length (chars): avg={q_len['avg']}, min={q_len['min']}, max={q_len['max']}")
    print(f"Answer length (chars):   avg={a_len['avg']}, min={a_len['min']}, max={a_len['max']}")

    dup_train = count_duplicates(train_q)
    dup_val = count_duplicates(val_q)
    dup_cross = 0
    if train_q and val_q:
        norm_train = set(normalize_question(q) for q in train_q)
        norm_val = set(normalize_question(q) for q in val_q)
        dup_cross = len(norm_train & norm_val)

    print(f"\nDuplicate questions within train:      {dup_train}")
    print(f"Duplicate questions within validation: {dup_val}")
    print(f"Questions overlapping train/validation: {dup_cross}")

    if all_meta:
        print_distribution("Question-type distribution", distribution(all_meta, "question_type"), total)
        print_distribution("Legal-domain distribution", distribution(all_meta, "domain"), total)
        print_distribution("Difficulty distribution", distribution(all_meta, "difficulty"), total)
    else:
        print("\n(No metadata side-car files found — skipping type/domain/difficulty breakdowns.)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
