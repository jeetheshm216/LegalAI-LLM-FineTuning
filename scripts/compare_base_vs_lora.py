import os
import sys
import json
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"
LORA_PATH = "/home/sece2026-student07/legalai-finetuning/outputs/qwen14b-legalai-v2"
DEVICE = "cuda:1" if torch.cuda.device_count() > 1 else "cuda:0"

print(f"Using Device: {DEVICE}")

# Define the 3 distinct multi-turn conversations requested by the user:
conversations = [
    {
        "domain": "Legal (BNS Section 103)",
        "turns": [
            "What does BNS Section 103 provide?",
            "Explain it simply.",
            "What is the punishment under this section?"
        ]
    },
    {
        "domain": "Programming (Python Odd/Even)",
        "turns": [
            "Write a Python program to check whether a number is odd or even.",
            "Explain the code."
        ]
    },
    {
        "domain": "AI / Technology (Qwen Concept)",
        "turns": [
            "What is Qwen?",
            "Tell me more about it.",
            "Now explain it like I'm a beginner."
        ]
    }
]

def run_conversation(model, tokenizer, turns, is_lora=False):
    history = []
    results = []
    
    for turn_idx, user_msg in enumerate(turns):
        history.append({"role": "user", "content": user_msg})
        
        # Build chat template
        prompt = tokenizer.apply_chat_template(
            history,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        input_len = inputs["input_ids"].shape[1]
        
        t0 = time.time()
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                do_sample=True
            )
        elapsed = round(time.time() - t0, 2)
        
        gen_ids = outputs[0, input_len:]
        answer = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        history.append({"role": "assistant", "content": answer})
        
        results.append({
            "turn": turn_idx + 1,
            "user_query": user_msg,
            "model_response": answer,
            "tokens_generated": len(gen_ids),
            "generation_time_sec": elapsed
        })
    return results

print("\n--- PHASE 1: LOADING BASE QWEN MODEL ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map=DEVICE,
    trust_remote_code=True
)
base_model.eval()
print("Base Qwen model loaded successfully on", DEVICE)

base_results = {}
for conv in conversations:
    domain = conv["domain"]
    print(f"\n[BASE QWEN] Running Conversation: {domain}...")
    base_results[domain] = run_conversation(base_model, tokenizer, conv["turns"], is_lora=False)

print("\n--- PHASE 2: ATTACHING LORA ADAPTER ---")
lora_model = PeftModel.from_pretrained(base_model, LORA_PATH)
lora_model.eval()
print(f"LegalAI V2 LoRA adapter attached from {LORA_PATH}")

lora_results = {}
for conv in conversations:
    domain = conv["domain"]
    print(f"\n[QWEN + LORA] Running Conversation: {domain}...")
    lora_results[domain] = run_conversation(lora_model, tokenizer, conv["turns"], is_lora=True)

# Save combined comparison report
output_data = {
    "base_qwen_results": base_results,
    "qwen_lora_results": lora_results
}

report_path = "/home/sece2026-student07/legalai-finetuning/scripts/base_vs_lora_comparison.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\nCompleted! Saved full results to {report_path}")

# Print summary comparison table to stdout
print("\n" + "="*80)
print("COMPARATIVE EVALUATION SUMMARY")
print("="*80)

for conv in conversations:
    domain = conv["domain"]
    print(f"\nDOMAIN: {domain.upper()}")
    print("-" * 60)
    for i in range(len(conv["turns"])):
        q = conv["turns"][i]
        b_ans = base_results[domain][i]["model_response"]
        l_ans = lora_results[domain][i]["model_response"]
        
        print(f"\n>>> TURN {i+1}: \"{q}\"")
        print("\n[BASE QWEN]:")
        print(b_ans[:250] + ("..." if len(b_ans) > 250 else ""))
        print("\n[QWEN + LORA]:")
        print(l_ans[:250] + ("..." if len(l_ans) > 250 else ""))
