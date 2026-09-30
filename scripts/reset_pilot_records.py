import sqlite3
import os
import glob

db_path = "data/legalai_indian_legal_knowledge.db"
raw_dir = "data/raw/central_acts"

pilot_doc_ids = [
    "DOC_COMPANIES_ACT_2013",
    "DOC_IBC_2016",
    "DOC_ARBITRATION_ACT_1996",
    "DOC_CONSUMER_PROTECTION_ACT_2019",
    "DOC_TRANSFER_OF_PROPERTY_ACT_1882",
    "DOC_CPC_1908",
    "DOC_POCSO_ACT_2012",
    "DOC_PMLA_2002",
    "DOC_NDPS_ACT_1985",
    "DOC_SC_ST_POA_ACT_1989",
    "DOC_MOTOR_VEHICLES_ACT_1988",
    "DOC_SPECIFIC_RELIEF_ACT_1963",
]

conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Count before
total_docs_before = c.execute("SELECT count(*) FROM indian_legal_documents").fetchone()[0]
total_chunks_before = c.execute("SELECT count(*) FROM indian_legal_chunks").fetchone()[0]
print(f"Before reset: {total_docs_before} documents, {total_chunks_before} chunks")

# 2. Delete chunks for the 12 pilot Acts
placeholders = ",".join("?" * len(pilot_doc_ids))
del_chunks = c.execute(f"DELETE FROM indian_legal_chunks WHERE document_id IN ({placeholders})", pilot_doc_ids).rowcount
print(f"Deleted {del_chunks} old hardcoded pilot chunks")

# 3. Delete documents for the 12 pilot Acts
del_docs = c.execute(f"DELETE FROM indian_legal_documents WHERE document_id IN ({placeholders})", pilot_doc_ids).rowcount
print(f"Deleted {del_docs} old hardcoded pilot documents")

# 4. Clear ingestion tracker for pilot
del_tracker = c.execute("DELETE FROM indian_corpus_ingestion_state").rowcount
print(f"Reset {del_tracker} ingestion state tracker rows")

conn.commit()

# 5. Count after
total_docs_after = c.execute("SELECT count(*) FROM indian_legal_documents").fetchone()[0]
total_chunks_after = c.execute("SELECT count(*) FROM indian_legal_chunks").fetchone()[0]
print(f"After reset: {total_docs_after} documents, {total_chunks_after} chunks (Original 9 documents preserved: {total_chunks_after == 1111})")

conn.close()

# 6. Remove old snippet raw files
if os.path.exists(raw_dir):
    for f in glob.glob(os.path.join(raw_dir, "*")):
        os.remove(f)
    print(f"Cleared old raw snippet directory: {raw_dir}")
