import sqlite3

conn_app = sqlite3.connect("data/legalai_app.db")
cur_app = conn_app.cursor()
print("=== APP DB DOCUMENTS ===")
for r in cur_app.execute("SELECT id, case_id, name, type, size FROM documents WHERE case_id IN ('case-01', 'case-02', 'case-03', 'case-04')").fetchall():
    print(r)

conn_rag = sqlite3.connect("data/legalai_case_rag.db")
cur_rag = conn_rag.cursor()
print("\n=== RAG CHUNKS FOR CASES ===")
for r in cur_rag.execute("SELECT id, case_id, document_name, page_number FROM case_chunks WHERE case_id IN ('case-01', 'case-02', 'case-03', 'case-04', '2024-CV-1187')").fetchall():
    print(r)
