import os
import re

def patch_pipeline():
    path = "/home/sece2026-student07/legalai-finetuning/src/legal_knowledge/retrieval/pipeline.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "import urllib.request" not in content:
        content = "import urllib.request\nimport json\n" + content

    target = """            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)"""

    replacement = """            # Fast path: vLLM OpenAI-compatible generation (80-150 tokens/s)
            try:
                vllm_req_data = json.dumps({
                    "model": "legalai",
                    "messages": messages,
                    "max_tokens": max_new_tokens,
                    "temperature": 0.35 if sub_q_count >= 2 else 0.0,
                    "top_p": 0.92 if sub_q_count >= 2 else 1.0,
                }).encode("utf-8")
                vllm_req = urllib.request.Request(
                    "http://127.0.0.1:8009/v1/chat/completions",
                    data=vllm_req_data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(vllm_req, timeout=15) as resp:
                    vllm_data = json.loads(resp.read().decode("utf-8"))
                    answer_text = vllm_data["choices"][0]["message"]["content"].strip()
                    if answer_text:
                        return answer_text
            except Exception as vllm_err:
                pass

            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)"""

    if target in content and "Fast path: vLLM OpenAI-compatible generation" not in content:
        content = content.replace(target, replacement, 1)
        print("Updated _generate_answer in src/legal_knowledge/retrieval/pipeline.py with vLLM fast path and HF fallback")
    else:
        print("Note: target not replaced or already patched")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    patch_pipeline()
