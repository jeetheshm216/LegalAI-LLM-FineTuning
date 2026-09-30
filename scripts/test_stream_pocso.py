import json
import requests

url = "http://127.0.0.1:8008/api/v1/ai/chat/stream"
payload = {"content": "What does Section 19 of the POCSO Act require when an offence is known or suspected?"}

resp = requests.post(url, json=payload, stream=True, timeout=60)
assert resp.status_code == 200

complete_event = None
tokens_received = 0
for line in resp.iter_lines():
    if line:
        decoded = line.decode("utf-8")
        if decoded.startswith("event:"):
            ev = decoded.replace("event:", "").strip()
        elif decoded.startswith("data:"):
            data_str = decoded.replace("data:", "").strip()
            if ev == "token":
                tokens_received += 1
            elif ev == "complete":
                complete_event = json.loads(data_str)

print("SSE Stream Result for POCSO §19:")
print("Tokens received:", tokens_received)
print("Complete event query_type:", complete_event.get("query_type"))
print("Complete event reliability:", complete_event.get("reliability"))
print("Complete event sources count:", len(complete_event.get("sources", [])))
top_s = complete_event.get("sources", [])[0]
print("Top source:", top_s.get("chunk_id"), "|", top_s.get("act_name"), "|", top_s.get("section_number"))
print("Content preview:", complete_event.get("content")[:180].replace("\n", " "))

assert complete_event.get("query_type") == "LEGAL_QUERY"
assert "POCSO_ACT_2012" in top_s.get("chunk_id")
assert "19" in top_s.get("chunk_id")
for s in complete_event.get("sources", []):
    assert "POCSO_ACT_2012" in s.get("chunk_id")
    assert "BNS" not in s.get("chunk_id")

print("--> SSE STREAM TEST PASSED! 100% POCSO, ZERO BNS LEAKAGE!")
