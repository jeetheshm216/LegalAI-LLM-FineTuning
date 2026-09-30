import sqlite3

conn = sqlite3.connect("/home/sece2026-student07/legalai-finetuning/data/legalai_rag_mvp.db")
c = conn.cursor()

print("--- Check BNS Section 303 in legal_sections ---")
c.execute("SELECT section_id, act_prefix, section_number, section_title, full_text FROM legal_sections WHERE act_prefix='BNS' AND section_number='303'")
row = c.fetchone()
if row:
    print("FOUND BNS 303 in legal_sections!")
    print("Section ID:", row[0])
    print("Title:", row[3])
    print("Full text length:", len(row[4]))
    print("Full text preview:")
    print(row[4][:600])
else:
    print("NOT FOUND BNS 303 in legal_sections!")
    c.execute("SELECT section_number, section_title FROM legal_sections WHERE act_prefix='BNS' AND (section_number LIKE '%303%' OR section_title LIKE '%theft%')")
    for r in c.fetchall():
        print("Related:", r)

print("\n--- Check BNS Section 303 in legal_chunks ---")
c.execute("SELECT chunk_id, act_prefix, section_number, section_title, content FROM legal_chunks WHERE act_prefix='BNS' AND section_number='303'")
chunks = c.fetchall()
print(f"Found {len(chunks)} chunks for BNS 303")
for ch in chunks:
    print("Chunk ID:", ch[0])
    print("Title:", ch[3])
    print("Content preview:")
    print(ch[4][:400])

print("\n--- Check BSA Section 63 in legal_sections ---")
c.execute("SELECT section_id, act_prefix, section_number, section_title, full_text FROM legal_sections WHERE act_prefix='BSA' AND section_number='63'")
row = c.fetchone()
if row:
    print("FOUND BSA 63 in legal_sections!")
    print("Section ID:", row[0])
    print("Title:", row[3])
    print("Full text length:", len(row[4]))
    print("Full text:")
    print(row[4])
else:
    print("NOT FOUND BSA 63 in legal_sections!")

print("\n--- Check BSA Section 63 in legal_chunks ---")
c.execute("SELECT chunk_id, act_prefix, section_number, section_title, content FROM legal_chunks WHERE act_prefix='BSA' AND section_number='63'")
chunks = c.fetchall()
print(f"Found {len(chunks)} chunks for BSA 63")
for ch in chunks:
    print("Chunk ID:", ch[0])
    print("Content preview:")
    print(ch[4])
