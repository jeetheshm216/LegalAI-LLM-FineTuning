import json
from collections import Counter
import re

def inspect_dataset(path):
    print(f"=== INSPECTING: {path} ===")
    total = 0
    keys = Counter()
    roles = Counter()
    topics = Counter()
    sample_items = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                item = json.loads(line)
                for k in item.keys():
                    keys[k] += 1
                    
                # Check messages format
                if "messages" in item:
                    msg_roles = tuple(m.get("role") for m in item["messages"])
                    roles[msg_roles] += 1
                    text_content = " ".join(m.get("content", "") for m in item["messages"])
                elif "prompt" in item and "completion" in item:
                    text_content = item["prompt"] + " " + item["completion"]
                elif "instruction" in item and "output" in item:
                    text_content = item["instruction"] + " " + item["output"]
                else:
                    text_content = str(item)
                    
                # Detect topics
                lower = text_content.lower()
                if "bns" in lower or "bharatiya nyaya" in lower:
                    topics["BNS (New Criminal Law)"] += 1
                if "bnss" in lower or "nagarik suraksha" in lower:
                    topics["BNSS (Criminal Procedure)"] += 1
                if "bsa" in lower or "sakshya" in lower:
                    topics["BSA (Evidence)"] += 1
                if "ipc" in lower or "indian penal code" in lower:
                    topics["IPC (Legacy Criminal)"] += 1
                if "crpc" in lower or "code of criminal procedure" in lower:
                    topics["CrPC (Legacy Procedure)"] += 1
                if "contract" in lower or "commercial" in lower or "charterparty" in lower or "lien" in lower:
                    topics["Contract / Commercial / Maritime"] += 1
                if "constitution" in lower or "fundamental right" in lower or "article" in lower:
                    topics["Constitutional Law"] += 1
                if "case" in lower or "hearing" in lower or "order" in lower or "petition" in lower or "plaintiff" in lower or "defendant" in lower:
                    topics["Court Practice / Case Analysis / Drafting"] += 1
                if "cyber" in lower or "it act" in lower or "online" in lower:
                    topics["Cybercrime & IT Law"] += 1

                if idx < 3:
                    sample_items.append(item)
            except Exception as e:
                pass
                
    print(f"Total entries: {total}")
    print(f"Top-level keys found: {dict(keys)}")
    print(f"Role structures: {dict(roles)}")
    print("\nTopic Breakdown:")
    for t, c in topics.most_common():
        print(f"  - {t}: {c} ({c/total*100:.1f}%)")
        
    print("\n--- SAMPLE 1 ---")
    print(json.dumps(sample_items[0], indent=2)[:800] if sample_items else "None")
    print("\n--- SAMPLE 2 ---")
    print(json.dumps(sample_items[1], indent=2)[:800] if len(sample_items) > 1 else "None")

if __name__ == "__main__":
    inspect_dataset("/data/user/sece2026-student07/Legal_dataset_final.jsonl")
    print("\n" + "="*70 + "\n")
    inspect_dataset("/data/user/sece2026-student07/Legal_dataset_total.jsonl.txt")
