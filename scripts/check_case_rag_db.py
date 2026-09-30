import sqlite3

conn = sqlite3.connect('/home/sece2026-student07/legalai-finetuning/data/legalai_case_rag.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print('Tables in case_rag.db:', tables)

for t in tables:
    c.execute(f"SELECT count(*) FROM {t}")
    cnt = c.fetchone()[0]
    print(f"Table {t}: {cnt} rows")

c.execute("SELECT DISTINCT case_id FROM case_documents")
print("Distinct case_ids in case_documents:", [r[0] for r in c.fetchall()])

c.execute("SELECT id, case_id, filename, title FROM case_documents LIMIT 10")
for r in c.fetchall():
    print("Doc:", r)
