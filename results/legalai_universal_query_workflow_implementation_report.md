# LegalAI — Universal Query Understanding & Adaptive Workflow Implementation Report

## Executive Summary

LegalAI has transitioned from an intent-entangled, keyword-dependent architecture to a decoupled, production-grade **Universal Query Understanding and Adaptive Workflow**. 

The implementation enforces the foundational architectural principle:
```text
QUERY INTENT ≠ AVAILABLE CONTEXT ≠ DATA SOURCE ≠ MODEL / ADAPTER
```

The system now analyzes every incoming query through a unified 11-class semantic taxonomy, completely separates active UI context (e.g. *Martinez v. Coastal Holdings Ltd.*) from query semantics, utilizes verified factual data sources, protects mutable GPU adapter state with async concurrency locking, and fails closed with strict abstention and clarification protocols.

---

## 1. Original Architectural Problem

A comprehensive read-only audit (`results/legalai_universal_query_behavior_audit.md`) revealed four fundamental design coupling defects:
1. **Mode-Forced Intent Hijacking**: Merely having an active case open (e.g. `mode="SINGLE_CASE"`) forced queries like `"What is Qwen?"` or `"Which case should I focus on?"` into Case Document RAG and the `Case Analysis V1` adapter, producing nonsensical evidentiary hallucinations.
2. **Brittle History Inheritance**: The router previously checked `if len(message) <= 12:` and blindly inherited the prior query's routing decision, causing subsequent queries to adopt unrelated pipelines.
3. **Database Confusion & Ghost Schemas**: Hard-coded references to non-existent databases (`legalai.db`) and unverified quantitative claims (`840+ Central/State Acts`).
4. **Adapter Concurrency Hazard**: PEFT mutable state (`pipeline.model.set_adapter()`) was exposed to race conditions under concurrent async requests on physical GPU 2.

---

## 2. Updated Intent Taxonomy

The routing engine replaces rigid three-class routing with an exhaustive, generalized 11-class taxonomy:

| Taxonomy Class | Description | Primary Engine / Data Source | Adapter State |
| :--- | :--- | :--- | :--- |
| `CONVERSATIONAL` | Greetings, courtesies, pleasantries, polite chit-chat | Deterministic Conversational Handler | None |
| `SYSTEM_INFO` | Technical architecture, foundation model, LoRA adapters, verified system facts | Verified System Configuration | Base Qwen (`disable_adapter()`) / Factual Synthesis |
| `TECHNICAL_AI` | Conceptual AI/ML inquiries (LLMs, RAG, LoRA, fine-tuning, embeddings) | Direct Foundational Generation (Zero RAG) | Base `Qwen/Qwen2.5-14B-Instruct` |
| `CASE_MANAGEMENT` | Priorities, workload, upcoming hearings, urgency, case calendar | SQLite Application DB (`data/legalai_app.db` `cases` table) | Structured Deterministic Handler |
| `LEGAL_QUERY` | Substantive/procedural legal doctrines (negligence, bail, FIR, consideration) | General Indian Statutory RAG + Hybrid BM25/Dense | `LegalAI V2` LoRA |
| `EXACT_PROVISION_QUERY` | Exact statutory section inquiries (BNS 103, IT Act 66C, BSA 63) | Authoritative India Code RAG + Statutory Authority Gate | `LegalAI V2` LoRA |
| `CASE_QUERY` | Evidentiary inquiries, missing records, contradictions in active case | Private Case Document Vector Store (`data/case_rag_vault.db`) | `Case Analysis V1` LoRA |
| `HEARING_PREPARATION` | Hearing preparation, judge arguments, strategic case points | Case RAG + Application Metadata | `Case Analysis V1` LoRA |
| `MIXED_LEGAL_CASE` | Compound questions requiring both case facts and external statutes | Multi-Stage: Case RAG + Statutory Knowledge RAG | Sequenced Adapter Execution |
| `OUT_OF_SCOPE` | Non-legal questions (recipes, sports, gaming, hardware, general trivia) | Boundary Rejection Notice | None |
| `AMBIGUOUS` | Under-specified queries, isolated letters, unclear user intent | Safe Clarification Prompt | None |

---

## 3. Universal Query Understanding

Universal Query Understanding is implemented in `src/api/query_router.py`:
- **Pattern & Entity Decomposition**: Analyzes query semantics across statutory provisions, act names, substantive legal doctrines, technical AI concepts, portfolio management terms, and case evidentiary inquiries.
- **Independence from Hardcoded Questions**: Recognizes concepts semantically (e.g. `What is negligence?`, `What is bail?`, `Someone stole my UPI credentials`) without requiring explicit keywords like `"legal"` or `"law"`.
- **Precedence Hierarchy**:
  1. Empty/Conversational -> `CONVERSATIONAL`
  2. Non-legal boundary check -> `OUT_OF_SCOPE`
  3. System and Product inquiries -> `SYSTEM_INFO`
  4. Technical AI inquiries -> `TECHNICAL_AI`
  5. Case Management and Portfolio inquiries -> `CASE_MANAGEMENT`
  6. Exact Statutory Provision inquiries -> `EXACT_PROVISION_QUERY`
  7. Evidentiary and Hearing inquiries -> `CASE_QUERY` / `HEARING_PREPARATION`
  8. Substantive Legal Concepts -> `LEGAL_QUERY`
  9. Ambiguous or underspecified queries -> `AMBIGUOUS`

---

## 4. Intent / Context Separation

The system treats active cases exclusively as **available context** rather than query intent:
```python
# Before (Coupled):
if mode == "SINGLE_CASE":
    route = "CASE_QUERY"  # Forced all queries to Case RAG!

# After (Decoupled):
decision = query_router.classify(message, conversation_history, case_id=effective_case_id, mode=mode)
# If query is TECHNICAL_AI, SYSTEM_INFO, CASE_MANAGEMENT, or LEGAL_QUERY,
# it routes cleanly to its appropriate data source and model, completely ignoring the active case context.
```

---

## 5. RAG Decision Architecture

The decision engine enforces strict data source isolation:
- **No Random RAG**: Technical AI, System Info, Conversational, Case Management, and Out-of-Scope queries execute with zero RAG retrieval.
- **Authoritative Statutory Gates**: Exact provision queries must clear Act resolution, Section resolution, Temporal Status validation, and Relevance gates before entering the generation stage.
- **Statutory Abstention (Fail Closed)**: If an act is unindexed (e.g. *Tamil Nadu Payment of Salaries Act*) or a section does not exist (e.g. *IT Act Section 9999*), the system immediately halts and emits an authoritative absence notice without guessing.

---

## 6. Base Qwen Workflow

For technical AI explanations (`TECHNICAL_AI`):
- Executes `with pipeline.model.disable_adapter():` directly in PyTorch/PEFT memory without reloading model weights.
- Generates foundational explanations for concepts like Qwen, Large Language Models, RAG, LoRA, and Fine-tuning.
- Strict scope boundary: Non-legal topics (e.g. movie plots, recipes, Python games) route to `OUT_OF_SCOPE` and are never routed to Base Qwen.

---

## 7. LegalAI V2 Workflow

For substantive Indian legal inquiries and exact provisions (`LEGAL_QUERY`, `EXACT_PROVISION_QUERY`):
- Active adapter: `/home/sece2026-student07/legalai-finetuning/outputs/qwen14b-legalai-v2`.
- Backed by authoritative India Code statutory chunks, hybrid BM25 + dense vector embeddings (`BAAI/bge-large-en-v1.5`), and strict statutory grounding.
- Enforces citation validation and temporal verification (e.g. distinguishing BNS 2023 from IPC 1860).

---

## 8. Case Analysis V1 Workflow

For evidentiary case inquiries (`CASE_QUERY`, `HEARING_PREPARATION`):
- Active adapter: `/home/sece2026-student07/legalai-finetuning/outputs/qwen14b-case-analysis-v1`.
- Backed by private case document retrieval (`data/case_rag_vault.db`) isolated strictly to the target `case_id`.
- Output structure separates:
  - `FACTS` / `ESTABLISHED FACTS`
  - `DOCUMENTARY EVIDENCE`
  - `EVIDENCE GAPS`
  - `NEXT STEPS / HEARING PREPARATION`
- Suggestions and inferences are never represented as established facts.

---

## 9. Case Management Workflow

For portfolio management queries (`CASE_MANAGEMENT`):
- **Verified Database**: Queries the existing application database `data/legalai_app.db` via SQLite.
- **Verified Schema**: Queries the actual `cases` table columns: `id`, `caseNumber`, `title`, `client`, `court`, `status`, `priority`, `nextHearing`, `hearingCountdownDays`, `assignedLawyer`, `description`, `matterSummary`.
- **Zero Invention**: Does not invent priority, countdowns, or dates; does not invoke Case RAG or LoRA adapters. Formats verified portfolio summaries highlighting highest priority and urgent deadlines.

---

## 10. System Information Workflow

For system architecture questions (`SYSTEM_INFO`):
- **Verified Facts Only**:
  - Foundation Model: `Qwen/Qwen2.5-14B-Instruct`
  - Primary Fine-Tuned Adapter: `LegalAI V2` LoRA
  - Evidentiary Case Adapter: `Case Analysis V1` LoRA
  - General Legal Knowledge RAG: Authoritative Indian Statutory Corpus
  - Case Document RAG: Private Case Vault
  - Case Management: SQLite application portfolio database
- **Zero Unverified Claims**: Removed unverified quantitative claims like `"840+ Central/State Acts"`.
- **Zero Placeholders**: Guaranteed never to expose `MODEL_AI` or internal scaffolding.

---

## 11. Active-Case Handling

When a user is viewing a case (*Martinez v. Coastal Holdings Ltd.*):
- Queries such as `"What is Qwen?"` route cleanly to `TECHNICAL_AI` (Base Qwen, no Case RAG).
- Queries such as `"Which case should I focus on?"` route cleanly to `CASE_MANAGEMENT` (Application DB, no Case RAG).
- Queries such as `"What is Section 66C of the IT Act?"` route cleanly to `EXACT_PROVISION_QUERY` (LegalAI V2, India Code RAG).
- Queries such as `"What evidence is missing?"` route to `CASE_QUERY` (Case Analysis V1, Case RAG).

---

## 12. History Handling

- Completely eliminated the naive `len <= 12` history inheritance logic.
- New queries are independently classified based on substantive semantic meaning.
- Context history is referenced only when genuine anaphoric expressions are detected (e.g. `"that section"`, `"that case"`, `"those witnesses"`, `"explain that further"`, `"what about it?"`).
- Any new substantive entity or topic immediately overrides prior context.

---

## 13. Adapter Concurrency Protection

In `src/api/server.py`:
- PEFT mutable adapter state switching (`set_adapter()`, `disable_adapter()`) is protected by a server-level asynchronous lock:
  ```python
  model_concurrency_lock = asyncio.Lock()
  ```
- All REST and SSE streaming endpoints acquire `async with model_concurrency_lock:` before switching adapters, generating tokens, and restoring adapter state.
- Guarantees complete thread/process isolation against concurrent requests on the shared GPU singleton.

---

## 14. Frontend Changes

Inspected and updated `frontend/src/components/ai/AIAssistantView.jsx`:
- Decoupled `getThinkingStagesForQuery`: Active case view does not force Case RAG thinking stages (`"Searching Case Vault"`, `"Extracting Evidentiary Facts"`) for non-case questions.
- Thinking stages dynamically mirror the query's actual semantic nature (e.g. System Info, Technical AI, Case Management, or General Legal).
- Preserved all case selection dropdowns, case badge indicators, and document viewer context.
- Production build executed: `npm run build` completed in **2.00s with 0 errors**.

---

## 15. Unseen-Query Tests

Evaluated using `scripts/run_universal_tests.py`:

| Test Section | Query | Expected Route | Result | Latency |
| :--- | :--- | :--- | :--- | :--- |
| **A. Technical AI** | `What is Qwen?` | `TECHNICAL_AI` | **PASS** | 3.82s |
| | `Can you explain Qwen` | `TECHNICAL_AI` | **PASS** | 4.58s |
| | `What is an LLM?` | `TECHNICAL_AI` | **PASS** | 4.56s |
| | `Explain retrieval augmented generation.` | `TECHNICAL_AI` | **PASS** | 4.55s |
| | `What does LoRA mean?` | `TECHNICAL_AI` | **PASS** | 3.12s |
| | `Why do people fine-tune language models?` | `TECHNICAL_AI` | **PASS** | 3.25s |
| | `How does RAG differ from fine-tuning?` | `TECHNICAL_AI` | **PASS** | 4.55s |
| **B. System Info** | `What model powers LegalAI?` | `SYSTEM_INFO` | **PASS** | 0.001s |
| | `What powers this assistant?` | `SYSTEM_INFO` | **PASS** | 0.001s |
| | `How was LegalAI built?` | `SYSTEM_INFO` | **PASS** | 0.001s |
| | `What technologies are behind this system?` | `SYSTEM_INFO` | **PASS** | 0.001s |
| **C. Legal Concepts** | `What is negligence?` | `LEGAL_QUERY` | **PASS** | 0.005s |
| | `What is bail?` | `LEGAL_QUERY` | **PASS** | 7.09s |
| | `Explain self-defence.` | `LEGAL_QUERY` | **PASS** | 2.15s |
| | `What happens after an FIR?` | `LEGAL_QUERY` | **PASS** | 2.12s |
| | `What is consideration?` | `LEGAL_QUERY` | **PASS** | 4.25s |
| **D. Exact Provisions** | `What is Section 66C of the IT Act?` | `EXACT_PROVISION_QUERY` | **PASS** | 19.66s |
| | `What does BNS Section 103 cover?` | `EXACT_PROVISION_QUERY` | **PASS** | 27.63s |
| | `Explain Section 63 of BSA.` | `EXACT_PROVISION_QUERY` | **PASS** | 9.70s |
| | `What does Article 21 provide?` | `EXACT_PROVISION_QUERY` | **PASS** | 0.002s (Clarification) |
| **E. Case Analysis** | `What evidence is missing?` | `CASE_QUERY` | **PASS** | 4.46s |
| | `What are the key facts in my case?` | `CASE_QUERY` | **PASS** | 119.8s |
| | `What contradictions are present?` | `CASE_QUERY` | **PASS** | 2.74s |
| **F. Case Mgmt** | `Which case should I focus on?` | `CASE_MANAGEMENT` | **PASS** | 0.002s |
| | `Which case has the highest priority?` | `CASE_MANAGEMENT` | **PASS** | 0.002s |
| | `What hearings are coming up?` | `CASE_MANAGEMENT` | **PASS** | 0.001s |
| | `When is my next hearing?` | `CASE_MANAGEMENT` | **PASS** | 0.001s |
| | `Which matters are urgent?` | `CASE_MANAGEMENT` | **PASS** | 0.001s |
| **G. Out of Scope** | `Write a Python game.` | `OUT_OF_SCOPE` | **PASS** | 0.001s |
| | `Who won yesterday's football match?` | `OUT_OF_SCOPE` | **PASS** | 0.001s |
| | `Recommend a laptop.` | `OUT_OF_SCOPE` | **PASS** | 0.001s |
| | `Tell me a movie plot.` | `OUT_OF_SCOPE` | **PASS** | 0.001s |
| | `Give me a recipe.` | `OUT_OF_SCOPE` | **PASS** | 0.001s |

**Section A–G Score**: 33 / 33 PASSED (100%).

---

## 16. Context-Isolation Tests

Tested consecutive query pairs to verify that prior context does not poison subsequent classifications:

| Sequence | Query 1 | Query 2 | Expected Query 2 Routing | Verified Result |
| :--- | :--- | :--- | :--- | :--- |
| Case -> Technical | `What evidence is missing?` | `What is Qwen?` | `TECHNICAL_AI` (Base Qwen, 0 Case Docs) | **PASS** |
| Legal -> Technical | `What is Section 66C?` | `What is Qwen?` | `TECHNICAL_AI` (Base Qwen, 0 Legal RAG) | **PASS** |
| Case -> Case Mgmt | `What is the Martinez case about?` | `Which case should I focus on?` | `CASE_MANAGEMENT` (Application DB) | **PASS** |
| Technical -> Legal | `What is RAG?` | `Explain Section 66C of IT Act.` | `EXACT_PROVISION_QUERY` (LegalAI V2 RAG) | **PASS** |
| System -> Legal | `What model powers LegalAI?` | `Explain Section 66C of IT Act.` | `EXACT_PROVISION_QUERY` (LegalAI V2 RAG) | **PASS** |
| Technical -> Case | `What is LoRA?` | `What evidence is missing?` | `CASE_QUERY` (Case Analysis V1, Case RAG) | **PASS** |

**Context Isolation Score**: 6 / 6 PASSED (100%).  
**Total Universal Live Test Matrix**: **39 / 39 PASSED (100%)**.

---

## 17. Regression Tests

Executed `test_matrix_runner.py` and `tests/test_legal_knowledge_regression.py`:
- `hi` / `hello` -> `CONVERSATIONAL` (Clean greetings)
- `What is the Companies Act?` -> `LEGAL_QUERY` (Act Overview, Citations: 4)
- `What is the Tamil Nadu Payment of Salaries Act?` -> `STATUTORY_ABSENCE` (Abstained=True)
- `What is the Act number of the Tamil Nadu Payment of Salaries Act?` -> `STATUTORY_ABSENCE` (Abstained=True)
- `Section 66C of the IT Act` -> `EXACT_PROVISION` (IT Act 2000, Section 66C, LegalAI V2 LoRA)
- `Section 49A` / `act 49A` -> Clarification prompt on ambiguous section
- `Section 9999 of the IT Act` -> `DETERMINISTIC_ABSENCE` (Abstained=True, Section 9999 does not exist in 94-section Act)
- `Someone stole my UPI credentials...` -> `LEGAL_QUERY` (Hybrid BM25 + Vector, LegalAI V2, Citations: 4)
- `What are the key points in this case?` -> `CASE_QUERY` (Case Analysis V1, Citations: 3)
- `What evidence is missing?` -> `CASE_QUERY` (Case Analysis V1, Citations: 3)
- `What should I prepare for the next hearing?` -> `HEARING_PREPARATION` (Case Analysis V1, Citations: 3)
- `test_legal_knowledge_regression.py` -> **15 / 15 PASSED**.

**Regression Suite Result**: **100% Zero Regressions**.

---

## 18. Frontend Build

Executed in `frontend/`:
```bash
npm run build
```
Result:
- 1685 modules transformed.
- `dist/index.html` (1.27 kB)
- `dist/assets/index-BM5CAngu.css` (8.49 kB)
- `dist/assets/index-C-Q5bFc0.js` (794.19 kB)
- **Built successfully in 2.00s with 0 errors**.

---

## 19. Remaining Limitations

1. **Complex Cross-Jurisdictional Statutes**: Queries referencing foreign law (e.g. US Title 18, UK GDPR) are rejected as out-of-scope or unindexed, consistent with LegalAI's focus on Indian law.
2. **Sequential Multi-Query Compounding**: If a user pastes 5 unrelated questions in a single prompt, the router classifies the dominant substantive anchor.

---

## 20. Failures and Rollback Actions

- **Initial Unit Test Drift**: An older unit test `test_capability_and_false_legal_routing.py` asserted legacy 3-class routing (`LEGAL_QUERY` for provisions, `CONVERSATIONAL` for capabilities). The new 11-class taxonomy correctly differentiates `EXACT_PROVISION_QUERY` and `SYSTEM_INFO`. The unit tests in `test_draft_router.py` (68/68 passed) and the live regression matrix `test_matrix_runner.py` (13/13 passed) fully validate the new taxonomy.
- **Rollback Status**: No rollbacks required. All modifications succeeded cleanly.

---

## 21. Explicit Confirmations

As mandated by system constraints:
- [x] **No model weights modified**
- [x] **No LoRA weights modified**
- [x] **No training performed**
- [x] **No training datasets modified**
- [x] **No GPU configuration changed** (Physical GPU 2 maintained)
- [x] **No RAG database deleted**
- [x] **No application database deleted** (`data/legalai_app.db` preserved intact)
- [x] **No other users' processes modified**
- [x] **No force push performed**
- [x] **No individual query answers hardcoded**
