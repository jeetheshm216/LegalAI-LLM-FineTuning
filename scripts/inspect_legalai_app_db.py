import sqlite3
import json

db_path = "/home/sece2026-student07/legalai-finetuning/data/legalai_app.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM cases")
print("Total cases in data/legalai_app.db:", c.fetchone()[0])

c.execute("PRAGMA table_info(cases)")
cols = [r[1] for r in c.fetchall()]
print("Schema columns:", cols)

c.execute("SELECT id, caseNumber, title, client, court, priority, status, nextHearing, hearingCountdownDays FROM cases")
for row in c.fetchall():
    print("Case:", dict(zip(["id", "caseNumber", "title", "client", "court", "priority", "status", "nextHearing", "hearingCountdownDays"], row)))

conn.close()
