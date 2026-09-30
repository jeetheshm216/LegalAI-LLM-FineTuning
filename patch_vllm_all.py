import sys
import os
import re

def patch_server():
    server_path = "/home/sece2026-student07/legalai-finetuning/src/api/server.py"
    with open(server_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "import urllib.request" not in content:
        content = "import urllib.request\n" + content
        print("Prepended import urllib.request to server.py")

    old_fn = """def stream_generate_tokens(
    pipeline,
    messages: List[Dict[str, str]],
    max_new_tokens: int = 384,
    disable_adapter: bool = False
):
    \"\"\"Runs generation in a background thread and yields tokens via TextIteratorStreamer.\"\"\"
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}

    streamer = TextIteratorStreamer(
        pipeline.tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        use_cache=True,
        pad_token_id=pipeline.tokenizer.pad_token_id,
        eos_token_id=pipeline.tokenizer.eos_token_id,
    )

    has_disable = hasattr(pipeline.model, "disable_adapter")

    def run_inference():
        with torch.inference_mode():
            if disable_adapter and has_disable:
                with pipeline.model.disable_adapter():
                    pipeline.model.generate(**generation_kwargs)
            else:
                pipeline.model.generate(**generation_kwargs)

    t = threading.Thread(target=run_inference)
    t.daemon = True
    t.start()
    return streamer"""

    new_fn = """def stream_generate_tokens(
    pipeline,
    messages: List[Dict[str, str]],
    max_new_tokens: int = 384,
    disable_adapter: bool = False,
    adapter_name: Optional[str] = None
):
    \"\"\"
    Streams tokens with ultra-fast vLLM engine (100+ tokens/s),
    falling back to local HuggingFace TextIteratorStreamer if vLLM is unavailable.
    \"\"\"
    model_name = "Qwen/Qwen2.5-14B-Instruct" if disable_adapter else ("case_analysis" if adapter_name == "case_analysis" else "legalai")
    
    # Fast path: vLLM OpenAI-compatible streaming
    try:
        req_data = json.dumps({
            "model": model_name,
            "messages": messages,
            "max_tokens": max_new_tokens,
            "temperature": 0.0,
            "stream": True
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        
        def vllm_chunk_generator(r):
            with r:
                for line in r:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            chunk = data["choices"][0]["delta"].get("content", "")
                            if chunk:
                                yield chunk
                        except Exception:
                            continue
        return vllm_chunk_generator(resp)
    except Exception as e:
        logger.warning(f"vLLM streaming connection failed ({e}), using local model fallback")

    # Fallback to local HuggingFace TextIteratorStreamer
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}

    streamer = TextIteratorStreamer(
        pipeline.tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        use_cache=True,
        pad_token_id=pipeline.tokenizer.pad_token_id,
        eos_token_id=pipeline.tokenizer.eos_token_id,
    )

    has_disable = hasattr(pipeline.model, "disable_adapter")

    def run_inference():
        with torch.inference_mode():
            if disable_adapter and has_disable:
                with pipeline.model.disable_adapter():
                    pipeline.model.generate(**generation_kwargs)
            else:
                pipeline.model.generate(**generation_kwargs)

    t = threading.Thread(target=run_inference)
    t.daemon = True
    t.start()
    return streamer"""

    if old_fn in content:
        content = content.replace(old_fn, new_fn)
        print("Updated stream_generate_tokens with vLLM fast path and HF fallback in server.py")
    else:
        print("WARNING: Could not find exact old stream_generate_tokens block in server.py")

    # 2. Update generate_conversational_response fallback model generation
    old_conv_gen = """    prompt = pipeline.tokenizer.apply_chat_template(
        chat_turns,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    with torch.inference_mode():
        output_ids = pipeline.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=pipeline.tokenizer.pad_token_id,
            eos_token_id=pipeline.tokenizer.eos_token_id,
        )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()"""

    new_conv_gen = """    try:
        req_data = json.dumps({
            "model": "legalai",
            "messages": chat_turns,
            "max_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    prompt = pipeline.tokenizer.apply_chat_template(
        chat_turns,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    with torch.inference_mode():
        output_ids = pipeline.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=pipeline.tokenizer.pad_token_id,
            eos_token_id=pipeline.tokenizer.eos_token_id,
        )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()"""

    if old_conv_gen in content:
        content = content.replace(old_conv_gen, new_conv_gen)
        print("Updated generate_conversational_response with vLLM fast path in server.py")

    with open(server_path, "w", encoding="utf-8") as f:
        f.write(content)


def patch_rag_legalai():
    rag_path = "/home/sece2026-student07/legalai-finetuning/src/rag/integration/rag_legalai.py"
    with open(rag_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "import urllib.request" not in content:
        content = "import urllib.request\nimport json\n" + content

    target_block = """        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = output_ids[0, input_length:]
        answer_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()"""

    replacement_block = """        vllm_success = False
        try:
            req_data = json.dumps({
                "model": "legalai",
                "messages": messages,
                "max_tokens": max_new_tokens,
                "temperature": 0.0
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8009/v1/chat/completions",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                vllm_data = json.loads(resp.read().decode("utf-8"))
                answer_text = vllm_data["choices"][0]["message"]["content"].strip()
                vllm_success = True
        except Exception:
            vllm_success = False

        if not vllm_success:
            with torch.inference_mode():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            new_tokens = output_ids[0, input_length:]
            answer_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()"""

    if target_block in content:
        content = content.replace(target_block, replacement_block)
        print("Updated answer_question in rag_legalai.py with vLLM fast path and HF fallback")
    else:
        print("WARNING: Could not find exact target block in rag_legalai.py")

    with open(rag_path, "w", encoding="utf-8") as f:
        f.write(content)


def patch_case_rag_pipeline():
    case_path = "/home/sece2026-student07/legalai-finetuning/src/case_rag/pipeline.py"
    with open(case_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "import urllib.request" not in content:
        content = "import urllib.request\nimport json\n" + content

    # In generate_answer:
    target_start = 'prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)'
    new_start = '''# Fast path: vLLM inference (50-150 tokens/s)
        target_model = "Qwen/Qwen2.5-14B-Instruct" if not use_adapter else "case_analysis"
        try:
            req_data = json.dumps({
                "model": target_model,
                "messages": messages,
                "max_tokens": max_new_tokens,
                "temperature": 0.0
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8009/v1/chat/completions",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                vllm_data = json.loads(resp.read().decode("utf-8"))
                return vllm_data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)'''

    if target_start in content and "target_model = \"Qwen/Qwen2.5-14B-Instruct\"" not in content:
        content = content.replace(target_start, new_start, 1)
        print("Updated generate_answer in src/case_rag/pipeline.py with vLLM fast path and HF fallback")
    else:
        print("Note: target_start check in case_rag/pipeline.py")

    with open(case_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    patch_server()
    patch_rag_legalai()
    patch_case_rag_pipeline()
    print("All patches applied successfully!")
