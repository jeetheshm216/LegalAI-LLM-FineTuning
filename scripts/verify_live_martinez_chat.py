import requests
import json
import time
import sys

API_URL = "http://localhost:8008/api/v1/ai/chat"

def run_query(test_name, payload):
    print(f"\n==========================================", flush=True)
    print(f"=== {test_name} ===", flush=True)
    print(f"Payload: {json.dumps(payload)}", flush=True)
    t0 = time.time()
    try:
        resp = requests.post(API_URL, json=payload, timeout=120)
        elapsed = round(time.time() - t0, 2)
        print(f"Status: {resp.status_code} (in {elapsed}s)", flush=True)
        if resp.status_code == 200:
            data = resp.json()
            route = data.get("route") or data.get("query_type")
            sources = data.get("sources", [])
            content = data.get("content", "")
            print(f"Route / Query Type: {route}", flush=True)
            print(f"Num sources: {len(sources)}", flush=True)
            for s in sources:
                doc_title = s.get("title") or s.get("document_title") or s.get("act_name") or s.get("reference")
                chunk_id = s.get("id") or s.get("chunk_id")
                print(f"  - Source doc: {doc_title} | chunk: {chunk_id}", flush=True)
            print(f"Content snippet (first 350 chars):\n{content[:350]}...\n", flush=True)
            return data
        else:
            print(f"Error: {resp.text}", flush=True)
            return None
    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        print(f"Exception after {elapsed}s: {e}", flush=True)
        return None

def main():
    results = {}
    
    # 1. Five Martinez Demo Queries (using caseNumber: 2024-CV-1187)
    queries = [
        ("Query 1: Key points", "what are the key points in this case"),
        ("Query 2: Established facts", "Summarize the established facts of this case using only the case documents."),
        ("Query 3: Supporting evidence", "What evidence currently supports the client's position?"),
        ("Query 4: Missing evidence", "What important evidence is missing or unclear from the current case file?"),
        ("Query 5: Hearing preparation", "Prepare me for the upcoming hearing based only on this case file.")
    ]
    
    for name, q in queries:
        payload = {
            "content": q,
            "mode": "SINGLE_CASE",
            "caseId": "2024-CV-1187",
            "caseNumber": "2024-CV-1187"
        }
        res = run_query(name, payload)
        assert res is not None, f"{name} failed to get response"
        route = res.get("route") or res.get("query_type")
        assert route == "CASE_QUERY", f"{name} route was {route}, expected CASE_QUERY"
        assert len(res.get("sources", [])) > 0, f"{name} returned 0 sources"
        assert "You are inquiring about specific case matter or evidentiary documents" not in res.get("content", ""), f"{name} triggered fallback message!"
        results[name] = "PASSED"
        time.sleep(1)

    # 2. Test with caseId = case-01
    print("\n--- Testing with caseId = case-01 ---", flush=True)
    res_id = run_query("Query with case-01 id", {
        "content": "what are the key points in this case",
        "mode": "SINGLE_CASE",
        "caseId": "case-01"
    })
    assert res_id is not None
    route_id = res_id.get("route") or res_id.get("query_type")
    assert route_id == "CASE_QUERY" and len(res_id.get("sources", [])) > 0
    results["ID Resolution (case-01)"] = "PASSED"
    time.sleep(1)

    # 3. Test Context Switching: General Mode (should not retrieve Martinez private documents)
    print("\n--- Testing Context Switching: GENERAL Mode ---", flush=True)
    res_gen = run_query("General Mode Query", {
        "content": "What is the punishment for murder under BNS?",
        "mode": "GENERAL",
        "caseId": None
    })
    assert res_gen is not None
    for s in res_gen.get("sources", []):
        title = s.get("title") or s.get("document_title") or ""
        assert "Martinez" not in title and "Coastal" not in title, "Case document leaked into GENERAL mode!"
    results["General Mode Isolation"] = "PASSED"
    time.sleep(1)

    # Switch back to SINGLE_CASE
    res_back = run_query("Switch Back to SINGLE_CASE", {
        "content": "What is the injunction status in this matter?",
        "mode": "SINGLE_CASE",
        "caseId": "2024-CV-1187"
    })
    assert res_back is not None
    route_back = res_back.get("route") or res_back.get("query_type")
    assert route_back == "CASE_QUERY" and len(res_back.get("sources", [])) > 0
    results["Switch back to Single Case"] = "PASSED"
    time.sleep(1)

    # 4. Cross-Case Isolation: Query against another case (e.g. 2024-CR-0442)
    print("\n--- Testing Cross-Case Isolation ---", flush=True)
    res_iso = run_query("Cross-Case Isolation Query (2024-CR-0442)", {
        "content": "what are the key points in this case regarding Coastal Holdings?",
        "mode": "SINGLE_CASE",
        "caseId": "2024-CR-0442"
    })
    assert res_iso is not None
    for s in res_iso.get("sources", []):
        title = s.get("title") or s.get("document_title") or ""
        assert "Coastal" not in title and "Martinez" not in title, "Leakage across cases!"
    results["Cross-Case Isolation"] = "PASSED"

    print("\n================ SUMMARY ================", flush=True)
    for k, v in results.items():
        print(f"{k}: {v}", flush=True)
    print("\nALL INTEGRATION CHECKS PASSED!", flush=True)

if __name__ == "__main__":
    main()
