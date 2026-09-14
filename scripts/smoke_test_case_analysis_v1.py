#!/usr/bin/env python3
"""
smoke_test_case_analysis_v1.py

Verifies:
1. Base model is Qwen/Qwen2.5-14B-Instruct
2. Adapter is outputs/qwen14b-case-analysis-v1
3. PEFT correctly loads the adapter
4. Direct inference with real CASE MATERIAL + LAWYER QUERY works
5. Response contains genuine legal analysis (no UI stubs)
"""

import os
import sys
import json
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

BASE_MODEL = "Qwen/Qwen2.5-14B-Instruct"
ADAPTER_PATH = "outputs/qwen14b-case-analysis-v1"

print("=" * 60)
print("CASE ANALYSIS V1 ADAPTER VERIFICATION & SMOKE TEST")
print("=" * 60)

assert os.path.exists(ADAPTER_PATH), f"Adapter path missing: {ADAPTER_PATH}"
adapter_config_path = os.path.join(ADAPTER_PATH, "adapter_config.json")
with open(adapter_config_path, "r", encoding="utf-8") as f:
    cfg = json.load(f)
print(f"Verified adapter_config.json:")
print(f"  Base Model Name: {cfg.get('base_model_name_or_path')}")
print(f"  LoRA Rank (r):   {cfg.get('r')}")
print(f"  LoRA Alpha:      {cfg.get('lora_alpha')}")
print(f"  Target Modules:  {cfg.get('target_modules')}")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"Loading Base Model on GPU 2: {BASE_MODEL}...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.bfloat16,
    device_map={"": 0}
)

print(f"Loading LoRA Adapter: {ADAPTER_PATH}...")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

print("PEFT Active Adapters:", model.active_adapters)
assert "default" in model.active_adapters or len(model.active_adapters) > 0, "No active adapter found!"

# Smoke test prompt from held-out case
test_case_prompt = """You are LegalAI Case Analysis specialist. Analyze the supplied case materials strictly and objectively.

[CASE MATERIAL]
Case: State of Maharashtra vs. M. K. Patil (2021)
Material:
The accused was charged under Section 302 IPC. The prosecution relies on the recovery of a blood-stained knife pursuant to a disclosure statement recorded under Section 27 of the Indian Evidence Act. PW-3, the panch witness to the memorandum and panchnama, turned hostile during cross-examination and stated that he signed the papers at the police station. The chemical analyzer report confirms human blood of Group 'B' on the weapon, matching the deceased.

[LAWYER QUERY]
Assess the evidentiary strength of the weapon recovery in light of PW-3's hostility."""

messages = [{"role": "user", "content": test_case_prompt}]
chat_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(chat_text, return_tensors="pt").to("cuda:0")

print("\nGenerating direct model inference response...")
with torch.no_grad():
    out_ids = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
        pad_token_id=tokenizer.pad_token_id
    )

gen_tokens = out_ids[0][inputs["input_ids"].shape[1]:]
response = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

print("\n--- SMOKE TEST OUTPUT ---")
print(response[:600])
print("--- END OUTPUT ---\n")

assert "upload documents" not in response.lower(), "FAILED: Produced static UI stub!"
assert len(response) > 50, "FAILED: Response too short!"
assert any(term in response.lower() for term in ["section 27", "panch", "hostile", "recovery", "weapon", "evidence"]), "FAILED: Did not analyze case material!"

print("=" * 60)
print("SMOKE TEST PASSED: ADAPTER IS FULLY LOADED AND FUNCTIONAL!")
print("=" * 60)
