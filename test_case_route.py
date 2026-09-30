import sys
import os
import sqlite3

def test_db():
    conn_app = sqlite3.connect("data/legalai_app.db")
    cur_app = conn_app.cursor()
    cur_app.execute("PRAGMA table_info(documents)")
    print("documents columns in legalai_app.db:", [c[1] for c in cur_app.fetchall()])
    cur_app.execute("SELECT * FROM documents")
    docs = cur_app.fetchall()
    print("Documents in legalai_app.db:", docs)
    conn_app.close()

    conn_rag = sqlite3.connect("data/legalai_case_rag.db")
    cur_rag = conn_rag.cursor()
    cur_rag.execute("PRAGMA table_info(case_documents)")
    print("case_documents columns:", [c[1] for c in cur_rag.fetchall()])
    cur_rag.execute("SELECT id, case_id, filename, status FROM case_documents")
    rag_docs = cur_rag.fetchall()
    print("Case documents in legalai_case_rag.db:", rag_docs)

    cur_rag.execute("PRAGMA table_info(case_chunks)")
    print("case_chunks columns:", [c[1] for c in cur_rag.fetchall()])
    cur_rag.execute("SELECT id, case_id, document_id, document_name, chunk_index, length(text) FROM case_chunks")
    chunks = cur_rag.fetchall()
    print(f"Total chunks in legalai_case_rag.db: {len(chunks)}")
    for c in chunks:
        print("  Chunk:", c)
    conn_rag.close()

if __name__ == "__main__":
    test_db()
