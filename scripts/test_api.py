#!/usr/bin/env python3
import json
import os
from collections import defaultdict, Counter

print("=== 1. IndicLegalQA Inspection ===")
indic_path = "data/external/raw/indiclegalqa/indiclegalqa.json"
if os.path.exists(indic_path):
    with open(indic_path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    print(f"IndicLegalQA items: {len(obj)}")
    case_map = defaultdict(list)
    for it in obj:
        case_name = it.get("case_name") or it.get("title") or it.get("source_judgment") or "UNKNOWN"
        case_map[case_name].append(it)
    print(f"Distinct cases in IndicLegalQA: {len(case_map)}")
    sample_case = list(case_map.keys())[0]
    print(f"Sample case: {sample_case} has {len(case_map[sample_case])} Q&A items")
    for q in case_map[sample_case][:5]:
        print("  Q:", q.get("question"))
        print("  A:", q.get("answer"))

print("\n=== 2. Realistic Lawyer Queries Inspection ===")
rq_path = "data/external/normalized/legalai_1000_realistic_lawyer_queries.jsonl"
if os.path.exists(rq_path):
    cases = set()
    total = 0
    with open(rq_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            total += 1
            r = json.loads(line)
            cases.add(r.get("source_document") or r.get("id"))
            if i < 2:
                print(f"  Item {i}: Q={r.get('question')[:80]} | Practice={r.get('practice_area')}")
    print(f"Total realistic queries: {total}, distinct documents/contexts: {len(cases)}")

print("\n=== 3. Legal Queries Data Inspection ===")
lqd_path = "data/external/normalized/legal_queries_data.jsonl"
if os.path.exists(lqd_path):
    total = 0
    with open(lqd_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            total += 1
            r = json.loads(line)
            if i < 2:
                print(f"  Item {i}: Q={r.get('question')[:80]} | Practice={r.get('practice_area')}")
    print(f"Total legal queries data: {total}")
