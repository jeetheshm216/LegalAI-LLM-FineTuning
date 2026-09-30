import re
import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')

TYPO_MAP = [
    (r'\bhwo\b', 'how'),
    (r'\bwat\b', 'what'),
    (r'\bwht\b', 'what'),
    (r'\bwats\b', 'what is'),
    (r'\bteh\b', 'the'),
    (r'\byuo\b', 'you'),
    (r'\bdrfat\b', 'draft'),
    (r'\bdarf\b', 'draft'),
    (r'\bdaft\b', 'draft'),
    (r'\bpetishun\b', 'petition'),
    (r'\bpetitin\b', 'petition'),
    (r'\bsectoin\b', 'section'),
    (r'\bseciton\b', 'section'),
    (r'\bproperti\b', 'property'),
    (r'\bpropety\b', 'property'),
    (r'\bdisput\b', 'dispute'),
    (r'\bdisptue\b', 'dispute'),
]

def normalize_typos(text: str) -> str:
    res = text
    for pat, repl in TYPO_MAP:
        res = re.sub(pat, repl, res, flags=re.IGNORECASE)
    return res

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
    norm = normalize_typos(q)
    res = r.classify(norm)
    print(f"RAW: '{q}' -> NORM: '{norm}' -> Intent: {res.intent.value}, Confidence: {res.confidence}")
