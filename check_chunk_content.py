import sqlite3
conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db")
c = conn.cursor()
c.execute("SELECT chunk_id, section_or_article, provision_number, provision_title, content FROM indian_legal_chunks WHERE chunk_id = 'CPC_1908_FIRST_SCH_RULE_1_64'")
r = c.fetchone()
print("ID:", r[0])
print("Sec:", r[1])
print("ProvNum:", r[2])
print("Title:", r[3])
print("Content:\n", r[4][:500])

