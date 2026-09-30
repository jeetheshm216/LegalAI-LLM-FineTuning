import requests
import time

t0 = time.time()
try:
    r = requests.post(
        "http://127.0.0.1:8008/api/v1/ai/chat",
        json={
            "content": "What are the key facts in my case?",
            "caseId": "case-01",
            "mode": "SINGLE_CASE",
            "selectedCases": ["case-01"],
            "history": []
        },
        timeout=180
    )
    dur = round(time.time() - t0, 3)
    print("Status:", r.status_code, "Duration:", dur)
    res = r.json()
    print("Route:", res.get("route"))
    print("Content preview:", res.get("content", "")[:200])
except Exception as e:
    print("Error:", e, "Duration:", round(time.time() - t0, 3))
