import sqlite3

for db_path, name in [
    ("data/legalai_case_rag.db", "Case RAG DB"),
    ("data/legalai_app.db", "App DB")
]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print("=" * 60)
    print(f"DATABASE: {name} ({db_path})")
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%_fts%'").fetchall()]
    for t in tables:
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"\nTable '{t}': columns = {cols}")
        rows = cur.execute(f"SELECT * FROM {t} LIMIT 5").fetchall()
        print(f"  Sample rows count: {len(rows)}")
        for r in rows[:3]:
            print(f"    {r[:5]}")
    conn.close()
