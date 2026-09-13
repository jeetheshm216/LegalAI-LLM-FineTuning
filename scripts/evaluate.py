#!/usr/bin/env python3
"""
evaluate.py

Evaluation framework for fine-tuned LegalAI models.
Loads Qwen2.5-14B-Instruct base model + LoRA adapter weights, evaluates against
held-out validation datasets (legal_validation.jsonl), generates grounded answers
using Qwen's native chat template, and computes generation outputs.
Includes pre-flight check mode without requiring model weight downloads.
"""

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List

import torch
import yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("LegalAI-Evaluator")

DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-14B-Instruct"
DEFAULT_ADAPTER_DIR = "outputs/qwen14b-first-run-checkpoint"
DEFAULT_EVAL_FILE = "data/legal_validation.jsonl"


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def load_eval_data(val_filepath: str) -> List[Dict]:
    if not os.path.exists(val_filepath):
        raise FileNotFoundError(f"Evaluation file not found: {val_filepath}")
    records = []
    with open(val_filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def dry_run_check(args):
    logger.info("=" * 65)
    logger.info("LEGALAI EVALUATION SCRIPT — PRE-FLIGHT CHECK")
    logger.info("=" * 65)
    
    base_model = args.base_model or DEFAULT_BASE_MODEL
    logger.info(f"Base model target:       {base_model}")
    logger.info(f"LoRA adapter target:     {args.adapter_dir}")
    logger.info(f"Evaluation dataset:      {args.eval_file}")
    
    if os.path.exists(args.eval_file):
        data = load_eval_data(args.eval_file)
        logger.info(f"[OK] Evaluation dataset found: {len(data)} examples")
        # Check sample turn structure
        if data and "messages" in data[0]:
            sample_msgs = data[0]["messages"]
            logger.info(f"[OK] Sample turn roles: {[m.get('role') for m in sample_msgs]}")
    else:
        logger.warning(f"[WARN] Evaluation dataset not found at {args.eval_file}")
        
    logger.info(f"Output destination:      {args.output_file}")
    logger.info(f"CUDA Available:          {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"Primary Device [0]:      {torch.cuda.get_device_name(0)}")
        logger.info(f"BF16 Supported:          {torch.cuda.is_bf16_supported()}")
    logger.info("=" * 65)
    logger.info("PRE-FLIGHT CHECK COMPLETED — Ready for post-training evaluation.")
    logger.info("=" * 65)


def run_evaluation(args):
    base_model = args.base_model or DEFAULT_BASE_MODEL
    adapter_dir = args.adapter_dir

    if not adapter_dir or not os.path.exists(adapter_dir):
        logger.warning(f"Adapter directory '{adapter_dir}' does not exist yet. Running evaluation on base model.")

    logger.info(f"Loading Qwen tokenizer for: {base_model}")
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info(f"Loading base model in BF16: {base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )

    if adapter_dir and os.path.exists(adapter_dir):
        logger.info(f"Attaching LoRA adapter from: {adapter_dir}")
        model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()

    eval_data = load_eval_data(args.eval_file)
    logger.info(f"Evaluating {len(eval_data)} samples from {args.eval_file}...")

    results = []
    for idx, item in enumerate(eval_data, start=1):
        messages = item.get("messages", [])
        prompt_messages = [m for m in messages if m["role"] != "assistant"]
        gold_answer = next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
        user_query = next((m["content"] for m in prompt_messages if m["role"] == "user"), "")

        # Format with native Qwen chat template
        if hasattr(tokenizer, "apply_chat_template"):
            input_ids = tokenizer.apply_chat_template(
                prompt_messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(model.device)
        else:
            prompt_str = "\n".join(f"{m['role']}: {m['content']}" for m in prompt_messages) + "\nassistant:"
            input_ids = tokenizer(prompt_str, return_tensors="pt")["input_ids"].to(model.device)

        input_len = input_ids.shape[1]

        with torch.no_grad():
            output_tokens = model.generate(
                input_ids,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                do_sample=args.temperature > 0.0,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        generated_tokens = output_tokens[0][input_len:]
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        results.append({
            "id": idx,
            "query": user_query,
            "gold_answer": gold_answer,
            "generated_answer": generated_text,
        })
        if idx % 25 == 0 or idx == len(eval_data):
            logger.info(f"Evaluated [{idx}/{len(eval_data)}] samples")

    os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved evaluation results to: {args.output_file}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned LegalAI models.")
    parser.add_argument("--config", default="configs/sft_first_run.yaml", help="Path to SFT configuration YAML.")
    parser.add_argument("--base-model", default=None, help="Hugging Face base model name or path.")
    parser.add_argument("--adapter-dir", default=None, help="Directory containing fine-tuned LoRA adapter.")
    parser.add_argument("--eval-file", default=DEFAULT_EVAL_FILE, help="Validation JSONL file.")
    parser.add_argument("--output-file", default="outputs/eval_results.json", help="Destination file for results.")
    parser.add_argument("--max-new-tokens", type=int, default=512, help="Maximum generated tokens.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Generation temperature.")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup without downloading or loading models.")
    args = parser.parse_args()

    # If config file is available, resolve defaults from config
    cfg = load_yaml_config(args.config)
    if args.base_model is None:
        args.base_model = cfg.get("model", {}).get("model_name_or_path", DEFAULT_BASE_MODEL)
    if args.adapter_dir is None:
        args.adapter_dir = cfg.get("training", {}).get("output_dir", DEFAULT_ADAPTER_DIR)

    if args.dry_run:
        dry_run_check(args)
    else:
        run_evaluation(args)


if __name__ == "__main__":
    main()
