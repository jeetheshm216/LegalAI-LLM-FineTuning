import sqlite3

conn = sqlite3.connect('data/legalai_indian_legal_knowledge.db')
c = conn.cursor()
rows = c.execute('SELECT document_id, title, act_prefix, legal_domain FROM indian_legal_documents ORDER BY act_prefix').fetchall()
print(f'Total documents: {len(rows)}')
for r in rows:
    count = c.execute('SELECT count(chunk_id) FROM indian_legal_chunks WHERE document_id=?', (r[0],)).fetchone()[0]
    print(f'{r[2]:<26} | {count:>4} chunks | {r[3]:<22} | {r[1]}')
