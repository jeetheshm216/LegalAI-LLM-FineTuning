import sqlite3

def inspect():
    conn_app = sqlite3.connect("data/legalai_app.db")
    cur_app = conn_app.cursor()
    cases = cur_app.execute("SELECT id, title, case_number, client, opposing_party, status FROM cases").fetchall()
    print("=== CASES IN APPS DB ===")
    for c in cases:
        print(f"ID: {c[0]} | Title: {c[1]} | Num: {c[2]} | Client: {c[3]} | Opp: {c[4]} | Status: {c[5]}")

    docs = cur_app.execute("SELECT case_id, count(*) FROM documents GROUP BY case_id").fetchall()
    print("\n=== APP DB DOCS PER CASE ===")
    for d in docs:
        print(f"Case {d[0]}: {d[1]} docs")

    conn_rag = sqlite3.connect("data/legalai_case_rag.db")
    cur_rag = conn_rag.cursor()
    chunks = cur_rag.execute("SELECT case_id, count(*) FROM case_chunks GROUP BY case_id").fetchall()
    print("\n=== RAG CHUNKS PER CASE ===")
    for ch in chunks:
        print(f"Case {ch[0]}: {ch[1]} chunks")

    sample_chunks = cur_rag.execute("SELECT chunk_id, case_id, document_name, page_number FROM case_chunks LIMIT 10").fetchall()
    print("\n=== SAMPLE CHUNKS ===")
    for s in sample_chunks:
        print(s)

if __name__ == "__main__":
    inspect()
