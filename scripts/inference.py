#!/usr/bin/env python3
"""
scripts/inference.py

Interactive CLI chat interface for LegalAI.
Loads the base model Qwen/Qwen2.5-14B-Instruct together with the trained
LegalAI LoRA adapter and provides interactive question-answering for Indian law.
"""

import argparse
import os
import sys
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Default model paths
DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-14B-Instruct"
DEFAULT_ADAPTER_DIR = "outputs/qwen14b-first-run-final-dataset"

# Grounded Indian legal assistant system prompt
SYSTEM_PROMPT = (
    "You are an Indian legal information assistant. Provide accurate, structured, and helpful "
    "information based strictly on Indian law, statutes, and legal procedures. Do not pretend to "
    "be a lawyer, provide legal representation, or establish an attorney-client relationship. "
    "Do not invent or fabricate sections, acts, case judgments, or legal provisions. If you are "
    "uncertain or if the provided facts are insufficient, explicitly state that you cannot provide "
    "a definitive answer. Always advise the user to consult a qualified Indian advocate for "
    "case-specific legal advice."
)


def load_model_and_tokenizer(base_model_path: str, adapter_path: str):
    """
    Loads tokenizer, base causal LM, and attaches the PEFT LoRA adapter.
    """
    print("\n" + "=" * 60)
    print("LEGALAI INTERACTIVE CHAT — INITIALIZATION")
    print("=" * 60)
    print(f"Base Model:        {base_model_path}")
    print(f"LoRA Adapter:      {adapter_path}")
    
    # 1. Determine CUDA device and precision
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
    
    print(f"CUDA Device:       {device_name}")
    print(f"Torch Precision:   {dtype}")
    print("=" * 60)

    # 2. Load tokenizer (prefer adapter directory if present, fallback to base model)
    tokenizer_dir = adapter_path if os.path.exists(os.path.join(adapter_path, "tokenizer_config.json")) else base_model_path
    print(f"Loading tokenizer from: {tokenizer_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 3. Load base model in bfloat16 with automatic device placement
    print(f"Loading base model ({base_model_path}) in {dtype}...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=False,
    )

    # 4. Attach LoRA adapter
    if os.path.exists(adapter_path):
        print(f"Attaching LoRA adapter from: {adapter_path}...")
        model = PeftModel.from_pretrained(base_model, adapter_path)
    else:
        print(f"WARNING: Adapter directory '{adapter_path}' not found! Running base model zero-shot.")
        model = base_model

    # 5. Set model in evaluation mode
    model.eval()
    print("Model successfully loaded and set to evaluation mode.\n")
    return model, tokenizer


def generate_response(
    model,
    tokenizer,
    user_query: str,
    max_new_tokens: int = 512,
    temperature: float = 0.3,
    top_p: float = 0.9,
) -> str:
    """
    Renders user query using the Qwen chat template and generates response tokens.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    # Format messages using Qwen native chat template
    rendered_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Tokenize input and move tensors to model device
    model_device = getattr(model, "device", next(model.parameters()).device)
    inputs = tokenizer(rendered_prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(model_device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    # Generate response
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # Decode only the generated response tokens
    new_tokens = output_ids[0][input_length:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def chat_loop(model, tokenizer, max_new_tokens: int, temperature: float, top_p: float):
    """
    Interactive command-line loop for chatting with LegalAI.
    """
    print("=" * 60)
    print("LegalAI Interactive Console")
    print("Type your legal question below.")
    print("Type 'exit' or 'quit' to terminate the session.")
    print("=" * 60)

    while True:
        try:
            print()
            user_input = input("You > ").strip()
            
            # Check for termination commands or blank lines
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nExiting LegalAI Interactive Chat. Goodbye!")
                break

            print("\nLegalAI is thinking...\n")
            response = generate_response(
                model=model,
                tokenizer=tokenizer,
                user_query=user_input,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
            )

            print("=" * 60)
            print("LegalAI:")
            print("=" * 60)
            print(response)
            print("=" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\n\nSession interrupted (Ctrl+C). Exiting LegalAI Interactive Chat. Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description="LegalAI interactive command-line chat.")
    parser.add_argument(
        "--base-model",
        type=str,
        default=DEFAULT_BASE_MODEL,
        help=f"Base model path/name (default: {DEFAULT_BASE_MODEL})",
    )
    parser.add_argument(
        "--adapter-dir",
        type=str,
        default=DEFAULT_ADAPTER_DIR,
        help=f"LoRA adapter directory (default: {DEFAULT_ADAPTER_DIR})",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
        help="Maximum new tokens to generate (default: 512)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature (default: 0.3)",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="Top-p nucleus sampling (default: 0.9)",
    )
    args = parser.parse_args()

    # Load model and launch chat session
    model, tokenizer = load_model_and_tokenizer(
        base_model_path=args.base_model,
        adapter_path=args.adapter_dir,
    )
    chat_loop(
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )


if __name__ == "__main__":
    main()
