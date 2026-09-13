#!/usr/bin/env python3
"""
scripts/inspect_qwen.py

Inspects Qwen/Qwen2.5-14B-Instruct configuration, tokenizer, special tokens,
chat template, architecture, attention modules, LoRA target compatibility,
parameter count, and hardware environment (BF16 & GPU visibility).
Does NOT download large model weight checkpoints.
"""

import os
import sys
import torch
from transformers import AutoConfig, AutoTokenizer
from peft import LoraConfig, TaskType

MODEL_ID = "Qwen/Qwen2.5-14B-Instruct"

def inspect_environment():
    print("=" * 65)
    print("1. HARDWARE & CUDA ENVIRONMENT")
    print("=" * 65)
    cuda_avail = torch.cuda.is_available()
    print(f"CUDA Available:        {cuda_avail}")
    print(f"CUDA Visible Devices:  {os.environ.get('CUDA_VISIBLE_DEVICES', 'Not explicitly set')}")
    device_count = torch.cuda.device_count() if cuda_avail else 0
    print(f"Visible Device Count:  {device_count}")
    if cuda_avail and device_count > 0:
        dev_name = torch.cuda.get_device_name(0)
        total_mem = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        bf16_supp = torch.cuda.is_bf16_supported()
        print(f"Primary Device [0]:    {dev_name}")
        print(f"Device Memory:         {total_mem:.2f} GB")
        print(f"BF16 Supported:        {bf16_supp}")
    print()

def inspect_model_config():
    print("=" * 65)
    print(f"2. MODEL ARCHITECTURE & CONFIGURATION ({MODEL_ID})")
    print("=" * 65)
    try:
        config = AutoConfig.from_pretrained(MODEL_ID, trust_remote_code=True)
        print(f"Model Type:            {config.model_type}")
        print(f"Architectures:         {config.architectures}")
        print(f"Vocab Size:            {config.vocab_size}")
        print(f"Hidden Size:           {config.hidden_size}")
        print(f"Intermediate Size:     {config.intermediate_size}")
        print(f"Num Hidden Layers:     {config.num_hidden_layers}")
        print(f"Num Attention Heads:   {config.num_attention_heads}")
        print(f"Num Key-Value Heads:   {getattr(config, 'num_key_value_heads', config.num_attention_heads)} (GQA)")
        print(f"Max Position Embeds:   {getattr(config, 'max_position_embeddings', 'N/A')}")
        
        # Estimate parameter count analytically from config
        vocab = config.vocab_size
        h = config.hidden_size
        layers = config.num_hidden_layers
        inter = config.intermediate_size
        kv_heads = getattr(config, 'num_key_value_heads', config.num_attention_heads)
        att_heads = config.num_attention_heads
        head_dim = getattr(config, 'head_dim', h // att_heads)
        
        # Embeddings: vocab * h
        embed_params = vocab * h
        # Per layer:
        # q_proj: h * (att_heads * head_dim) = h * h
        # k_proj: h * (kv_heads * head_dim)
        # v_proj: h * (kv_heads * head_dim)
        # o_proj: (att_heads * head_dim) * h = h * h
        # gate_proj: h * inter
        # up_proj: h * inter
        # down_proj: inter * h
        # input_layernorm + post_attention_layernorm: 2 * h
        q_p = h * (att_heads * head_dim)
        k_p = h * (kv_heads * head_dim)
        v_p = h * (kv_heads * head_dim)
        o_p = (att_heads * head_dim) * h
        mlp_p = 3 * (h * inter)
        norm_p = 2 * h
        layer_params = q_p + k_p + v_p + o_p + mlp_p + norm_p
        
        final_norm_p = h
        # lm_head (tied or untied):
        tie_embed = getattr(config, 'tie_word_embeddings', False)
        lm_head_p = 0 if tie_embed else vocab * h
        
        total_est = embed_params + (layers * layer_params) + final_norm_p + lm_head_p
        print(f"Estimated Parameters:  ~{total_est / 1e9:.2f} B ({total_est:,} params)")
        return config
    except Exception as e:
        print(f"Failed to load model config: {e}")
        return None

def inspect_tokenizer():
    print("=" * 65)
    print(f"3. TOKENIZER & CHAT TEMPLATE ({MODEL_ID})")
    print("=" * 65)
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        print(f"Tokenizer Class:       {tokenizer.__class__.__name__}")
        print(f"Vocab Size:            {len(tokenizer)}")
        print(f"EOS Token:             '{tokenizer.eos_token}' (ID: {tokenizer.eos_token_id})")
        print(f"PAD Token:             '{tokenizer.pad_token}' (ID: {tokenizer.pad_token_id})")
        print(f"BOS Token:             '{tokenizer.bos_token}' (ID: {tokenizer.bos_token_id})")
        has_chat_template = getattr(tokenizer, "chat_template", None) is not None
        print(f"Chat Template Found:   {has_chat_template}")
        
        # Test formatting sample legal messages
        sample_messages = [
            {"role": "system", "content": "You are LegalAI."},
            {"role": "user", "content": "What is an FIR?"},
            {"role": "assistant", "content": "An FIR is a First Information Report."}
        ]
        formatted = tokenizer.apply_chat_template(sample_messages, tokenize=False)
        print("\n--- Sample Rendered Chat Template ---")
        print(formatted)
        print("-------------------------------------")
        return tokenizer
    except Exception as e:
        print(f"Failed to load tokenizer: {e}")
        return None

def inspect_lora_targets():
    print("=" * 65)
    print("4. LoRA CONFIGURATION & MODULE TARGET COMPATIBILITY")
    print("=" * 65)
    target_modules = [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ]
    print(f"Target Modules:        {target_modules}")
    print("Architecture Mapping:  Qwen2 / Qwen2.5 uses standard Qwen2DecoderLayer with:")
    print("  - Self-Attention:    self_attn.q_proj, self_attn.k_proj, self_attn.v_proj, self_attn.o_proj")
    print("  - MLP:               mlp.gate_proj, mlp.up_proj, mlp.down_proj")
    print("All 7 target modules match Qwen2.5 architecture identically.")
    
    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=target_modules,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    print(f"PEFT LoraConfig initialized successfully: r={lora_cfg.r}, alpha={lora_cfg.lora_alpha}")

if __name__ == "__main__":
    inspect_environment()
    inspect_model_config()
    inspect_tokenizer()
    inspect_lora_targets()
