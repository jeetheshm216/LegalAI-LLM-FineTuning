#!/usr/bin/env python3
"""
train.py

Main fine-tuning entrypoint for LegalAI on NVIDIA B200 GPUs.
Fully compatible with:
  - Transformers 5.16.1
  - TRL 1.13.0 (using SFTConfig and processing_class=tokenizer)
  - PEFT 0.20.0 (LoRA)
  - PyTorch 2.11.0+cu128
"""

import argparse
import inspect
import logging
import os
import sys
from typing import Any, Dict

import yaml
import torch
from datasets import load_dataset
from peft import LoraConfig, TaskType
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    set_seed,
)
from trl import SFTConfig, SFTTrainer

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("LegalAI-Trainer")


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_lora_config(lora_cfg: Dict[str, Any]) -> LoraConfig:
    task_type_str = lora_cfg.get("task_type", "CAUSAL_LM")
    task_type = getattr(TaskType, task_type_str, TaskType.CAUSAL_LM)
    
    return LoraConfig(
        r=lora_cfg.get("r", 16),
        lora_alpha=lora_cfg.get("lora_alpha", 32),
        lora_dropout=lora_cfg.get("lora_dropout", 0.05),
        target_modules=lora_cfg.get("target_modules", [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ]),
        bias=lora_cfg.get("bias", "none"),
        task_type=task_type,
    )


def build_sft_config(
    training_cfg: Dict[str, Any],
    hardware_cfg: Dict[str, Any],
    logging_cfg: Dict[str, Any],
    data_cfg: Dict[str, Any],
    output_dir_override: str = None
) -> SFTConfig:
    output_dir = output_dir_override or training_cfg.get("output_dir", "outputs/legalai-lora-checkpoint")
    max_seq_length = data_cfg.get("max_seq_length", 2048)
    
    raw_kwargs = {
        "output_dir": output_dir,
        "num_train_epochs": float(training_cfg.get("num_train_epochs", 3.0)),
        "per_device_train_batch_size": int(training_cfg.get("per_device_train_batch_size", 4)),
        "per_device_eval_batch_size": int(training_cfg.get("per_device_eval_batch_size", 4)),
        "gradient_accumulation_steps": int(training_cfg.get("gradient_accumulation_steps", 4)),
        "learning_rate": float(training_cfg.get("learning_rate", 2e-4)),
        "lr_scheduler_type": training_cfg.get("lr_scheduler_type", "cosine"),
        "warmup_steps": int(training_cfg.get("warmup_steps", 10)),
        "weight_decay": float(training_cfg.get("weight_decay", 0.01)),
        "max_grad_norm": float(training_cfg.get("max_grad_norm", 1.0)),
        "bf16": hardware_cfg.get("bf16", True),
        "fp16": hardware_cfg.get("fp16", False),
        "gradient_checkpointing": hardware_cfg.get("gradient_checkpointing", True),
        "dataloader_num_workers": int(hardware_cfg.get("dataloader_num_workers", 2)),
        "logging_steps": int(logging_cfg.get("logging_steps", 5)),
        "report_to": logging_cfg.get("report_to", "none"),
        "eval_strategy": training_cfg.get("eval_strategy", "epoch"),
        "eval_steps": int(training_cfg.get("eval_steps", 100)),
        "save_strategy": training_cfg.get("save_strategy", "epoch"),
        "save_steps": int(training_cfg.get("save_steps", 100)),
        "save_total_limit": int(training_cfg.get("save_total_limit", 2)),
        "load_best_model_at_end": training_cfg.get("load_best_model_at_end", False),
        "max_length": max_seq_length,
        "dataset_text_field": None,
    }
    
    sig = inspect.signature(SFTConfig.__init__)
    filtered_kwargs = {k: v for k, v in raw_kwargs.items() if k in sig.parameters}
    
    return SFTConfig(**filtered_kwargs)


def run_dry_run_validation(config: Dict[str, Any], config_path: str):
    logger.info("=" * 65)
    logger.info("STARTING LEGALAI SFT PRE-FLIGHT DRY-RUN VERIFICATION")
    logger.info("=" * 65)
    
    # 1. Environment & Hardware Verification
    logger.info("[1/5] Checking Hardware and Execution Environment...")
    cuda_avail = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if cuda_avail else 0
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU"
    logger.info(f"  CUDA Available: {cuda_avail}")
    logger.info(f"  GPU Count:      {gpu_count}")
    logger.info(f"  Primary Device: {device_name}")
    logger.info(f"  BF16 Supported: {torch.cuda.is_bf16_supported() if cuda_avail else False}")
    logger.info(f"  TRL Installed:  True (SFTConfig & SFTTrainer verified)")
    
    # 2. Config Verification
    logger.info(f"[2/5] Validating Configuration ({config_path})...")
    model_cfg = config.get("model", {})
    data_cfg = config.get("data", {})
    lora_cfg = config.get("lora", {})
    train_cfg = config.get("training", {})
    hw_cfg = config.get("hardware", {})
    log_cfg = config.get("logging", {})
    
    model_name = model_cfg.get("model_name_or_path", "unspecified")
    logger.info(f"  Configured Model:    {model_name}")
    logger.info(f"  Target Precision:    {model_cfg.get('torch_dtype', 'bfloat16')}")
    logger.info(f"  Context Window:      {data_cfg.get('max_seq_length', 2048)}")

    # 3. Dataset Verification
    logger.info("[3/5] Verifying Dataset Files...")
    train_file = data_cfg.get("train_file", "data/legal_train.jsonl")
    val_file = data_cfg.get("validation_file", "data/legal_validation.jsonl")
    
    if not os.path.exists(train_file):
        raise FileNotFoundError(f"Training dataset missing: {train_file}")
    if not os.path.exists(val_file):
        raise FileNotFoundError(f"Validation dataset missing: {val_file}")
        
    raw_dataset = load_dataset("json", data_files={"train": train_file, "validation": val_file})
    logger.info(f"  Train Records:       {len(raw_dataset['train'])}")
    logger.info(f"  Validation Records:  {len(raw_dataset['validation'])}")
    logger.info(f"  Columns:             {raw_dataset['train'].column_names}")
    
    # 4. LoRA Configuration Verification
    logger.info("[4/5] Initializing PEFT LoRA Configuration...")
    peft_config = build_lora_config(lora_cfg)
    logger.info(f"  LoRA Rank (r):       {peft_config.r}")
    logger.info(f"  LoRA Alpha:          {peft_config.lora_alpha}")
    logger.info(f"  Target Modules:      {peft_config.target_modules}")
    logger.info(f"  LoRA Dropout:        {peft_config.lora_dropout}")
    
    # 5. SFTConfig Verification (TRL 1.x)
    logger.info("[5/5] Building TRL SFTConfig Object...")
    sft_args = build_sft_config(train_cfg, hw_cfg, log_cfg, data_cfg)
    logger.info(f"  Output Directory:    {sft_args.output_dir}")
    logger.info(f"  Epochs:              {sft_args.num_train_epochs}")
    logger.info(f"  Per-Device Batch:    {sft_args.per_device_train_batch_size}")
    logger.info(f"  Grad Accumulation:   {sft_args.gradient_accumulation_steps}")
    logger.info(f"  Learning Rate:       {sft_args.learning_rate}")
    logger.info(f"  BF16 Enabled:        {sft_args.bf16}")
    logger.info(f"  Grad Checkpointing:  {sft_args.gradient_checkpointing}")
    logger.info(f"  Max Sequence Length: {sft_args.max_length}")
    logger.info(f"  SFTTrainer Target:   processing_class=tokenizer (TRL 1.x)")
    
    logger.info("=" * 65)
    logger.info("DRY-RUN VERIFICATION SUCCESSFUL — ALL PRE-CONDITIONS MET")
    logger.info("No model was downloaded and no training was executed.")
    logger.info("=" * 65)


def train(config: Dict[str, Any], config_path: str, output_dir_override: str = None):
    model_cfg = config.get("model", {})
    data_cfg = config.get("data", {})
    lora_cfg = config.get("lora", {})
    train_cfg = config.get("training", {})
    hw_cfg = config.get("hardware", {})
    log_cfg = config.get("logging", {})

    set_seed(train_cfg.get("seed", 42))

    model_id = model_cfg.get("model_name_or_path")
    logger.info(f"Loading tokenizer for: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype_str = model_cfg.get("torch_dtype", "bfloat16")
    torch_dtype = getattr(torch, dtype_str, torch.bfloat16)

    logger.info(f"Loading base model in {torch_dtype}: {model_id}")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )

    peft_config = build_lora_config(lora_cfg)
    sft_args = build_sft_config(train_cfg, hw_cfg, log_cfg, data_cfg, output_dir_override)

    train_file = data_cfg.get("train_file")
    val_file = data_cfg.get("validation_file")
    dataset = load_dataset("json", data_files={"train": train_file, "validation": val_file})

    logger.info("Initializing TRL SFTTrainer (TRL 1.x processing_class=tokenizer)...")
    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=peft_config,
        processing_class=tokenizer,
    )

    logger.info("Starting training execution...")
    trainer.train()

    logger.info(f"Saving final adapter weights to: {sft_args.output_dir}")
    trainer.save_model(sft_args.output_dir)
    tokenizer.save_pretrained(sft_args.output_dir)
    logger.info("Training complete.")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune LegalAI models using LoRA/SFT.")
    parser.add_argument("--config", default="configs/sft_config.yaml", help="Path to SFT configuration YAML.")
    parser.add_argument("--dry-run", action="store_true", help="Perform pre-flight verification without training.")
    parser.add_argument("--output-dir", default=None, help="Optional override for checkpoint output directory.")
    args = parser.parse_args()

    config = load_yaml_config(args.config)
    
    if args.dry_run:
        run_dry_run_validation(config, args.config)
        return

    train(config, args.config, args.output_dir)


if __name__ == "__main__":
    main()
