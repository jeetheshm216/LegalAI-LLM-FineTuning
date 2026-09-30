import sqlite3

def inspect_schema():
    conn_app = sqlite3.connect("data/legalai_app.db")
    cur_app = conn_app.cursor()
    print("=== CASES TABLE SCHEMA ===")
    for col in cur_app.execute("PRAGMA table_info(cases)").fetchall():
        print(col)
    
    print("\n=== SAMPLE CASE ===")
    sample = cur_app.execute("SELECT * FROM cases LIMIT 2").fetchall()
    for s in sample:
        print(s)

    conn_rag = sqlite3.connect("data/legalai_case_rag.db")
    cur_rag = conn_rag.cursor()
    print("\n=== CASE_CHUNKS SCHEMA ===")
    for col in cur_rag.execute("PRAGMA table_info(case_chunks)").fetchall():
        print(col)
    print("\n=== CASE_DOCUMENTS SCHEMA ===")
    for col in cur_rag.execute("PRAGMA table_info(case_documents)").fetchall():
        print(col)
    print("\n=== CHUNKS PER CASE ===")
    print(cur_rag.execute("SELECT case_id, count(*) FROM case_chunks GROUP BY case_id").fetchall())

if __name__ == "__main__":
    inspect_schema()
