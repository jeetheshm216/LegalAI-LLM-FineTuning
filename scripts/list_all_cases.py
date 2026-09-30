import sqlite3

conn = sqlite3.connect("data/legalai_app.db")
cur = conn.cursor()
rows = cur.execute("SELECT id, caseNumber, title, client, court, caseType FROM cases").fetchall()
for r in rows:
    print(r)
