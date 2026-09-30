import urllib.request
import json
import time

def run_query(query, label):
    print("=" * 70)
    print(f"QUERY [{label}]: {query}")
    print("=" * 70)
    
    t0 = time.time()
    req_data = json.dumps({
        "content": query,
        "history": [],
        "caseId": "case-01"
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "http://127.0.0.1:8008/api/v1/ai/chat/stream",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    
    first_token_time = None
    token_count = 0
    complete_payload = None
    last_text = ""
    
    with urllib.request.urlopen(req, timeout=45) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("event: token"):
                continue
            elif line.startswith("data: "):
                try:
                    data_json = json.loads(line[6:])
                    if "token" in data_json:
                        if first_token_time is None:
                            first_token_time = time.time() - t0
                        token_count += 1
                        last_text = data_json["token"]
                    elif "content" in data_json:
                        complete_payload = data_json
                        resp.close()
                        break
                except Exception:
                    pass

    total_time = time.time() - t0
    ttft_ms = (first_token_time * 1000) if first_token_time else 0
    tps = token_count / total_time if total_time > 0 else 0
    
    print(f"TTFT: {ttft_ms:.1f} ms | Total Time: {total_time:.2f} s | Tokens: {token_count} | Speed: {tps:.1f} tps")
    print(f"Route: {complete_payload.get('route')} | Reliability: {complete_payload.get('reliability')}\n")
    print("RESPONSE OUTPUT:\n" + last_text + "\n\n")

if __name__ == "__main__":
    # Test 1: The user's exact analogy question that previously gave the car rental output
    run_query(
        "Give me an analogy to understand this case of Martinez v. Coastal Holdings",
        "COMMERCIAL ANALOGY TEST"
    )
    # Test 2: The next phase requirement: Points to specify in the next hearing
    run_query(
        "Carefully analyze this case and tell me what are the specific points, arguments, and relief we must specify and pray for in the next hearing?",
        "NEXT HEARING PREPARATION TEST"
    )
