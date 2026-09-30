import sqlite3

conn_app = sqlite3.connect("data/legalai_app.db")
cur = conn_app.cursor()
print(cur.execute("SELECT caseId, count(*) FROM documents GROUP BY caseId").fetchall())
