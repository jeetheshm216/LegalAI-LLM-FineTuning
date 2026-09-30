import json
import time
import requests

BASE_URL = "http://127.0.0.1:8008"

BENCHMARK_PROMPTS = [
    {
        "id": "q1_general_coding",
        "name": "General Coding / Concept (Odd or Even Python)",
        "query": "Write a Python program to check whether a number is odd or even.",
        "case_id": None,
        "mode": "GENERAL",
        "history": []
    },
    {
        "id": "q2_case_greeting",
        "name": "Case Context Greeting ('hi')",
        "query": "hi",
        "case_id": "2024-CV-1187",
        "mode": "SINGLE_CASE",
        "history": []
    },
    {
        "id": "q3_civil_petition_drafting",
        "name": "Civil Petition Property Dispute Drafting",
        "query": """**1. Type of Document:**
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
""",
        "case_id": None,
        "mode": "GENERAL",
        "history": []
    },
    {
        "id": "q4_legal_statutory",
        "name": "Legal Statutory Query (BNS Section 103 Murder)",
        "query": "What is the punishment for murder under section 103 of Bharatiya Nyaya Sanhita?",
        "case_id": None,
        "mode": "GENERAL",
        "history": []
    },
    {
        "id": "q5_legal_conceptual_low_conf",
        "name": "General Legal Concept (Doctrine of Res Judicata and Estoppel)",
        "query": "Explain the concept of constructive res judicata and how it differs from issue estoppel under Indian civil jurisprudence.",
        "case_id": None,
        "mode": "GENERAL",
        "history": []
    }
]

def run_suite():
    results = []
    print(f"Executing {len(BENCHMARK_PROMPTS)} benchmark questions against {BASE_URL}...")
    for idx, item in enumerate(BENCHMARK_PROMPTS):
        print(f"\n[{idx+1}/{len(BENCHMARK_PROMPTS)}] Running: {item['name']}...")
        t0 = time.time()
        payload = {
            "content": item["query"],
            "caseId": item["case_id"],
            "mode": item["mode"],
            "history": item["history"]
        }
        try:
            r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=payload, timeout=120)
            dur = round(time.time() - t0, 3)
            if r.status_code == 200:
                data = r.json()
                res_obj = {
                    "id": item["id"],
                    "name": item["name"],
                    "query": item["query"],
                    "status_code": r.status_code,
                    "duration_sec": dur,
                    "query_type": data.get("query_type"),
                    "route": data.get("route"),
                    "reliability": data.get("reliability"),
                    "reliabilityLabel": data.get("reliabilityLabel"),
                    "source_count": len(data.get("sources", [])),
                    "sources": data.get("sources", []),
                    "content": data.get("content", "")
                }
                print(f" -> Success ({dur}s) | Route: {data.get('route')} | Sources: {len(data.get('sources', []))}")
                results.append(res_obj)
            else:
                print(f" -> Failed ({r.status_code}): {r.text}")
                results.append({
                    "id": item["id"],
                    "name": item["name"],
                    "query": item["query"],
                    "status_code": r.status_code,
                    "duration_sec": dur,
                    "error": r.text
                })
        except Exception as e:
            dur = round(time.time() - t0, 3)
            print(f" -> Exception ({dur}s): {e}")
            results.append({
                "id": item["id"],
                "name": item["name"],
                "query": item["query"],
                "error": str(e)
            })

    output_path = "/home/sece2026-student07/legalai-finetuning/benchmark_final_after_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved final benchmark results to {output_path}")

if __name__ == "__main__":
    run_suite()
