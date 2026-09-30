import sqlite3

conn = sqlite3.connect('data/legalai_indian_legal_knowledge.db')
c = conn.cursor()
rows = c.execute('SELECT act_prefix, count(chunk_id), min(document_id) FROM indian_legal_chunks GROUP BY act_prefix').fetchall()
print('Chunk counts grouped by act_prefix:')
for r in rows:
    print(f'{r[0]:<28} | {r[1]:>4} chunks | doc_id={r[2]}')
