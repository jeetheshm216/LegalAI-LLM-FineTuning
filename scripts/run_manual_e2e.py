"""Execute Phase 8: Manual End-to-End Tests for LegalAI RAG + V2 integration."""
import os
import json
import torch

from src.rag.integration.rag_legalai import answer_legal_question, LegalAIRAGPipeline

def run_manual_tests():
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"Visible GPU Count: {torch.cuda.device_count()}")
    if torch.cuda.is_available():
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")

    pipeline = LegalAIRAGPipeline(
        base_model_name="Qwen/Qwen2.5-14B-Instruct",
        adapter_dir="outputs/qwen14b-legalai-v2",
        device="cuda:0",
        db_path="data/legalai_rag_mvp.db"
    )

    questions = [
        {
            "id": 1,
            "question": "What is the punishment for murder under Section 103 of the BNS?",
            "act_filter": "BNS",
            "section_filter": "103"
        },
        {
            "id": 2,
            "question": "What provision of BNSS deals with anticipatory bail?",
            "act_filter": "BNSS",
            "section_filter": None
        },
        {
            "id": 3,
            "question": "Which BSA provision deals with admissibility of electronic records?",
            "act_filter": "BSA",
            "section_filter": None
        },
        {
            "id": 4,
            "question": "What law applies to a substantive offence committed on 15 June 2024?",
            "act_filter": None,
            "section_filter": None,
            "effective_date": "2024-06-15"
        },
        {
            "id": 5,
            "question": "What is BNS Section 999?",
            "act_filter": "BNS",
            "section_filter": "999"
        }
    ]

    results = []
    for q in questions:
        print(f"\n==================================================")
        print(f"RUNNING QUESTION {q['id']}: {q['question']}")
        print(f"==================================================")
        res = pipeline.answer_question(
            question=q["question"],
            act_filter=q["act_filter"],
            section_filter=q["section_filter"],
            effective_date=q.get("effective_date"),
            top_k=5,
            max_new_tokens=512
        )
        print(f"STATUS: {res['confidence_status']}")
        print(f"RETRIEVED SECTIONS: {[(s.get('act_code') or s.get('act_name')) + ' Sec ' + str(s.get('section_number')) for s in res['retrieved_sources']]}")
        print(f"CITATIONS: {res['citations']}")
        print(f"ANSWER:\n{res['answer']}\n")
        results.append({
            "test_id": q["id"],
            "question": q["question"],
            "result": res
        })

    os.makedirs("results", exist_ok=True)
    with open("results/manual_e2e_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nSaved manual test results to results/manual_e2e_results.json")

if __name__ == "__main__":
    run_manual_tests()
