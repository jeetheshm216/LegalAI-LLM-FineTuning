import sys
import time
import requests
import json

BASE_URL = "http://localhost:8008/api/v1/ai/chat/stream"

def test_query(prompt, label):
    print(f"\n==========================================")
    print(f"TEST: {label} -> Query: '{prompt}'")
    print(f"==========================================")
    t0 = time.time()
    payload = {
        "content": prompt,
        "mode": "GENERAL",
        "history": []
    }
    first_token_time = None
    accumulated_content = ""
    event_type = None

    try:
        resp = requests.post(BASE_URL, json=payload, stream=True, timeout=120)
        for line in resp.iter_lines():
            line_str = line.decode('utf-8') if isinstance(line, bytes) else line
            if not line_str:
                continue
            if line_str.startswith("event: "):
                event_type = line_str[7:].strip()
            elif line_str.startswith("data: "):
                data_json = json.loads(line_str[6:])
                if event_type == "token":
                    if first_token_time is None:
                        first_token_time = round(time.time() - t0, 3)
                        print(f"⚡ [FIRST TOKEN ARRIVED IN {first_token_time}s]")
                    accumulated_content = data_json.get("token", "")
                elif event_type == "complete":
                    total_time = round(time.time() - t0, 3)
                    print(f"✅ [COMPLETED IN {total_time}s]")
                    print(f"Intent: {data_json.get('query_type')}")
                    print(f"Sample response:\n{data_json.get('content', '')[:250]}...")
                    return total_time, first_token_time
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

test_query("hwo are you", "Typo Pleasantry")
test_query("what are you doing", "Activity Question")
test_query("wow", "Interjection")
test_query("drfat a petishun for property dispute", "Typo Court Drafting")
