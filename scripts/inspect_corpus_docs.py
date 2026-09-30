import sqlite3

conn = sqlite3.connect('/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db')
cur = conn.cursor()
rows = cur.execute('SELECT doc_id, short_title, act_prefix, legal_domain FROM indian_legal_documents').fetchall()
print(f'Total documents: {len(rows)}')
for r in rows:
    count = cur.execute('SELECT count(chunk_id) FROM indian_legal_chunks WHERE document_id=?', (r[0],)).fetchone()[0]
    print(f'  {r[0]}: prefix={r[2]}, domain={r[3]}, chunks={count} -> {r[1]}')
