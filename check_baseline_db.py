import sqlite3

for path in ['data/legalai_app.db', 'data/legalai_case_rag.db']:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"=== {path} ===")
    for t in tables:
        cnt = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  {t}: {cnt} rows")
    conn.close()
