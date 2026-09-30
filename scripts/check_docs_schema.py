import sqlite3

conn_app = sqlite3.connect("data/legalai_app.db")
cur_app = conn_app.cursor()
print("=== DOCUMENTS TABLE SCHEMA ===")
for col in cur_app.execute("PRAGMA table_info(documents)").fetchall():
    print(col)

print("\n=== SAMPLE DOCUMENTS ===")
for r in cur_app.execute("SELECT * FROM documents LIMIT 5").fetchall():
    print(r)
