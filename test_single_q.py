import requests
import json
import time

for q in ["hwo are you", "what are you doing", "wow"]:
    t0 = time.time()
    r = requests.post(
        "http://localhost:8008/api/v1/ai/chat/stream",
        json={"content": q, "mode": "GENERAL", "history": []},
        stream=True,
        timeout=30
    )
    tokens = []
    final_content = ""
    for line in r.iter_lines():
        line_str = line.decode('utf-8') if isinstance(line, bytes) else line
        if not line_str:
            continue
        if line_str.startswith("data: "):
            try:
                data = json.loads(line_str[6:])
                if "token" in data:
                    tokens.append(data["token"])
                if "content" in data:
                    final_content = data["content"]
            except Exception:
                pass
    elapsed = round(time.time() - t0, 3)
    print(f"QUERY: '{q}' | ELAPSED: {elapsed}s | FINAL CONTENT: {final_content}")
