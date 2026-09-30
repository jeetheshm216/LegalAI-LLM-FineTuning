import sys
sys.path.insert(0, "/home/sece2026-student07/legalai-finetuning")
from src.legal_knowledge.indexing.database import IndianLegalDatabaseManager
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline

db = IndianLegalDatabaseManager()
chunk = db.get_chunk_by_provision("CPC_1908", "ORDER_39_RULE_1", provision_type="ORDER_RULE")
print("Direct DB chunk:", chunk.section_or_article if chunk else None)

pipeline = GeneralIndianLegalKnowledgePipeline()
res = pipeline.query("Explain Order 39 Rule 1 CPC")
print("Pipeline query response_type:", res.get("response_type"))
print("Sources count:", len(res.get("sources", [])))
if res.get("sources"):
    print("Source citation:", res["sources"][0]["citation"])

