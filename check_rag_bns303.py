import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.retrieval.hybrid_search import get_hybrid_retriever

retriever = get_hybrid_retriever()
query = "What is the definition and punishment for theft under BNS Section 303 compared to old IPC Section 378/379?"
results = retriever.search(query, top_k=5)

print(f"Total results: {len(results)}")
for i, r in enumerate(results):
    print(f"=== RESULT {i} (score: {r.score}) ===")
    print("Act:", r.metadata.get("act_title"))
    print("Section:", r.metadata.get("section_number"))
    print("Title:", r.metadata.get("section_title"))
    print("Content preview:")
    print(r.content[:500])
    print("-" * 50)
