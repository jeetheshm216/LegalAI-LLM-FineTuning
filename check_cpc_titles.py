import sqlite3
conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db")
c = conn.cursor()
c.execute("SELECT chunk_id, provision_number, provision_title FROM indian_legal_chunks WHERE act_prefix = 'CPC_1908' AND provision_type = 'ORDER_RULE' AND (provision_title LIKE '%injunction%' OR provision_title LIKE '%rejection of plaint%' OR provision_title LIKE '%ex parte%')")
for r in c.fetchall():
    print(r)

