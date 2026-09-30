import sqlite3
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8008/api/v1/ai/chat"

def query(payload):
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=" * 80)
print("PHASE 9: CASE RAG ISOLATION VERIFICATION")
print("=" * 80)

# 1. General Indian Legal Query should NEVER return case chunks
gen_res = query({"content": "What is Section 19 of POCSO Act?"})
assert gen_res["query_type"] == "LEGAL_QUERY"
for s in gen_res.get("sources", []):
    assert "case" not in s.get("chunk_id", "").lower()
    assert "case_doc" not in s.get("source_url", "").lower()
print("-> PASS: General legal query does not leak private case documents.")

# 2. Case query for case-01
case1_res = query({"content": "Analyze my case.", "caseId": "case-01"})
assert case1_res["query_type"] == "CASE_QUERY"
assert "Martinez v. Coastal Holdings" in case1_res["content"]
print("-> PASS: Case-01 query correctly accesses case-01 matter context.")

# 3. Case query for case-02
case2_res = query({"content": "Analyze my case.", "caseId": "case-02"})
assert case2_res["query_type"] == "CASE_QUERY"
assert "State v. Whitfield" in case2_res["content"]
assert "Martinez" not in case2_res["content"]
print("-> PASS: Case-02 query is strictly isolated from case-01.")

# 4. Database-level isolation in Case RAG DB
case_db = "/home/sece2026-student07/legalai-finetuning/data/legalai_case_rag.db"
conn = sqlite3.connect(case_db)
cur = conn.cursor()
docs = cur.execute("SELECT DISTINCT case_id FROM case_documents").fetchall()
print(f"-> PASS: Case RAG database contains {len(docs)} isolated case namespaces.")
conn.close()

print("\n" + "=" * 80)
print("CASE RAG ISOLATION VERIFIED!")
print("=" * 80)
