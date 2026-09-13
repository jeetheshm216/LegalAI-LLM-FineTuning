# Root Cause Analysis: LegalAI RAG MVP Failure Modes & False Domain Hallucinations

**Date:** September 13, 2026  
**Project:** `/home/sece2026-student07/legalai-finetuning`  
**Inspected Components:**
- `src/rag/retrieval/retriever.py`
- `src/rag/database/sqlite_adapter.py`
- `src/rag/integration/rag_legalai.py`
- `src/rag/integration/grounded_prompt.py`
- `data/legalai_rag_mvp.db` (BNS 2023, BNSS 2023, BSA 2023 only)
- `results/legal_eval_125_v2_rag_results.jsonl`

---

## 1. Executive Diagnosis

The Legal RAG MVP database currently indexes **exactly three criminal enactments**:
1. Bharatiya Nyaya Sanhita, 2023 (BNS) — 358 sections
2. Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) — 531 sections
3. Bharatiya Sakshya Adhiniyam, 2023 (BSA) — 170 sections
Total: 1,059 statutory sections across 1,089 chunks.

However, the 125-question evaluation benchmark (`data/legal_eval_125.jsonl`) is a comprehensive cross-discipline benchmark spanning 15 distinct legal fields:
- Constitutional Law (15 questions)
- Contract Law (10 questions)
- Property & Tenancy Law (8 questions)
- Consumer Protection Law (8 questions)
- Cyber & IT Law (8 questions)
- Family & Succession Law (7 questions)
- Company & Corporate Law (6 questions)
- Intellectual Property Law (5 questions)
- Labour & Industrial Law (4 questions)
- Arbitration & Civil Procedure (4 questions)
- Criminal & Evidence Law (28 questions)
- Hallucination & Trap Detection (5 questions)
- Real-world & Cross-domain (17 questions)

Over **70% of benchmark queries** concern statutes entirely absent from the 3-Act RAG corpus.

---

## 2. Nine Precise Code-Level Failure Points

### Point 1: Unconditional Nearest-Neighbor Vector Retrieval
In `src/rag/database/sqlite_adapter.py` (`search_vector`):
```python
doc_vec = np.frombuffer(blob, dtype=np.float32)
sim = float(np.dot(q_vec, doc_vec) / doc_norm)
candidates.append(item)
candidates.sort(key=lambda x: x["vector_score"], reverse=True)
return candidates[:limit]
```
Dense vector search calculates cosine similarity across all 1,089 stored chunks and returns the `top_k` highest cosine matches. Even when a query is completely out-of-domain (e.g. *"What does Article 21 protect?"* or *"What is Section 138 cheque bounce?"*), cosine similarity to some arbitrary criminal chunk (e.g. BNS §103 or BNS §316) is ~0.35–0.45. The retriever **never filters out low-similarity chunks**.

### Point 2: Blind Reciprocal Rank Fusion (RRF) Normalization
In `src/rag/retrieval/retriever.py` (`retrieve`):
```python
for rank, item in enumerate(vec_candidates, start=1):
    cid = item["chunk_id"]
    scores[cid] = scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
```
RRF discards raw similarity scores and assigns score based purely on ordinal rank: `1.0 / (60 + rank)` (approx. 0.016 for rank 1). As a consequence, completely unrelated chunks (cosine score 0.35) receive the exact same RRF score as a perfect pinpoint match (cosine score 0.95).

### Point 3: Absence of a Real Relevance / Evidence Gate
In `retriever.py`, there is **no threshold check**:
- No minimum dense cosine similarity threshold (e.g., `RAG_MIN_DENSE_SIMILARITY`).
- No minimum lexical BM25 threshold (e.g., `RAG_MIN_LEXICAL_SCORE`).
- No requirement of an Act or topic match.
As long as the database has chunks, `retriever.retrieve()` returns `top_k` chunks.

### Point 4: Mandatory Authority Mandate in Grounded Prompt
In `src/rag/integration/grounded_prompt.py`:
```text
MANDATORY RULES OF LEGAL REASONING:
1. PRIMARY STATUTORY GROUNDING:
   - Your answers must be strictly grounded in the provided authoritative legal provisions.
   - Treat the retrieved statutory text as the primary source of truth.
```
When unrelated BNS chunks are passed into the prompt, the model is commanded under Rule 1 to treat them as authoritative and ground its response in them.

### Point 5: Absence of Comprehensive Legal-Domain & Act Detection
In `src/rag/integration/rag_legalai.py`, `_extract_explicit_act_and_section` only recognizes BNS, BNSS, and BSA. An ad-hoc regex caught only 8 specific phrases (`income tax`, `companies act`, `gst`, `motor vehicles`, `cpc`, `arbitration`, `consumer protection`, `negotiable instruments`). Queries mentioning:
- "Article 21", "Article 19", "Article 32", "Fundamental Rights"
- "Contract Act", "Section 74", "Section 27", "liquidated damages"
- "IT Act", "Section 79", "intermediary liability"
- "RERA", "allottee", "builder delay"
- "DPDP", "data fiduciary", "consent manager"
- "RTI Act", "public information officer", "30 days"
- "Trade Marks Act", "Patents Act", "inventive step"
- "Payment of Gratuity", "Industrial Disputes"
bypassed detection, pulled arbitrary BNS/BNSS/BSA chunks, and forced the model into wrong-domain confabulation.

### Point 6: Naive Temporal Date Handling
In `src/rag/integration/rag_legalai.py`:
```python
elif effective_date and effective_date < "2024-07-01":
    status = "TEMPORAL_TRANSITION_APPLIED"
```
The pipeline only checked `effective_date` if explicitly passed as an argument. It did **not extract conduct dates** from the user's natural language query (e.g., *"theft allegedly took place on 15 June 2024"*). Without automated date extraction and substantive vs procedural classification, BNS was erroneously applied to conduct occurring prior to July 1, 2024, violating Article 20(1) non-retroactivity.

### Point 7: Binary Abstention Implementation
Previously, abstention only occurred if `retrieved_results` was strictly empty:
```python
if not retrieved_results and not concordance_mappings:
    answer_text = "The available legal sources do not provide sufficient information..."
```
Because vector search always returned chunks, `not retrieved_results` was almost never triggered for out-of-corpus queries, preventing justified abstentions.

### Point 8: Unverified Pinpoint Citations
In `src/rag/integration/rag_legalai.py`:
```python
citations = [format_legal_citation(r) for r in retrieved_results]
```
Citations were formatted from whatever chunks were retrieved, irrespective of whether the model used them or whether they were legally relevant to the question. No post-generation verification checked whether the generated answer's citations matched the retrieved context.

### Point 9: Binary Benchmark Rubric Penalizing Justified Abstention
In `scripts/run_v2_rag_benchmark.py`:
The keyword coverage rubric (`evaluate_response`) required lexical matches with the benchmark's substantive reference text. When the model correctly stated that an out-of-corpus statute was unavailable, completeness ratio was scored 0, collapsing correctness to 0/2. The evaluator failed to distinguish between an outright incorrect answer and a **justified, legally sound refusal due to corpus limitations**.

---

## 3. The 8-Stage Architecture Solution

```
USER QUESTION
      ↓
[Stage 1] Legal Domain & Explicit Statute Detection (Constitution, NI Act, IT Act, etc.)
      ↓
[Stage 2] Candidate Retrieval (FTS5 Lexical + Dense BGE-Large + RRF)
      ↓
[Stage 3] Relevance & Authority Gate (Thresholding: Cosine ≥ 0.60, Lexical BM25, Act Match)
      ↓
[Stage 4] Temporal Law Validation (Extract conduct date vs July 1, 2024; Article 20(1))
      ↓
[Stage 5] Evidence Sufficiency Classification
          (ANSWERABLE | PARTIALLY_ANSWERABLE | OUT_OF_CORPUS | TEMPORALLY_UNCERTAIN | LOW_RELEVANCE)
      ↓
[Stage 6] Grounded Prompt Assembly with Explicit Domain Boundaries
      ↓
[Stage 7] Deterministic Qwen V2 Generation (do_sample=False)
      ↓
[Stage 8] Post-Generation Citation & Hallucination Verification
      ↓
FINAL GROUNDED ANSWER OR CONTROLLED JUSTIFIED ABSTENTION
```

---

## 4. Immediate Implementation Path

1. **Relevance Gate:** Implement `RelevanceGate` filtering out sub-threshold chunks and enforcing domain consistency.
2. **Domain Detector:** Implement `LegalDomainDetector` mapping queries to target statutes and identifying out-of-corpus requests.
3. **Temporal Guard:** Implement `TemporalLawGuard` parsing incident dates and enforcing Article 20(1) non-retroactivity.
4. **Structured Abstention:** Provide clear, professional advocate explanations of corpus scope instead of generic errors.
5. **Post-Generation Citation Verifier:** Validate that all cited provisions exist in retrieved chunks.
6. **Multi-Class Evaluator:** Recognize `JUSTIFIED_ABSTENTION` and measure in-corpus accuracy, out-of-corpus handling, and wrong-domain retrieval.
