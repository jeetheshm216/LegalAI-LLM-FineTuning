"""Tests the live FastAPI server endpoints for General Indian Legal Knowledge."""

import urllib.request
import json

BASE_URL = "http://127.0.0.1:8008/api/v1/ai/chat"


def query_api(text: str):
    payload = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_all_tests():
    print("=" * 60)
    print("LEGALAI — LIVE INDIAN LEGAL KNOWLEDGE API VERIFICATION")
    print("=" * 60)

    # 1. Foreign Law Query: GDPR
    print("\n[TEST 1: Foreign Law Interception - GDPR]")
    res1 = query_api("What is GDPR?")
    print("Content:", res1["content"])
    print("Query Type:", res1.get("query_type"))
    assert "LegalAI currently focuses on Indian law" in res1["content"]
    assert "Digital Personal Data Protection Act, 2023" in res1["content"]
    print("--> PASS: Polite Indian-law redirection verified.")

    # 2. Constitutional Law: Article 21
    print("\n[TEST 2: Constitutional Law - Article 21]")
    res2 = query_api("What does Article 21 of the Constitution of India guarantee?")
    print("Snippet:", res2["content"][:220])
    print("Sources:", [s["reference"] for s in res2.get("sources", [])])
    assert "Article 21" in res2["content"]
    assert "Constitution of India" in res2["content"]
    print("--> PASS: Article 21 Constitution retrieved.")

    # 3. Central Act: Section 138 NI Act
    print("\n[TEST 3: Central Act - Section 138 Negotiable Instruments Act]")
    res3 = query_api("What are the requirements of Section 138 NI Act for cheque bounce?")
    print("Snippet:", res3["content"][:220])
    print("Sources:", [s["reference"] for s in res3.get("sources", [])])
    assert "Section 138" in res3["content"]
    assert "Negotiable Instruments Act" in res3["content"]
    print("--> PASS: Section 138 NI Act retrieved.")

    # 4. Struck Down Provision: Section 66A IT Act
    print("\n[TEST 4: Struck-down Provision - Section 66A IT Act / Shreya Singhal]")
    res4 = query_api("Can police register FIR under Section 66A IT Act?")
    print("Snippet:", res4["content"][:280])
    print("Reliability:", res4.get("reliabilityLabel"))
    assert "Shreya Singhal" in res4["content"]
    assert "unconstitutional" in res4["content"].lower()
    print("--> PASS: Struck down provision verified with Shreya Singhal precedent.")

    # 5. Supreme Court Precedent: Arjun Panditrao Khotkar
    print("\n[TEST 5: Judicial Precedent - Electronic Evidence Certificate]")
    res5 = query_api("What did Supreme Court hold in Arjun Panditrao regarding 65B certificate?")
    print("Snippet:", res5["content"][:250])
    print("Sources:", [s["reference"] for s in res5.get("sources", [])])
    assert "Arjun Panditrao Khotkar" in res5["content"]
    assert "(2020) 7 SCC 1" in res5["content"]
    print("--> PASS: Arjun Panditrao Khotkar precedent retrieved.")

    print("\n" + "=" * 60)
    print("ALL LIVE INDIAN LEGAL KNOWLEDGE API TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
