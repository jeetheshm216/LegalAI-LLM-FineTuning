import requests
import json

BASE_URL = "http://127.0.0.1:8008"

def test_endpoints():
    print("--- 1. Testing GET /api/v1/conversations ---")
    r = requests.get(f"{BASE_URL}/api/v1/conversations")
    print(f"Status: {r.status_code}, Resp: {r.json()}")

    print("\n--- 2. Testing 'hi' inside a case (should give clean greeting, zero document dump) ---")
    payload_hi = {
        "content": "hi",
        "caseId": "2024-CV-1187",
        "mode": "SINGLE_CASE"
    }
    r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload_hi)
    res = r.json()
    print(f"Status: {r.status_code}")
    print(f"Query Type: {res.get('query_type')}, Route: {res.get('route')}")
    print(f"Sources: {len(res.get('sources', []))}")
    print(f"Answer Content:\n{res.get('content')}")

    print("\n--- 3. Testing Civil Petition Drafting Prompt ---")
    civil_petition_prompt = """**1. Type of Document:**
Civil Petition / Petition relating to a property dispute

**2. Purpose:**
The petition is being prepared to request the court to protect the petitioner's rights over a property and to seek appropriate relief against the respondent, who is allegedly interfering with the petitioner's lawful possession of the property.

**3. Parties Involved:**

* **Petitioner:** Mr. Arun Kumar, aged 42, residing at Coimbatore, Tamil Nadu
* **Respondent:** Mr. Ravi Kumar, aged 45, residing at Coimbatore, Tamil Nadu
* **Court:** Appropriate jurisdictional Civil Court

**4. Specific Details / Clauses:**

* Description and location of the disputed property
* Petitioner's basis for claiming ownership or lawful possession
* Details of the respondent's alleged interference
* Relevant dates and events
* Details of supporting documents, such as sale deed, patta, tax receipts, or other records
* Request for the court to restrain the respondent from interfering with the petitioner's possession
"""
    payload_draft = {
        "content": civil_petition_prompt,
        "mode": "GENERAL"
    }
    r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload_draft)
    res = r.json()
    print(f"Status: {r.status_code}")
    print(f"Query Type: {res.get('query_type')}, Route: {res.get('route')}")
    print(f"Sources: {len(res.get('sources', []))}")
    content = res.get('content', '')
    print(f"Answer Snippet (first 400 chars):\n{content[:400]}")
    assert "2024-CV-0998" not in content, "Error: hallucinated Nguyen estate case!"
    assert "Nguyen" not in content, "Error: hallucinated Nguyen name!"
    assert "Arun Kumar" in content, "Success: contains Arun Kumar"
    print("Civil Petition verification passed!")

    print("\n--- 4. Testing Conversation Lifecycle (Create -> Rename -> Delete) ---")
    import time
    conv_id = f"test-conv-{int(time.time())}"
    new_conv = {
        "id": conv_id,
        "title": "Initial Test Chat",
        "mode": "GENERAL",
        "case_id": None,
        "case_number": None,
        "selected_cases": [],
        "context_settings": {},
        "messages": [{"role": "user", "content": "hello"}]
    }
    r_save = requests.post(f"{BASE_URL}/api/v1/conversations", json=new_conv)
    print(f"Save Conv Status: {r_save.status_code}, Body: {r_save.json()}")

    r_rename = requests.patch(f"{BASE_URL}/api/v1/conversations/{conv_id}/title", json={"title": "Renamed Test Chat"})
    print(f"Rename Status: {r_rename.status_code}, Body: {r_rename.json()}")

    r_del = requests.delete(f"{BASE_URL}/api/v1/conversations/{conv_id}")
    print(f"Delete Status: {r_del.status_code}, Body: {r_del.json()}")

    print("\nAll API tests completed successfully!")

if __name__ == "__main__":
    test_endpoints()
