#!/usr/bin/env python3
"""
validate_legal_dataset.py

Validates the LegalAI JSONL dataset files (train + validation) for structural
correctness and basic quality issues. Prints a clear report and exits with a
non-zero status code if any hard errors are found.

Usage:
    python validate_legal_dataset.py
    python validate_legal_dataset.py --train data/legal_train.jsonl --validation data/legal_validation.jsonl
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TRAIN = os.path.join(SCRIPT_DIR, "data", "legal_train.jsonl")
DEFAULT_VAL = os.path.join(SCRIPT_DIR, "data", "legal_validation.jsonl")

MIN_ANSWER_CHARS = 40
MAX_ANSWER_CHARS = 4000
VALID_ROLES = {"user", "assistant"}


def normalize_question(q: str) -> str:
    q = q.lower().strip()
    q = re.sub(r"[^a-z0-9\s]", "", q)
    q = re.sub(r"\s+", " ", q)
    return q


def load_lines(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def is_valid_unicode(s: str) -> bool:
    try:
        s.encode("utf-8").decode("utf-8")
        return True
    except UnicodeError:
        return False


def validate_file(path: str, label: str) -> Tuple[List[Dict], List[str], List[str]]:
    """Returns (parsed_records, errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []
    records: List[Dict] = []

    lines = load_lines(path)
    if not lines:
        errors.append(f"[{label}] File missing or empty: {path}")
        return records, errors, warnings

    seen_questions_norm = set()

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            warnings.append(f"[{label}] Line {i}: blank line (skipped).")
            continue

        # 1. Valid JSON
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"[{label}] Line {i}: invalid JSON ({e}).")
            continue

        # Check for duplicate keys is implicit in json.loads (last key wins);
        # do a raw check for repeated top-level keys as a heuristic.
        if line.count('"messages"') > 1:
            errors.append(f"[{label}] Line {i}: possible duplicate 'messages' key.")

        # 2. Has 'messages'
        if "messages" not in obj:
            errors.append(f"[{label}] Line {i}: missing 'messages' field.")
            continue

        messages = obj["messages"]
        if not isinstance(messages, list) or len(messages) < 2:
            errors.append(f"[{label}] Line {i}: 'messages' must be a list with at least a user and assistant turn.")
            continue

        roles_present = [m.get("role") for m in messages]

        # 3 & 4. Has user and assistant message
        if "user" not in roles_present:
            errors.append(f"[{label}] Line {i}: no 'user' message found.")
        if "assistant" not in roles_present:
            errors.append(f"[{label}] Line {i}: no 'assistant' message found.")

        # 5. Roles valid
        for m in messages:
            role = m.get("role")
            if role not in VALID_ROLES:
                errors.append(f"[{label}] Line {i}: invalid role '{role}'.")

        user_msgs = [m for m in messages if m.get("role") == "user"]
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]

        user_content = user_msgs[0].get("content", "") if user_msgs else ""
        assistant_content = assistant_msgs[-1].get("content", "") if assistant_msgs else ""

        # 6. Messages non-empty
        if not user_content or not user_content.strip():
            errors.append(f"[{label}] Line {i}: empty user message.")
        if not assistant_content or not assistant_content.strip():
            errors.append(f"[{label}] Line {i}: empty assistant message.")

        # 9. Broken unicode
        if not is_valid_unicode(user_content) or not is_valid_unicode(assistant_content):
            errors.append(f"[{label}] Line {i}: invalid/broken unicode detected.")

        # 10 & 11. Extremely short / long answers
        if assistant_content and len(assistant_content) < MIN_ANSWER_CHARS:
            warnings.append(
                f"[{label}] Line {i}: assistant answer is very short ({len(assistant_content)} chars)."
            )
        if assistant_content and len(assistant_content) > MAX_ANSWER_CHARS:
            warnings.append(
                f"[{label}] Line {i}: assistant answer is very long ({len(assistant_content)} chars)."
            )

        # 7. Duplicate questions within this file
        norm = normalize_question(user_content)
        if norm in seen_questions_norm:
            errors.append(f"[{label}] Line {i}: duplicate question within {label} set.")
        else:
            seen_questions_norm.add(norm)

        if not errors or errors[-1].split(":")[0] != f"[{label}] Line {i}":
            records.append(obj)

    return records, errors, warnings


def check_cross_split_overlap(train_records: List[Dict], val_records: List[Dict]) -> List[str]:
    errors = []

    def question_of(obj: Dict) -> str:
        for m in obj.get("messages", []):
            if m.get("role") == "user":
                return normalize_question(m.get("content", ""))
        return ""

    train_qs = {question_of(r) for r in train_records}
    val_qs = {question_of(r) for r in val_records}

    overlap = train_qs & val_qs
    if overlap:
        errors.append(
            f"[cross-split] {len(overlap)} question(s) appear in BOTH train and validation sets."
        )
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate the LegalAI JSONL dataset.")
    parser.add_argument("--train", default=DEFAULT_TRAIN)
    parser.add_argument("--validation", default=DEFAULT_VAL)
    args = parser.parse_args()

    print("=" * 70)
    print("LegalAI Dataset Validation Report")
    print("=" * 70)

    train_records, train_errors, train_warnings = validate_file(args.train, "train")
    val_records, val_errors, val_warnings = validate_file(args.validation, "validation")

    cross_errors = check_cross_split_overlap(train_records, val_records) if train_records and val_records else []

    all_errors = train_errors + val_errors + cross_errors
    all_warnings = train_warnings + val_warnings

    print(f"\nTrain file:      {args.train}")
    print(f"  Valid records parsed: {len(train_records)}")
    print(f"Validation file: {args.validation}")
    print(f"  Valid records parsed: {len(val_records)}")

    print(f"\nErrors found:   {len(all_errors)}")
    for e in all_errors:
        print(f"  ERROR: {e}")

    print(f"\nWarnings found: {len(all_warnings)}")
    for w in all_warnings:
        print(f"  WARN:  {w}")

    print("\n" + "-" * 70)
    if all_errors:
        print(f"RESULT: FAILED — {len(all_errors)} error(s) must be fixed.")
        sys.exit(1)
    else:
        print("RESULT: PASSED — no structural errors found.")
        if all_warnings:
            print(f"        ({len(all_warnings)} warning(s) noted above for review.)")
        sys.exit(0)


if __name__ == "__main__":
    main()
