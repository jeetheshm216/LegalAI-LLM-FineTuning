import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Enforce cuda:2
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

import torch
from src.rag.integration.rag_legalai import LegalAIRAGPipeline
from src.case_rag import CaseRAGPipeline
from src.api.server import (
    generate_conversational_response,
    generate_out_of_scope_response,
)
from src.api.query_router import QueryRouter, QueryIntent

def run_e2e_evaluation():
    print("=" * 80)
    print("STARTING END-TO-END MULTI-TURN CONVERSATIONAL & CASE EVALUATION ON CUDA:2")
    print("=" * 80)

    print("\n1. Initializing Base Pipeline (Qwen2.5-14B-Instruct) on cuda:2...")
    t0 = time.time()
    # Ingest index path
    pipeline = LegalAIRAGPipeline(
        db_path=str(REPO_ROOT / "data" / "legalai_rag_mvp.db"),
        base_model_name="Qwen/Qwen2.5-14B-Instruct",
        adapter_dir=str(REPO_ROOT / "outputs" / "qwen14b-legalai-v2"),
        device="cuda:0"
    )
    pipeline.load_model()

    case_v1_path = str(REPO_ROOT / "outputs" / "qwen14b-case-analysis-v1")
    if os.path.exists(case_v1_path) and hasattr(pipeline.model, "load_adapter"):
        try:
            pipeline.model.load_adapter(case_v1_path, adapter_name="case_analysis_v1")
            pipeline.model.set_adapter("default")
            print("Successfully registered 'case_analysis_v1' adapter on model singleton.")
        except Exception as e:
            print(f"Warning loading case_analysis_v1 adapter: {e}")

    from src.case_rag import CaseEmbedder
    case_embedder = CaseEmbedder(existing_model=pipeline.embedder.model)
    case_rag = CaseRAGPipeline(
        index_db_path=str(REPO_ROOT / "data" / "legalai_case_rag.db"),
        base_pipeline=pipeline,
        embedder=case_embedder
    )
    router = QueryRouter()
    print(f"Pipeline initialized in {time.time() - t0:.2f}s")

    conversation_history = []

    # TURN 1: Meta question about chatbot behavior
    turn1_query = "Why aren't you working as a normal chatbot?"
    print(f"\n--- TURN 1: Meta Query ---")
    print(f"User: {turn1_query}")
    decision1 = router.classify(turn1_query, conversation_history=conversation_history)
    print(f"Router Decision: Intent={decision1.intent.value}, SubIntent={decision1.sub_intent}")
    assert decision1.intent == QueryIntent.CONVERSATIONAL

    t_start = time.time()
    turn1_resp = generate_conversational_response(
        pipeline=pipeline,
        message=turn1_query,
        history=conversation_history,
        max_new_tokens=256
    )
    t_gen = time.time() - t_start
    print(f"LegalAI ({t_gen:.2f}s):\n{turn1_resp}\n")
    assert len(turn1_resp) > 50
    assert any(term in turn1_resp.lower() for term in ["legal", "specialized", "assistant", "indian"])

    conversation_history.append({"role": "user", "content": turn1_query, "query_type": decision1.intent.value})
    conversation_history.append({"role": "assistant", "content": turn1_resp, "query_type": decision1.intent.value})

    # TURN 2: Capability inquiry
    turn2_query = "What can you do?"
    print(f"\n--- TURN 2: Capability Query ---")
    print(f"User: {turn2_query}")
    decision2 = router.classify(turn2_query, conversation_history=conversation_history)
    print(f"Router Decision: Intent={decision2.intent.value}, SubIntent={decision2.sub_intent}")
    assert decision2.intent == QueryIntent.CONVERSATIONAL

    t_start = time.time()
    turn2_resp = generate_conversational_response(
        pipeline=pipeline,
        message=turn2_query,
        history=conversation_history,
        max_new_tokens=256
    )
    t_gen = time.time() - t_start
    print(f"LegalAI ({t_gen:.2f}s):\n{turn2_resp}\n")
    assert len(turn2_resp) > 50

    conversation_history.append({"role": "user", "content": turn2_query, "query_type": decision2.intent.value})
    conversation_history.append({"role": "assistant", "content": turn2_resp, "query_type": decision2.intent.value})

    # TURN 3: Non-legal out-of-scope query
    turn3_query = "Can you give me a recipe for chocolate cake?"
    print(f"\n--- TURN 3: Out-of-Scope Query ---")
    print(f"User: {turn3_query}")
    decision3 = router.classify(turn3_query, conversation_history=conversation_history)
    print(f"Router Decision: Intent={decision3.intent.value}, SubIntent={decision3.sub_intent}")
    assert decision3.intent == QueryIntent.OUT_OF_SCOPE

    turn3_resp = generate_out_of_scope_response(turn3_query, history=conversation_history)
    print(f"LegalAI:\n{turn3_resp}\n")
    expected_redirection = (
        "I am a Legal AI assistant. I can only assist with legal matters, case analysis, "
        "and legal research. If you have any legal related questions or cases to discuss, we can discuss that."
    )
    assert turn3_resp == expected_redirection

    conversation_history.append({"role": "user", "content": turn3_query, "query_type": decision3.intent.value})
    conversation_history.append({"role": "assistant", "content": turn3_resp, "query_type": decision3.intent.value})

    # TURN 4: Case Query (Martinez Matter)
    turn4_query = "What is the core contractual dispute regarding the port authority strike in this matter?"
    case_id = "2024-CV-1187"
    print(f"\n--- TURN 4: Case Analysis Query ---")
    print(f"User: {turn4_query} (Case: {case_id})")
    decision4 = router.classify(turn4_query, conversation_history=conversation_history, case_id=case_id)
    print(f"Router Decision: Intent={decision4.intent.value}, SubIntent={decision4.sub_intent}")
    assert decision4.intent == QueryIntent.CASE_QUERY

    t_start = time.time()
    res4 = case_rag.answer_case_question(
        question=turn4_query,
        case_id=case_id,
        conversation_history=conversation_history,
        top_k=6,
        max_new_tokens=384
    )
    t_gen = time.time() - t_start
    print(f"LegalAI ({t_gen:.2f}s):\n{res4.answer}\n")
    assert len(res4.answer) > 50

    conversation_history.append({"role": "user", "content": turn4_query, "query_type": decision4.intent.value})
    conversation_history.append({"role": "assistant", "content": res4.answer, "query_type": decision4.intent.value})

    # TURN 5: Reformatting previous response clearly as bullet points
    turn5_query = "Can you explain the previous response clearly and format it as bullet points?"
    print(f"\n--- TURN 5: Reformatting Follow-up Query ---")
    print(f"User: {turn5_query}")
    decision5 = router.classify(turn5_query, conversation_history=conversation_history, case_id=case_id)
    print(f"Router Decision: Intent={decision5.intent.value}, SubIntent={decision5.sub_intent}")
    assert decision5.intent == QueryIntent.CASE_QUERY

    t_start = time.time()
    res5 = case_rag.answer_case_question(
        question=turn5_query,
        case_id=case_id,
        conversation_history=conversation_history,
        top_k=6,
        max_new_tokens=384
    )
    t_gen = time.time() - t_start
    print(f"LegalAI ({t_gen:.2f}s):\n{res5.answer}\n")
    assert len(res5.answer) > 50
    # Must contain bullet points
    assert "•" in res5.answer or "-" in res5.answer or "*" in res5.answer

    conversation_history.append({"role": "user", "content": turn5_query, "query_type": decision5.intent.value})
    conversation_history.append({"role": "assistant", "content": res5.answer, "query_type": decision5.intent.value})

    # TURN 6: Multi-turn Recall of Turn 1
    turn6_query = "From the start of our chat, what was the first question I asked you?"
    print(f"\n--- TURN 6: Multi-Turn Conversation Memory Recall ---")
    print(f"User: {turn6_query}")
    decision6 = router.classify(turn6_query, conversation_history=conversation_history, case_id=case_id)
    print(f"Router Decision: Intent={decision6.intent.value}, SubIntent={decision6.sub_intent}")

    t_start = time.time()
    res6 = case_rag.answer_case_question(
        question=turn6_query,
        case_id=case_id,
        conversation_history=conversation_history,
        top_k=4,
        max_new_tokens=256
    )
    t_gen = time.time() - t_start
    print(f"LegalAI ({t_gen:.2f}s):\n{res6.answer}\n")
    assert "normal chatbot" in res6.answer.lower() or "first question" in res6.answer.lower() or "working" in res6.answer.lower()

    print("\n" + "=" * 80)
    print("ALL 6 MULTI-TURN END-TO-END EVALUATION TESTS PASSED PERFECTLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_e2e_evaluation()
