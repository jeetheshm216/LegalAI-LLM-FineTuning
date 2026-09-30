import urllib.request, json
url = "http://localhost:8008/api/v1/ai/chat"
req = urllib.request.Request(url, data=json.dumps({"content": "What is Section 89 of the Companies Act, 2013?"}).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
print("Keys:", list(data.keys()))
for k, v in data.items():
    if isinstance(v, str):
        print(f"{k} (len {len(v)}): {v[:150]}...")
    elif isinstance(v, list):
        print(f"{k} (count {len(v)})")
    else:
        print(f"{k}: {v}")
