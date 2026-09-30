import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.query_router import UniversalQueryRouter

router = UniversalQueryRouter()
q = "Do I have another case with a similar issue?"
dec = router.classify(q, case_id="case-01")
print("Query:", q)
print("Normalized:", dec.normalized_query)
print("Intent:", dec.intent)
print("SubIntent:", dec.sub_intent)
print("OutputPlan:", dec.output_plan)
print("Reason:", dec.reason)
