import sqlite3

conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_app.db")
c = conn.cursor()
rows = c.execute("SELECT id, caseNumber, title, client, court, priority, status, nextHearing, hearingCountdownDays, description FROM cases").fetchall()
for r in rows:
    print(r)
