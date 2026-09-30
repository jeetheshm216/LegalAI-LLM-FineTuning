import re
from typing import Optional, List, Dict, Any

TYPO_RULES = [
    # Conversational / Greetings / Pronouns
    (r'\bhwo\b', 'how'),
    (r'\bwat\b', 'what'),
    (r'\bwht\b', 'what'),
    (r'\bwats\b', 'what is'),
    (r'\bteh\b', 'the'),
    (r'\byuo\b', 'you'),
    (r'\bu\b', 'you'),
    (r'\bur\b', 'your'),
    (r'\br\b', 'are'),
    (r'\bthx\b', 'thanks'),
    (r'\bplz\b', 'please'),
    (r'\bpls\b', 'please'),
    # Legal & Court Drafting
    (r'\bdrfat\b', 'draft'),
    (r'\bdarf\b', 'draft'),
    (r'\bdaft\b', 'draft'),
    (r'\bdrft\b', 'draft'),
    (r'\bpetishun\b', 'petition'),
    (r'\bpetitin\b', 'petition'),
    (r'\bpetiton\b', 'petition'),
    (r'\bptition\b', 'petition'),
    (r'\bsectoin\b', 'section'),
    (r'\bseciton\b', 'section'),
    (r'\bsction\b', 'section'),
    (r'\bproperti\b', 'property'),
    (r'\bpropety\b', 'property'),
    (r'\bproprty\b', 'property'),
    (r'\bdisput\b', 'dispute'),
    (r'\bdisptue\b', 'dispute'),
    (r'\bevidenc\b', 'evidence'),
    (r'\bevidense\b', 'evidence'),
    (r'\bwitnes\b', 'witness'),
    (r'\bwitniss\b', 'witness'),
    (r'\bstatut\b', 'statute'),
    (r'\bplaintif\b', 'plaintiff'),
    (r'\bdefendent\b', 'defendant'),
    (r'\bagrument\b', 'argument'),
    (r'\bargmnt\b', 'argument'),
    (r'\bjudgemnt\b', 'judgment'),
    (r'\bjudgmet\b', 'judgment'),
    (r'\bjurisdiciton\b', 'jurisdiction'),
    (r'\bjurisdcition\b', 'jurisdiction'),
    (r'\bchargeshit\b', 'chargesheet'),
    (r'\bchrgsheet\b', 'chargesheet'),
    (r'\binjunciton\b', 'injunction'),
    (r'\binjuntion\b', 'injunction'),
    (r'\badvocat\b', 'advocate'),
    (r'\blawer\b', 'lawyer'),
    (r'\bafidavit\b', 'affidavit'),
    (r'\baffidavt\b', 'affidavit')
]

def normalize_query_typos(query: str) -> str:
    res = query
    for pat, repl in TYPO_RULES:
        res = re.sub(pat, repl, res, flags=re.IGNORECASE)
    return res

test_queries = [
    "hwo are you",
    "what are you doing",
    "wow",
    "wat is sectoin 302 of bns",
    "drfat a petishun for properti disput",
    "how to prepare for hearng",
    "any contridiction in witnes statemnt"
]

for q in test_queries:
    print(f"ORIGINAL: '{q}' -> NORMALIZED: '{normalize_query_typos(q)}'")
