import time
import sys
from src.api.query_router import get_query_router

router = get_query_router()

queries = [
    "what are the key points in this case",
    "Summarize the established facts of this case using only the case documents.",
    "What evidence currently supports the client's position?",
    "What important evidence is missing or unclear from the current case file?",
    "Prepare me for the upcoming hearing based only on this case file."
]

for q in queries:
    t0 = time.time()
    print(f"Testing: {q}")
    res = router.classify(q)
    print(f"  Result: {res.intent} in {round(time.time() - t0, 4)}s (patterns: {res.matched_patterns})")

print("All queries routed successfully!")
