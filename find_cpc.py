import sqlite3

conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db")
c = conn.cursor()

c.execute("SELECT chunk_id, section_or_article, provision_number, provision_type, provision_title FROM indian_legal_chunks WHERE act_prefix = 'CPC_1908' AND (content LIKE '%injunction%' OR provision_title LIKE '%injunction%') LIMIT 5")
rows = c.fetchall()
print(f"Total rows found: {len(rows)}")
for r in rows:
    print(r)

# Also check all provision_numbers in CPC that start with ORDER or FIRST_SCH
c.execute("SELECT provision_number, section_or_article, provision_type FROM indian_legal_chunks WHERE act_prefix = 'CPC_1908' AND provision_type = 'ORDER_RULE' LIMIT 10")
print("\nSample ORDER_RULE rows:")
for r in c.fetchall():
    print(r)

