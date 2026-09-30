import urllib.request
import json
import time

QUERIES = [
    # 1. Conversational
    {"query": "hi", "case_id": None},
    {"query": "hello, how are you doing?", "case_id": None},
    
    # 2. General Legal / Act Overview
    {"query": "What is the Companies Act?", "case_id": None},
    
    # 3. Unindexed Legal Act
    {"query": "What is the Tamil Nadu Payment of Salaries Act?", "case_id": None},
    
    # 4. Act Number Query
    {"query": "What is the Act number of the Tamil Nadu Payment of Salaries Act?", "case_id": None},
    
    # 5. Exact Provision
    {"query": "Section 66C of the IT Act", "case_id": None},
    
    # 6. Ambiguous Provision
    {"query": "Section 49A", "case_id": None},
    
    # 7. Act 49A
    {"query": "act 49A", "case_id": None},
    
    # 8. Deterministic Statutory Absence
    {"query": "Section 9999 of the IT Act", "case_id": None},
    
    # 9. Natural Cybercrime Query
    {"query": "Someone stole my UPI credentials. What Indian legal provisions may apply?", "case_id": None},
    
    # 10. Case Queries (Case RAG + Case Analysis V1)
    {"query": "What are the key points in this case?", "case_id": "case-live-test-01"},
    {"query": "What evidence is missing?", "case_id": "case-live-test-01"},
    {"query": "What should I prepare for the next hearing?", "case_id": "case-live-test-01"},
]

def run_query(item):
    url = "http://127.0.0.1:8008/api/v1/ai/chat"
    payload = {"content": item["query"]}
    if item["case_id"]:
        payload["caseId"] = item["case_id"]
        payload["mode"] = "CASE_ASSISTANT"
    else:
        payload["mode"] = "GENERAL"
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read().decode("utf-8"))
            elapsed = time.time() - t0
            return resp, elapsed
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return {"error": f"HTTPError {e.code}: {err_msg}"}, time.time() - t0
    except Exception as e:
        return {"error": str(e)}, time.time() - t0

def get_field(res, key):
    if key in res:
        return res[key]
    diag = res.get("diagnostic", {})
    return diag.get(key)

def main():
    results = []
    print(f"Starting execution of {len(QUERIES)} queries in test matrix...")
    for idx, item in enumerate(QUERIES, 1):
        q = item["query"]
        cid = item["case_id"]
        print(f"\n=======================================================")
        print(f"[{idx}/{len(QUERIES)}] Query: {q} (case_id={cid})")
        res, elapsed = run_query(item)
        
        route = get_field(res, "route") or get_field(res, "query_type")
        intent = get_field(res, "intent")
        resolved_act = get_field(res, "resolved_act")
        prov_num = get_field(res, "provision_number")
        ret_mode = get_field(res, "retrieval_mode")
        adapter = get_field(res, "adapter")
        qwen_invoked = get_field(res, "qwen_invoked")
        abstained = get_field(res, "abstained")
        citations = res.get("citations", [])
        content = res.get("content", "")
        err = res.get("error")

        print(f"  Elapsed: {elapsed:.2f}s | Route: {route} | Intent: {intent}")
        print(f"  Act: {resolved_act} | Prov: {prov_num} | Ret: {ret_mode}")
        print(f"  Adapter: {adapter} | Qwen Invoked: {qwen_invoked} | Abstained: {abstained}")
        print(f"  Citation Count: {len(citations)}")
        text_snippet = content[:200].replace("\n", " ") if content else (err or "No content")
        print(f"  Snippet: {text_snippet}...")

        results.append({
            "index": idx,
            "query": q,
            "case_id": cid,
            "elapsed": elapsed,
            "route": route,
            "intent": intent,
            "resolved_act": resolved_act,
            "provision_number": prov_num,
            "retrieval_mode": ret_mode,
            "adapter": adapter,
            "qwen_invoked": qwen_invoked,
            "abstained": abstained,
            "citations_count": len(citations),
            "citations": citations,
            "response_snippet": text_snippet,
            "full_response": content,
            "error": err
        })
    
    with open("test_matrix_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved full test matrix results to scratch/test_matrix_results.json")

if __name__ == "__main__":
    main()
