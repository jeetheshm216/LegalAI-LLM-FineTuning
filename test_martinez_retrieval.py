import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.case_rag import CaseRAGPipeline, CaseEmbedder

p = CaseRAGPipeline("data/legalai_case_rag.db", CaseEmbedder())

queries = [
    "what are the key points in this case",
    "Summarize the established facts of this case using only the case documents.",
    "What evidence currently supports the client's position?",
    "What important evidence is missing or unclear from the current case file?",
    "Prepare me for the upcoming hearing based only on this case file."
]

for q in queries:
    chunks = p.retriever.retrieve(q, case_id="2024-CV-1187", top_k=3)
    print(f"\nQuery: '{q}' -> {len(chunks)} chunks:")
    for c in chunks:
        print(f"  [{c.document_name} p.{c.page_number}] score={c.score:.3f}: {c.text[:100]}...")

# Isolation check
other_chunks = p.retriever.retrieve("what are the key points in this case", case_id="case-live-test-01", top_k=5)
print(f"\nIsolation check: Querying 'case-live-test-01' for Martinez terms:")
for c in other_chunks:
    print(f"  [{c.document_name} p.{c.page_number}] (case={c.case_id})")
    assert "Martinez" not in c.text and "Charterparty" not in c.document_name
print("PASS: Case isolation between 2024-CV-1187 and case-live-test-01 verified!")
