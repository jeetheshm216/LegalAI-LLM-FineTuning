#!/usr/bin/env python3
"""
prepare_dataset.py

Loads, validates, and inspects the conversational SFT dataset for LegalAI.
Verifies messages structure, valid roles (user/assistant), and computes
character/token length statistics without altering the source JSONL files.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple
from datasets import Dataset, DatasetDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_TRAIN = os.path.join(PROJECT_DIR, "data", "legal_train.jsonl")
DEFAULT_VAL = os.path.join(PROJECT_DIR, "data", "legal_validation.jsonl")

VALID_ROLES = {"user", "assistant"}


def validate_record(record: Dict, line_num: int, split_name: str) -> Tuple[bool, str]:
    if "messages" not in record:
        return False, f"[{split_name}:{line_num}] Missing 'messages' field"
    messages = record["messages"]
    if not isinstance(messages, list) or len(messages) < 2:
        return False, f"[{split_name}:{line_num}] 'messages' must be a list with at least 2 turns"
    
    roles = []
    for turn in messages:
        if not isinstance(turn, dict):
            return False, f"[{split_name}:{line_num}] Turn is not a JSON object"
        role = turn.get("role")
        content = turn.get("content")
        if role not in VALID_ROLES:
            return False, f"[{split_name}:{line_num}] Invalid role: {role}"
        if not content or not isinstance(content, str) or not content.strip():
            return False, f"[{split_name}:{line_num}] Empty content for role: {role}"
        roles.append(role)
    
    if "user" not in roles:
        return False, f"[{split_name}:{line_num}] No user turn found"
    if "assistant" not in roles:
        return False, f"[{split_name}:{line_num}] No assistant turn found"
        
    return True, ""


def load_and_validate_split(filepath: str, split_name: str) -> List[Dict]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{split_name} file not found: {filepath}")
    
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"[{split_name}:{idx}] JSON parse error: {e}")
            
            valid, err = validate_record(rec, idx, split_name)
            if not valid:
                raise ValueError(err)
            records.append(rec)
            
    return records


def compute_char_stats(records: List[Dict]) -> Dict[str, float]:
    user_lens = []
    assistant_lens = []
    total_lens = []
    for r in records:
        u_len = sum(len(m["content"]) for m in r["messages"] if m["role"] == "user")
        a_len = sum(len(m["content"]) for m in r["messages"] if m["role"] == "assistant")
        user_lens.append(u_len)
        assistant_lens.append(a_len)
        total_lens.append(u_len + a_len)
    
    return {
        "avg_user_chars": round(sum(user_lens) / len(user_lens), 1) if user_lens else 0,
        "avg_assistant_chars": round(sum(assistant_lens) / len(assistant_lens), 1) if assistant_lens else 0,
        "avg_total_chars": round(sum(total_lens) / len(total_lens), 1) if total_lens else 0,
        "min_total_chars": min(total_lens) if total_lens else 0,
        "max_total_chars": max(total_lens) if total_lens else 0,
    }


def prepare_dataset(train_path: str, val_path: str) -> Tuple[DatasetDict, List[Dict], List[Dict]]:
    train_records = load_and_validate_split(train_path, "train")
    val_records = load_and_validate_split(val_path, "validation")
    
    ds_train = Dataset.from_list(train_records)
    ds_val = Dataset.from_list(val_records)
    
    hf_dataset = DatasetDict({
        "train": ds_train,
        "validation": ds_val
    })
    
    return hf_dataset, train_records, val_records


def main():
    parser = argparse.ArgumentParser(description="Validate and prepare LegalAI SFT dataset.")
    parser.add_argument("--train", default=DEFAULT_TRAIN, help="Path to legal_train.jsonl")
    parser.add_argument("--validation", default=DEFAULT_VAL, help="Path to legal_validation.jsonl")
    args = parser.parse_args()

    print("=" * 65)
    print("LegalAI SFT Dataset Preparation & Verification")
    print("=" * 65)

    hf_dataset, train_recs, val_recs = prepare_dataset(args.train, args.validation)
    
    print("\n[OK] Validation passed for all records.")
    print(f"  Training examples:   {len(hf_dataset['train'])}")
    print(f"  Validation examples: {len(hf_dataset['validation'])}")
    print(f"  Features:            {hf_dataset['train'].column_names}")

    train_stats = compute_char_stats(train_recs)
    val_stats = compute_char_stats(val_recs)
    
    print("\n--- Length Statistics (Characters) ---")
    print(f"  Train: avg total={train_stats['avg_total_chars']}, avg user={train_stats['avg_user_chars']}, avg assistant={train_stats['avg_assistant_chars']}")
    print(f"         min={train_stats['min_total_chars']}, max={train_stats['max_total_chars']}")
    print(f"  Val:   avg total={val_stats['avg_total_chars']}, avg user={val_stats['avg_user_chars']}, avg assistant={val_stats['avg_assistant_chars']}")
    print(f"         min={val_stats['min_total_chars']}, max={val_stats['max_total_chars']}")

    print("\n--- Sample Formatted Conversation (Train #1) ---")
    sample = hf_dataset["train"][0]["messages"]
    for turn in sample:
        role_label = turn["role"].upper()
        content = turn["content"]
        print(f"[{role_label}]: {content}\n")

    print("=" * 65)
    print("Dataset is structurally valid and ready for Hugging Face SFT.")
    print("=" * 65)


if __name__ == "__main__":
    main()
