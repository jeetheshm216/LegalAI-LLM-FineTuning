import json
from collections import Counter

def check_other_datasets():
    datasets = [
        "/home/sece2026-student07/legalai-finetuning/data/case_analysis/case_analysis_train.jsonl",
        "/home/sece2026-student07/legalai-finetuning/data/legalai_1000_realistic_lawyer_queries.jsonl",
        "/home/sece2026-student07/legalai-finetuning/data/legal_train_v2.jsonl",
        "/home/sece2026-student07/legalai-finetuning/data/legal_eval_125.jsonl"
    ]
    
    for path in datasets:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                first = f.readline().strip()
                count = 1 + sum(1 for _ in f)
                d = json.loads(first)
                print(f"File: {path.split('/')[-1]}")
                print(f"  Count: {count}")
                print(f"  Keys: {list(d.keys())}")
                if "messages" in d:
                    u = [m['content'] for m in d['messages'] if m['role'] == 'user']
                    a = [m['content'] for m in d['messages'] if m['role'] == 'assistant']
                    print(f"  Sample User: {u[0][:100] if u else ''}")
                    print(f"  Sample Asst: {a[0][:120] if a else ''}")
                elif "instruction" in d:
                    print(f"  Sample Instruction: {d['instruction'][:100]}")
                    print(f"  Sample Output: {d.get('output', '')[:120]}")
                print("-" * 50)
        except Exception as e:
            print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    check_other_datasets()
