import sys
sys.path.insert(0, '/data/user/sece2026-student07/legalai-finetuning')
from src.api.query_router import UniversalQueryRouter, QueryIntent

router = UniversalQueryRouter()
test_queries = [
    "hi",
    "hello",
    "thank you so much",
    "Write a Python program to check whether a number is odd or even",
    "what is bns 103",
    "what is the injunction order in this matter?",
    "what are the key facts of this case?",
]

for q in test_queries:
    res = router.classify(q, case_id="2024-CV-1187")
    print(f"Query: '{q}'")
    print(f"  -> Intent: {res.intent.value} (conf={res.confidence})")
    print(f"  -> Reason: {res.reason}")
    print(f"  -> Requires Case Docs: {res.requires_case_documents}")
