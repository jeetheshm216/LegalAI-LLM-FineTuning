#!/usr/bin/env python3
"""
scripts/test_trainer_init.py

Safe verification script that tests complete SFTTrainer initialization
with Qwen2.5-14B-Instruct, LoRA configuration, dataset, and SFTConfig
WITHOUT executing trainer.train().
"""

import argparse
import logging
import os
import sys
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from trl import SFTTrainer

# Import helper functions from existing train.py
from train import load_yaml_config, build_lora_config, build_sft_config

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("LegalAI-TrainerInitTest")


def test_init(config_path: str):
    logger.info("=" * 65)
    logger.info("TESTING SFTTRAINER INITIALIZATION (NO TRAINING)")
    logger.info("=" * 65)
    
    config = load_yaml_config(config_path)
    model_cfg = config.get("model", {})
    data_cfg = config.get("data", {})
    lora_cfg = config.get("lora", {})
    train_cfg = config.get("training", {})
    hw_cfg = config.get("hardware", {})
    log_cfg = config.get("logging", {})

    set_seed(train_cfg.get("seed", 42))

    model_id = model_cfg.get("model_name_or_path")
    logger.info(f"Loading tokenizer: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        if "<|endoftext|>" in tokenizer.get_vocab():
            tokenizer.pad_token = "<|endoftext|>"
        else:
            tokenizer.pad_token = tokenizer.eos_token

    dtype_str = model_cfg.get("torch_dtype", "bfloat16")
    torch_dtype = getattr(torch, dtype_str, torch.bfloat16)

    logger.info(f"Loading model in {torch_dtype}: {model_id}")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )

    logger.info("Building LoRA config...")
    peft_config = build_lora_config(lora_cfg)

    logger.info("Building SFTConfig...")
    sft_args = build_sft_config(train_cfg, hw_cfg, log_cfg, data_cfg)

    train_file = data_cfg.get("train_file")
    val_file = data_cfg.get("validation_file")
    logger.info(f"Loading datasets: {train_file}, {val_file}")
    dataset = load_dataset("json", data_files={"train": train_file, "validation": val_file})

    logger.info("Instantiating SFTTrainer (TRL 1.x)...")
    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=peft_config,
        processing_class=tokenizer,
    )

    logger.info("=" * 65)
    logger.info("SUCCESS: SFTTrainer initialized successfully without error!")
    logger.info("No training was started (trainer.train() was NOT called).")
    logger.info("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Test SFTTrainer initialization.")
    parser.add_argument("--config", default="configs/sft_first_run.yaml", help="Path to YAML config.")
    args = parser.parse_args()

    test_init(args.config)


if __name__ == "__main__":
    main()
