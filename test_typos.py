import sys
import os
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.query_router import QueryRouter

r = QueryRouter()
queries = [
    "hwo are you",
    "what are you doing",
    "wow",
    "wat is sectoin 302 of bns",
    "drfat a petishun for property dispute"
]
for q in queries:
    res = r.classify(q)
    print(f"QUERY: '{q}' -> Intent: {res.intent.value}, Confidence: {res.confidence}")
