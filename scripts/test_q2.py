import requests
import json
import time

url = "http://localhost:8008/api/v1/ai/chat"
payload = {
    "content": "Summarize the established facts of this case using only the case documents.",
    "mode": "SINGLE_CASE",
    "caseId": "2024-CV-1187",
    "caseNumber": "2024-CV-1187"
}

print("Sending request for Query 2...")
t0 = time.time()
try:
    r = requests.post(url, json=payload, timeout=60)
    print("Done in", round(time.time() - t0, 2), "seconds")
    print("Status:", r.status_code)
    print("Response snippet:", r.text[:300])
except Exception as e:
    print("Failed after", round(time.time() - t0, 2), "seconds:", e)
