import sqlite3

conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_rag_mvp.db")
c = conn.cursor()

c.execute("SELECT chunk_id, length(content), content FROM legal_chunks WHERE section_id='BNS_2023_SEC_303' OR chunk_id LIKE '%BNS_2023_SEC_303%'")
rows = c.fetchall()
print(f"Total chunks found: {len(rows)}")
for r in rows:
    print(f"=== {r[0]} (length: {r[1]}) ===")
    print(repr(r[2]))
    print("-" * 50)
