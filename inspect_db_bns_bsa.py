import sqlite3
from pathlib import Path

db_path = Path("/home/sece2026-student07/legalai-finetuning/data/legalai_rag_mvp.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("--- TABLES ---")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print(tables)

for table in tables:
    if "statute" in table.lower() or "section" in table.lower() or "act" in table.lower() or "chunk" in table.lower():
        print(f"\nTable: {table}")
        c.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in c.fetchall()]
        print("Columns:", cols)

print("\n--- SEARCH BNS Section 303 ---")
# Try searching for section 303 in any relevant table
for table in tables:
    try:
        c.execute(f"SELECT * FROM {table} WHERE section_number='303' OR section_number LIKE '%303%' LIMIT 5")
        rows = c.fetchall()
        if rows:
            print(f"Found in {table}: {len(rows)} rows")
            for r in rows:
                print(r[:8])
    except Exception as e:
        pass

print("\n--- SEARCH BSA Section 63 ---")
for table in tables:
    try:
        c.execute(f"SELECT * FROM {table} WHERE section_number='63' OR section_number LIKE '%63%' LIMIT 5")
        rows = c.fetchall()
        if rows:
            print(f"Found in {table}: {len(rows)} rows")
            for r in rows:
                print(r[:8])
    except Exception as e:
        pass
