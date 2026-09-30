import sqlite3

conn = sqlite3.connect("data/legalai_case_rag.db")
c = conn.cursor()
c.execute("SELECT document_name, page_number, chunk_index, text FROM case_chunks WHERE case_id='case-live-test-01'")
for doc, page, chunk, text in c.fetchall():
    print(f"=== {doc} (p.{page}, c.{chunk}) ===")
    print(text)
conn.close()
