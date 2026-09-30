import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.rag.integration.rag_legalai import LegalAIRAGPipeline

pipeline = LegalAIRAGPipeline(
    db_path="/home/sece2026-student07/legalai-finetuning/data/legalai_rag_mvp.db",
    base_model_name="Qwen/Qwen2.5-14B-Instruct",
    adapter_dir="/home/sece2026-student07/legalai-finetuning/outputs/qwen14b-legalai-v2",
    device="cuda:0"
)

q1 = "What is the definition and punishment for theft under BNS Section 303 compared to old IPC Section 378/379?"
domain_res = pipeline.domain_detector.detect(q1)

raw_cands = pipeline.retriever.retrieve(
    query=q1,
    act_filter=domain_res.statute_code,
    section_filter=domain_res.specific_provision,
    mode="hybrid",
    top_k=5
)

print("First candidate attributes:", dir(raw_cands[0]))
print("First candidate dict:", raw_cands[0].__dict__ if hasattr(raw_cands[0], '__dict__') else raw_cands[0])
for i, c in enumerate(raw_cands):
    text_val = getattr(c, 'text', getattr(c, 'content', getattr(c, 'raw_text', '')))
    print(f"\n--- Cand {i} (len: {len(text_val)}) ---")
    print("Act:", getattr(c, 'act_name', getattr(c, 'act', '')))
    print("Section:", getattr(c, 'section_number', getattr(c, 'section', '')))
    print("Text snippet:\n", repr(text_val[:300]))

# Check what prompt is built!
from src.rag.integration.grounded_prompt import build_grounded_prompt
gate_res = pipeline.relevance_gate.evaluate_candidates(
    query=q1,
    candidates=raw_cands,
    target_domain=domain_res.detected_domain,
    target_statute_code=domain_res.statute_code,
    target_section=domain_res.specific_provision
)
prompt_ctx = build_grounded_prompt(
    question=q1,
    retrieved_chunks=gate_res.filtered_chunks,
    evidence_status="ANSWERABLE"
)
print("\n" + "=" * 50)
print("USER PROMPT GIVEN TO LLM:")
print(prompt_ctx.user_prompt)
