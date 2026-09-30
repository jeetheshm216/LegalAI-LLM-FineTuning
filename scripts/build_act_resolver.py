import sqlite3
import re

conn = sqlite3.connect('data/legalai_indian_legal_knowledge.db')
c = conn.cursor()
docs = c.execute('SELECT document_id, title, act_prefix, legal_domain FROM indian_legal_documents').fetchall()

print('Document metadata:')
for d in docs:
    print(f'prefix: {d[2]}, title: {d[1]}')
