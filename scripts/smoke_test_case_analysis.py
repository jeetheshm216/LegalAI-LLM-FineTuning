#!/usr/bin/env python3
"""
smoke_test_case_analysis.py

Direct isolated case-analysis inference path.
Verifies that:
1. Model directly receives CASE MATERIAL and LAWYER QUERY
2. Generation produces substantive legal analysis and NOT the static UI stub
"""

import os
import sys
import json
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

BASE_MODEL = "Qwen/Qwen2.5-14B-Instruct"
ADAPTER_PATH = "outputs/qwen14b-legalai-v2"
TEST_FILE = "data/case_analysis/case_analysis_test.jsonl"

print("=" * 60)
print("LEGALAI CASE ANALYSIS — DIRECT INFERENCE SMOKE TEST")
print("=" * 60)

# Load 1 held-out test item
with open(TEST_FILE, "r", encoding="utf-8") as f:
    sample_record = json.loads(f.readline())

print(f"Loaded sample test record: {sample_record['id']} ({sample_record['task_type']})")
print(f"Case ID: {sample_record['case_id']}")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
print(f"Loading base model: {BASE_MODEL}...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.bfloat16,
    device_map={"": 0}
)

if os.path.exists(ADAPTER_PATH):
    print(f"Loading adapter from: {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
else:
    model = base_model

model.eval()

# Format chat template directly using messages from test item
messages = sample_record["messages"]
# Pass user message (which contains CASE MATERIAL + LAWYER QUERY)
user_prompt = messages[0]["content"]
chat_formatted = tokenizer.apply_chat_template(
    [{"role": "user", "content": user_prompt}],
    tokenize=False,
    add_generation_prompt=True
)

print(f"Rendered Prompt Length: {len(chat_formatted)} characters")
print("Prompt Snippet:")
print("-" * 40)
print(chat_formatted[:300] + "\n...")
print("-" * 40)

inputs = tokenizer(chat_formatted, return_tensors="pt").to("cuda:0")

with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
        temperature=None,
        top_p=None,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
    )

gen_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
response_text = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

print("\nGENERATED RESPONSE:")
print("-" * 40)
print(response_text)
print("-" * 40)

# Verify smoke test assertions
stub_phrases = [
    "Please upload documents",
    "You are inquiring about specific case matter",
    "please select an active matter"
]
is_stub = any(phrase.lower() in response_text.lower() for phrase in stub_phrases)
assert not is_stub, f"SMOKE TEST FAILED: Output contained static guidance stub: {response_text}"
assert len(response_text) > 50, f"SMOKE TEST FAILED: Output was empty or too short: {response_text}"

print("\n" + "=" * 60)
print("SMOKE TEST PASSED! DIRECT INFERENCE PATH IS OPERATIONAL.")
print("The model directly processes the supplied CASE MATERIAL and LAWYER QUERY.")
print("=" * 60)
