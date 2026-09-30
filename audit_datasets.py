import json
import re
from collections import Counter
import hashlib

def analyze_file(filepath, label):
    total = 0
    parse_errors = 0
    empty_content = 0
    truncated_ends = 0
    unique_user_queries = set()
    unique_pairs = set()
    
    user_lens = []
    asst_lens = []
    
    has_markdown_headers = 0
    has_bullets = 0
    has_statute_citations = 0
    has_case_citations = 0
    ends_with_punctuation = 0
    
    statutes_mentioned = Counter()
    
    sample_truncated = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                data = json.loads(line)
            except Exception as e:
                parse_errors += 1
                continue
                
            messages = data.get("messages", [])
            user_msg = ""
            asst_msg = ""
            for m in messages:
                if m.get("role") == "user":
                    user_msg = m.get("content", "")
                elif m.get("role") == "assistant":
                    asst_msg = m.get("content", "")
                    
            if not user_msg or not asst_msg:
                empty_content += 1
                continue
                
            u_words = len(user_msg.split())
            a_words = len(asst_msg.split())
            user_lens.append(u_words)
            asst_lens.append(a_words)
            
            u_hash = hashlib.md5(user_msg.strip().lower().encode()).hexdigest()
            p_hash = hashlib.md5((user_msg.strip() + "|||" + asst_msg.strip()).lower().encode()).hexdigest()
            unique_user_queries.add(u_hash)
            unique_pairs.add(p_hash)
            
            # Check punctuation and truncation
            stripped_asst = asst_msg.strip()
            if stripped_asst and stripped_asst[-1] in ('.', '!', '?', '"', "'", ')', '`'):
                ends_with_punctuation += 1
            else:
                truncated_ends += 1
                if len(sample_truncated) < 3:
                    sample_truncated.append((idx, user_msg[:80], asst_msg[-120:]))
                    
            # Check structure
            if re.search(r'^#{1,4}\s', asst_msg, re.MULTILINE):
                has_markdown_headers += 1
            if re.search(r'^\s*[-*•]\s|\n\s*\d+\.\s', asst_msg):
                has_bullets += 1
            if re.search(r'\b(section|sec\.?|article|art\.?)\s+\d+', asst_msg, re.IGNORECASE):
                has_statute_citations += 1
            if re.search(r'\b(v\.|versus|scc|air|scr|bom\s+cr)\b', asst_msg, re.IGNORECASE):
                has_case_citations += 1
                
            # Statutes
            for st in ["BNS", "BNSS", "BSA", "IPC", "CrPC", "Evidence Act", "IT Act", "DPDP", "Arbitration", "Contract Act", "Companies Act", "CPC", "Constitution"]:
                if re.search(rf'\b{st}\b', asst_msg, re.IGNORECASE):
                    statutes_mentioned[st] += 1

    return {
        "label": label,
        "total": total,
        "parse_errors": parse_errors,
        "empty_content": empty_content,
        "unique_queries": len(unique_user_queries),
        "unique_pairs": len(unique_pairs),
        "dup_queries": total - len(unique_user_queries),
        "dup_pairs": total - len(unique_pairs),
        "avg_user_words": sum(user_lens) / len(user_lens) if user_lens else 0,
        "avg_asst_words": sum(asst_lens) / len(asst_lens) if asst_lens else 0,
        "min_asst_words": min(asst_lens) if asst_lens else 0,
        "max_asst_words": max(asst_lens) if asst_lens else 0,
        "short_answers_pct": sum(1 for w in asst_lens if w < 30) / len(asst_lens) * 100 if asst_lens else 0,
        "deep_answers_pct": sum(1 for w in asst_lens if w >= 80) / len(asst_lens) * 100 if asst_lens else 0,
        "truncated_ends": truncated_ends,
        "truncated_pct": truncated_ends / total * 100 if total else 0,
        "ends_with_punct_pct": ends_with_punctuation / total * 100 if total else 0,
        "has_markdown_headers_pct": has_markdown_headers / total * 100 if total else 0,
        "has_bullets_pct": has_bullets / total * 100 if total else 0,
        "has_statute_citations_pct": has_statute_citations / total * 100 if total else 0,
        "has_case_citations_pct": has_case_citations / total * 100 if total else 0,
        "statutes": dict(statutes_mentioned.most_common(10)),
        "sample_truncated": sample_truncated
    }

def check_overlap(path_final, path_total):
    def get_queries(path):
        q = {}
        with open(path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                if not line.strip(): continue
                try:
                    d = json.loads(line)
                    for m in d.get("messages", []):
                        if m.get("role") == "user":
                            q[m.get("content", "").strip().lower()] = idx
                except:
                    pass
        return q

    q_final = get_queries(path_final)
    q_total = get_queries(path_total)
    
    in_both = set(q_final.keys()).intersection(set(q_total.keys()))
    only_final = set(q_final.keys()) - set(q_total.keys())
    only_total = set(q_total.keys()) - set(q_final.keys())
    
    return {
        "final_queries": len(q_final),
        "total_queries": len(q_total),
        "common_queries": len(in_both),
        "only_in_final": len(only_final),
        "only_in_total": len(only_total),
        "final_subset_of_total_pct": len(in_both) / len(q_final) * 100 if q_final else 0
    }

if __name__ == "__main__":
    res_final = analyze_file("/data/user/sece2026-student07/Legal_dataset_final.jsonl", "Legal_dataset_final")
    res_total = analyze_file("/data/user/sece2026-student07/Legal_dataset_total.jsonl.txt", "Legal_dataset_total")
    overlap = check_overlap("/data/user/sece2026-student07/Legal_dataset_final.jsonl", "/data/user/sece2026-student07/Legal_dataset_total.jsonl.txt")
    
    print("=== RESULTS ===")
    print(json.dumps({"final": res_final, "total": res_total, "overlap": overlap}, indent=2))
