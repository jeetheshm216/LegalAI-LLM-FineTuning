import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.query_understanding.normalizer import QueryNormalizer

qn = QueryNormalizer()
s = "thiscase is about Section 66C and BNS 103"
shielded, protected = qn.protect_entities(s)
print("shielded:", shielded)
print("protected:", protected)
norm_text, protected_out = qn.normalize(s)
print("normalized:", norm_text)
