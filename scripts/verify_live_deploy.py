import requests
import json

test_queries = [
    # 1. User's exact Screenshot 1 query:
    {
        "name": "Screenshot 1 - Case 2 (Whitfield)",
        "payload": {
            "content": "what is this case is about",
            "mode": "SINGLE_CASE",
            "caseId": "case-02",
            "caseNumber": "2024-CR-0442",
            "conversationId": "test_live_1"
        }
    },
    # 2. User's exact Screenshot 2 queries:
    {
        "name": "Screenshot 2 - are you doing good",
        "payload": {
            "content": "are you doing good",
            "mode": "GENERAL",
            "conversationId": "test_live_2"
        }
    },
    {
        "name": "Screenshot 2 - why aren't you working as a normal chatbot",
        "payload": {
            "content": "why aren't you working as a normal chatbot",
            "mode": "GENERAL",
            "conversationId": "test_live_3"
        }
    },
    {
        "name": "Screenshot 2 - martienx typo case query",
        "payload": {
            "content": "what is the case about the martienx",
            "mode": "GENERAL",
            "conversationId": "test_live_4"
        }
    },
    # 3. Case 1 query (Martinez)
    {
        "name": "Case 1 - Martinez cargo in berth 9",
        "payload": {
            "content": "what is the issue regarding the cargo in berth 9",
            "mode": "SINGLE_CASE",
            "caseId": "case-01",
            "caseNumber": "2024-CV-1187",
            "conversationId": "test_live_5"
        }
    }
]

print("="*70)
print("TESTING LIVE SERVER API (PORT 8008) WITH NEW CONTEXT-FIRST ROUTER")
print("="*70)

for t in test_queries:
    print(f"\n>>> Running: {t['name']}")
    print(f"    Payload: content='{t['payload']['content']}' mode='{t['payload']['mode']}' caseId='{t['payload'].get('caseId')}'")
    try:
        r = requests.post("http://127.0.0.1:8008/api/v1/ai/chat", json=t['payload'], timeout=45)
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            qtype = data.get("query_type")
            rel = data.get("reliability")
            content = data.get("content", "")
            print(f"    Query Type: {qtype} | Reliability: {rel}")
            print(f"    Response snippet (first 300 chars):")
            print("    " + content[:300].replace("\n", "\n    "))
        else:
            print(f"    Error text: {r.text[:200]}")
    except Exception as e:
        print(f"    Request failed: {e}")
