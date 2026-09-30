import sqlite3

conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db")
c = conn.cursor()

# Map Order 39 Rule 1
c.execute("""
UPDATE indian_legal_chunks
SET provision_number = 'ORDER_39_RULE_1',
    section_or_article = 'Order XXXIX Rule 1',
    provision_title = 'Order XXXIX Rule 1: Cases in which temporary injunction may be granted.',
    provision_type = 'ORDER_RULE'
WHERE chunk_id = 'CPC_1908_FIRST_SCH_RULE_1_64'
""")

# Map Order 7 Rule 11
c.execute("""
UPDATE indian_legal_chunks
SET provision_number = 'ORDER_7_RULE_11',
    section_or_article = 'Order VII Rule 11',
    provision_title = 'Order VII Rule 11: Rejection of plaint.',
    provision_type = 'ORDER_RULE'
WHERE chunk_id = 'CPC_1908_FIRST_SCH_RULE_11_5'
""")

conn.commit()

# Verify
c.execute("SELECT chunk_id, section_or_article, provision_number, provision_type, provision_title FROM indian_legal_chunks WHERE provision_number IN ('ORDER_39_RULE_1', 'ORDER_7_RULE_11')")
for r in c.fetchall():
    print("Mapped row:", r)

conn.close()

