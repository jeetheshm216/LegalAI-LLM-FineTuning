import sqlite3
conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db")
c = conn.cursor()
c.execute("SELECT chunk_id, section_or_article, provision_number, provision_type, provision_title FROM indian_legal_chunks WHERE act_prefix = 'CPC_1908' AND (content LIKE '%injunction%' OR provision_title LIKE '%injunction%') LIMIT 5")
for r in c.fetchall():
    print(r)
