import urllib.request
import json
import time

def test_stream(query, label):
    print("=" * 60)
    print(f"TEST: {label} -> '{query}'")
    print("=" * 60)
    
    t0 = time.time()
    req_data = json.dumps({
        "content": query,
        "history": [],
        "active_case_id": None
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
    
    with urllib.request.urlopen(req, timeout=30) as resp:
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
    
    print(f"Time to First Token (TTFT): {ttft_ms:.1f} ms")
    print(f"Total Stream Time:         {total_time:.3f} s")
    print(f"Token updates received:    {token_count}")
    print(f"Effective throughput:      {tps:.1f} tokens/s")
    if complete_payload:
        print(f"Route:                     {complete_payload.get('route')}")
        print(f"Query Type:                {complete_payload.get('query_type')}")
        print(f"Reliability:               {complete_payload.get('reliability')}")
        print(f"Citations:                 {complete_payload.get('citations')}")
    print("\nFull Output Preview:\n" + last_text[:400] + "...\n")

if __name__ == "__main__":
    test_stream("Explain the provisions and punishment for murder under Section 103 BNS", "LEGAL STATUTORY INQUIRY")
    test_stream("What are the essential elements of cheating under Bharatiya Nyaya Sanhita?", "LEGAL CONCEPT INQUIRY")
