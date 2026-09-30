import sqlite3

conn = sqlite3.connect('/home/sece2026-student07/legalai-finetuning/data/legalai_app.db')
c = conn.cursor()

c.execute("SELECT caseId, count(*), group_concat(filename) FROM documents GROUP BY caseId")
for r in c.fetchall():
    print(f"Case: {r[0]:20} | Count: {r[1]} | Files: {r[2]}")
