import urllib.request
import json
import time

def test_models():
    for model in ["Qwen/Qwen2.5-32B-Instruct", "legalai", "case_analysis"]:
        t0 = time.time()
        req_data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Hello! Briefly introduce yourself in one sentence."}],
            "max_tokens": 50,
            "temperature": 0.0,
            "stream": True
        }).encode("utf-8")
        
        req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        
        chunks = []
        first = True
        ttft = 0.0
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                line = line.decode("utf-8").strip()
                if line.startswith("data: ") and line != "data: [DONE]":
                    data = json.loads(line[6:])
                    text = data["choices"][0]["delta"].get("content", "")
                    if text:
                        if first:
                            ttft = time.time() - t0
                            first = False
                        chunks.append(text)
        dur = time.time() - t0
        full_text = "".join(chunks).strip()
        print(f"[{model}] TTFT: {ttft*1000:.1f}ms | Total: {dur:.3f}s | Chunks: {len(chunks)} | Speed: {len(chunks)/dur:.1f} tps")
        print(f"   -> {full_text}\n")

if __name__ == "__main__":
    test_models()
