# LegalAI Universal Query Behavior, Routing, RAG, Qwen & LoRA Root-Cause Audit Report

**Audit Date**: September 17, 2026  
**Auditor**: Antigravity AI Engineering (Autonomous Systems Root-Cause Analysis)  
**System Evaluated**: LegalAI Production Assistant (Qwen2.5-14B-Instruct + LegalAI V2 LoRA + Case Analysis V1 LoRA + General Indian Legal Knowledge Pipeline + Case Document RAG Subsystem)  
**Host Environment**: `college-gpu` (NVIDIA RTX B200 / Physical GPU 2, CUDA_VISIBLE_DEVICES=2, Port 8008)  
**Audit Scope**: Read-Only Comprehensive Architectural Diagnostic Audit (Zero Code/Model/Dataset/Corpus Modifications)

---

## 1. Executive Summary

A comprehensive, read-only architectural root-cause audit of the LegalAI assistant was executed to diagnose why questions spanning system/product details, case management, general AI knowledge, and conversation context exhibit severe routing failures, accidental Case RAG retrieval, context contamination, and improper abstentions.

### Core Findings:
1. **The Observed Defect (`MODEL_AI` on Martinez Case)**:
   When a user asked *"what is the model of legal ai"*, the system retrieved case documents from *Martinez v. Coastal Holdings Ltd.*, displayed *"Supported by case documents"*, and generated:
   > *"The supplied case material does not establish a specific model of legal AI used."*
   
   **Root Cause**: In `server.py`, the routing logic enforced:
   ```python
   is_case_mode = (req.mode == "SINGLE_CASE" and (effective_case_id or rag_case_id)) or (req.selectedCases and len(req.selectedCases) > 0)
   if route_result.intent == QueryIntent.CASE_QUERY or (is_case_mode and route_result.intent not in (...)):
   ```
   Furthermore, in `query_router.py`, the query lacked statutory legal anchors, lacked case anchors, and did not match greeting tokens, falling into `AMBIGUOUS`. In prior and active code paths where `is_case_mode` was true, non-statutory queries defaulted into `CaseRAGPipeline.answer_case_question`. Case RAG performed vector/lexical retrieval on Martinez documents, grounded the prompt with maritime cargo filings, and invoked the `case_analysis_v1` LoRA adapter. Because the system prompt strictly instructs Case Analysis V1 to ground answers only on supplied case documents, the adapter correctly reported that the case material did not mention the model of legal AI, exposing model variable strings like `MODEL_AI`.

2. **The Intent Taxonomy Gap**:
   The router taxonomy (`QueryIntent`) contains only five rigid classes: `CONVERSATIONAL`, `LEGAL_QUERY`, `CASE_QUERY`, `OUT_OF_SCOPE`, and `AMBIGUOUS`. There is **no route** for:
   - `SYSTEM_INFORMATION` / `PRODUCT_INFO` (e.g., model architecture, LoRA, capabilities, technologies)
   - `TECHNICAL_AI_KNOWLEDGE` (e.g., what is AI, ML, LLM, RAG, embeddings)
   - `CASE_MANAGEMENT` / `PORTFOLIO_QUERY` (e.g., case priorities, upcoming hearings, deadlines, focus)
   - `GENERAL_KNOWLEDGE` without legal RAG.

3. **Context Leakage via Step 7 Follow-Up**:
   In `query_router.py` (Step 7), any query of 12 words or fewer inherits the intent of the *previous substantive turn*. Consequently:
   - In Sequence A, after asking *"What evidence is missing?"* (`CASE_QUERY`), asking *"What is RAG?"* was classified as `CASE_QUERY`, retrieving Martinez case documents!
   - In Sequence B, after asking *"What is Section 66C of the IT Act?"* (`LEGAL_QUERY`), asking *"What is Qwen?"* was classified as `LEGAL_QUERY`, invoking Statutory Legal RAG and returning: *"I couldn't verify this from the available Indian legal sources in the current corpus."*

4. **Absence of Base Qwen Route**:
   The system never runs Qwen2.5-14B in base mode (`model.disable_adapter()`). Every generation path either runs `LegalAI V2` (for statutory law or conversational) or `Case Analysis V1` (for case queries). General technical and AI questions are either rejected with *"That's outside my legal scope, buddy"* (`OUT_OF_SCOPE`) or forced into clarification (`AMBIGUOUS`).

5. **Concurrency & Adapter Switching Safety**:
   While `CaseRAGPipeline` wraps `model.set_adapter("case_analysis_v1")` in a `try ... finally` block restoring `default`, PEFT adapter switching mutates the global PyTorch model state on a single GPU without an `asyncio.Lock()` or mutex. Concurrent requests across threads can experience adapter race conditions.

---

## 2. Current Architecture

```
                                  USER QUERY (Frontend)
                                           │
                                           ▼
                       AIAssistantView.jsx (Vite/React)
             [Attaches active caseId, mode: 'SINGLE_CASE' / 'GENERAL', history]
                                           │
                                           ▼
                                FastAPI (/api/v1/ai/chat)
                                           │
                                           ▼
                        Deterministic Query Router (query_router.py)
                                           │
       ┌──────────────────┬────────────────┼──────────────────┬─────────────────┐
       ▼                  ▼                ▼                  ▼                 ▼
CONVERSATIONAL      OUT_OF_SCOPE       AMBIGUOUS          CASE_QUERY       LEGAL_QUERY
(Regex Greetings, (Regex Coding,    (Catch-all fallback  (Regex Case/Matter  (Statutes, Sections,
 Gratitude, Id)     Sports, Movies,  for unanchored        Words or forced     Penal/Civil Terms)
       │            Tech Shopping)   queries)             by is_case_mode)              │
       │                  │                │                  │                         │
       ▼                  ▼                ▼                  ▼                         ▼
Static text or    Static rejection   Static polite      CaseRAGPipeline          General Indian Legal
Qwen + V2 LoRA    ("Outside scope,   clarification      (Doc retrieval from      Knowledge Pipeline
(LEGALAI_SYSTEM_   buddy...")        question           active case, grounds     (Exact Act Resolver,
 PROMPT)                                                Case Analysis V1 LoRA)   Hybrid BM25+Vector,
                                                              │                  Temporal Guard,
                                                              │                  Qwen + LegalAI V2)
                                                              ▼                         │
                                                        Case-Grounded Answer            ▼
                                                        ("Supported by case      Statutory Grounded
                                                         documents")             Answer + Citations
```

### Architectural Deficiencies:
- **Missing Information Planes**: No database query plane for case management metadata (cases, hearings, deadlines).
- **Missing Knowledge Planes**: No direct Base Qwen plane for general AI, computer science, and legal tech queries.
- **Asymmetric Precedence**: Conversation history blindly overrides query intent for all short inputs.
- **Frontend State Coupling**: The active workspace case is implicitly treated as the primary intent determinant rather than passive context.

---

## 3. Actual Request Flow

Tracing a request from UI to response across the stack:

1. **User Action**: User types a query into `AIAssistantView.jsx`.
2. **Frontend Payload Assembly** (`aiService.sendMessageStream`):
   - Injects `content`: user input.
   - Injects `convId`: conversation ID.
   - Injects `mode`: `'SINGLE_CASE'` if a case is currently selected in the UI sidebar/view, otherwise `'GENERAL'`.
   - Injects `caseId` / `caseNumber`: e.g., `'2024-CV-1187'` (*Martinez v. Coastal Holdings Ltd.*).
   - Injects `selectedCases`: `['2024-CV-1187']`.
   - Injects `history`: past turns in the active conversation.
3. **Backend Ingestion** (`server.py: ai_chat` / `ai_chat_stream`):
   - Invokes `router.classify(req.content, conversation_history=req.history)`.
   - Evaluates Pre-Route: `indian_knowledge_bridge.check_foreign_law_query`.
   - Route 1 (`CONVERSATIONAL`): If greeting/identity, generates via `generate_conversational_response`.
   - Route 2 (`OUT_OF_SCOPE`): If coding/trivia/sports, returns static scope boundary.
   - Route 2B (`AMBIGUOUS`): If no legal anchor, no case anchor, returns static clarification request.
   - Route 3 (`CASE_QUERY` or `is_case_mode` fallback): If `CASE_QUERY` OR if `mode == 'SINGLE_CASE'` and intent was not excluded, calls `case_rag_pipeline.answer_case_question`.
   - Route 4 (`LEGAL_QUERY`): Calls `indian_knowledge_pipeline.query`.
4. **Model Execution**:
   - For Case RAG: Activates `case_analysis_v1` on `pipeline.model`, generates with greedy decoding (`do_sample=False`), restores `default`.
   - For Legal RAG: Uses `outputs/qwen14b-legalai-v2` (`default`), generates with greedy decoding.
   - For Conversational: Uses `outputs/qwen14b-legalai-v2` (`default`), generates with sampling (`do_sample=True, temp=0.7`).
5. **Frontend Rendering** (`LegalAnswerRenderer.jsx`):
   - Renders message content, reliability badges (`"Supported by case documents"`, `"Verified Indian Legal Authority"`), citations, and source accordions.

---

## 4. Query Taxonomy

### Current Implemented Taxonomy:
| Intent Enum | Trigger Criteria | Action Taken | Failure Mode |
|---|---|---|---|
| `CONVERSATIONAL` | Exact regex greetings, gratitude, small talk, or keyword token set (`"hi"`, `"how are you"`) | Static greeting dictionary or Qwen with conversational system prompt | Misses system questions; capability inquiry returns canned boilerplate |
| `LEGAL_QUERY` | Section syntax, Act names, penal/civil terms, cybercrime concepts | General Indian Legal Knowledge Pipeline (Exact Resolver + Hybrid Search + Qwen V2) | Hijacks short non-legal questions if previous turn was legal |
| `CASE_QUERY` | Case matter regex (`"witness"`, `"evidence"`, `"hearing"`, `"pleadings"`) | CaseRAGPipeline (retrieves active case docs, runs Case Analysis V1 LoRA) | Hijacks system/general questions if previous turn was case-related |
| `OUT_OF_SCOPE` | Regex programming, sports, movies, recipes, consumer tech, general trivia | Static friendly rejection message | Rejects technical questions about AI, ML, LLMs, and LegalAI itself |
| `AMBIGUOUS` | Catch-all fallback when no anchor is detected | Static clarification message | Asks for clarification on clear system questions ("what is the model of legal ai") |

### Missing Taxonomy Classes:
1. `SYSTEM_INFO`: Questions about LegalAI, its underlying model, architecture, training, or creators.
2. `TECHNICAL_KNOWLEDGE`: Explanations of AI, RAG, LoRA, ML, vector databases, and embeddings.
3. `CASE_MANAGEMENT`: Questions querying case status, priority ranking, court hearing calendars, and task deadlines across the lawyer's portfolio.
4. `GENERAL_KNOWLEDGE`: Non-legal, non-programming general knowledge questions that can be answered factually by base Qwen without RAG.

---

## 5. Qwen Role

### Base Model: `Qwen/Qwen2.5-14B-Instruct`
- **Architecture**: 14.7 Billion parameter causal decoder transformer, 48 layers, 40 attention heads (GQA with 8 KV heads), 131,072 token context window, vocabulary size 152,064.
- **Intrinsic Capabilities**:
  - General reasoning, computer science, and multilingual comprehension.
  - Conversational fluency, instruction following, and structured formatting (Markdown/JSON).
  - Pretrained knowledge of world facts, algorithms, machine learning, and AI architectures (including what Qwen, transformers, LoRA, and RAG are).
- **Actual Utilization in Current System**:
  - Never invoked without a LoRA adapter attached.
  - Never allowed to answer technical or AI questions directly.
  - Restricted strictly to:
    1. Grounded statutory synthesis over retrieved sections.
    2. Grounded case analysis over retrieved document chunks.
    3. Casual conversational banter when not intercepted by static regex dictionaries.

---

## 6. LegalAI V2 LoRA Role

### Adapter: `outputs/qwen14b-legalai-v2`
- **Configuration**:
  - Rank ($r$): 16, Alpha ($\alpha$): 32, Dropout: 0.05.
  - Targets: All linear projection layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
  - Parameter Size: ~275 MB (`adapter_model.safetensors`).
- **Training Data**: `data/legal_train_v2.jsonl` (1,424 samples).
- **What LegalAI V2 Actually Teaches**:
  1. **Indian Legal Answer Structure**: Synthesizes statutory provisions into advocate-grade explanations (Scope, Essential Ingredients, Penal Consequences).
  2. **Temporal Law Behavioral Discipline**: Respects Article 20(1) non-retroactivity; understands that pre-July 1, 2024 substantive offences are governed by IPC, while post-July 1, 2024 are governed by BNS.
  3. **Strict Grounding & Hallucination Resistance**: Adheres to retrieved context; avoids inventing section numbers.
- **What LegalAI V2 Does NOT Contain**:
  - Does NOT contain the full text of all 840+ Indian Central and State Acts (this comes from the SQLite statutory databases and RAG retriever).
  - Does NOT contain client case facts or evidence.

---

## 7. Case Analysis V1 Role

### Adapter: `outputs/qwen14b-case-analysis-v1`
- **Configuration**:
  - Rank ($r$): 16, Alpha ($\alpha$): 32, Targets: all 7 linear projections (~275 MB).
- **Training Data**: `data/case_analysis/case_analysis_train.jsonl` (5,786 samples).
- **What Case Analysis V1 Actually Teaches**:
  1. **Evidentiary Rigor**: Distinguishes between documented facts and missing documents.
  2. **Absence Protocol**: Uses the strict phrasing *"Not found in the supplied case material"* when evidence is absent.
  3. **Advocate Tasks**: Trained on 8 core litigation workflows: Pleading Scrutiny, Witness Contradiction Analysis, Charge Sheet Review, Missing Document Audit, Precedent Research, Settlement Assessment, and Hearing Preparation.
- **Interaction with System Queries**:
  - When a system query (e.g. *"what is the model of legal ai"*) enters Case RAG, Case Analysis V1 receives maritime dispute context from the Martinez case. Following its fine-tuned behavior, it checks the documents for "model of legal AI", finds nothing, and generates: *"The supplied case material does not establish a specific model of legal AI used."*

---

## 8. General Legal RAG Role

### Implementation: `GeneralIndianLegalKnowledgePipeline` & `LegalAIRAGPipeline`
- **Databases**:
  - `data/legalai_indian_legal_knowledge.db` (38 MB SQLite DB containing 840+ Central & State Acts).
  - `data/legalai_rag_mvp.db` (14 MB SQLite DB for core 2023 criminal enactments: BNS, BNSS, BSA).
- **Retriever**:
  - Exact Provision Resolver: Deterministic section/article lookup with temporal transition mapping.
  - Hybrid Searcher: Reciprocal Rank Fusion (RRF) combining BM25 keyword matching and dense vector retrieval (`BAAI/bge-small-en-v1.5`).
- **Evidence Gates**:
  - Statutory Relevance Gate: Evaluates candidate chunks against query intent.
  - Temporal Law Guard: Evaluates incident date against commencement thresholds.
  - Statutory Citation Verifier: Validates that generated citations match retrieved chunk citations.
- **Role**: Authoritative statutory evidence provider. Should ONLY be activated when the user asks a substantive Indian legal question.

---

## 9. Case RAG Role

### Implementation: `CaseRAGPipeline`
- **Database**: `data/legalai_case_rag.db`.
- **Index**: SQLite table storing document chunks with dense vector embeddings (`BAAI/bge-small-en-v1.5`).
- **Chunker**: Legal document chunker respecting paragraph and page boundaries.
- **Isolation**: Strictly isolates chunks by `case_id` (`WHERE case_id = ?`).
- **Role**: Retrieves private evidentiary documents uploaded by the lawyer for a specific matter.
- **Failure Mode**: When the system treats the active workspace case as an execution directive rather than passive context, Case RAG retrieves irrelevant case chunks for general or system queries.

---

## 10. Prompt / Context Construction

| Route | System Prompt Used | User Prompt Construction | Generation Parameters |
|---|---|---|---|
| **Conversational** | `LEGALAI_SYSTEM_PROMPT` | History (last 4 turns) + User message | `do_sample=True, temp=0.7, top_p=0.9, max_tokens=256` |
| **Legal RAG** | `GROUNDED_SYSTEM_PROMPT` | Question + Temporal Directive + Verified Statutory Authorities + Citation Rules | `do_sample=False, max_tokens=512` |
| **Case RAG** | `CASE_ANALYSIS_SYSTEM_PROMPT` | `CASE MATERIAL:\n{case_chunks}\n\nLAWYER QUERY:\n{question}` | `do_sample=False, max_tokens=512` |
| **Out-of-Scope** | None (Static template) | None (Static response selected via pattern) | No LLM execution |
| **Ambiguous** | None (Static template) | None (Static clarification string) | No LLM execution |

### Vulnerabilities:
- `LEGALAI_SYSTEM_PROMPT` contains zero factual knowledge about LegalAI's own technical specifications (model name, size, LoRA adapters, database architecture).
- No prompt template exists for General Technical explanations or Case Portfolio queries.

---

## 11. Frontend → Backend Flow

### Inspection of `AIAssistantView.jsx` & `aiService.js`:
1. **Case State Retention**:
   When opening the AI Assistant from a case detail view, `lockedCase` sets `mode = 'SINGLE_CASE'` and `caseId = lockedCase.caseNumber`.
2. **Payload Injection**:
   Even if the user switches mental focus to a general question ("What is RAG?"), the frontend transmits:
   ```json
   {
     "content": "What is RAG?",
     "mode": "SINGLE_CASE",
     "caseId": "2024-CV-1187",
     "selectedCases": ["2024-CV-1187"]
   }
   ```
3. **Stale Mode Transmission**:
   The frontend conversation model does not automatically clear `mode` or `caseId` when the user asks a non-case question. It relies entirely on the backend to distinguish whether the query actually pertains to the case.
4. **Backend Reception**:
   In `server.py`, the backend checks `is_case_mode`. If `query_router.py` does not explicitly flag the query as `LEGAL_QUERY`, `CONVERSATIONAL`, `OUT_OF_SCOPE`, or `AMBIGUOUS`, the backend forwards the request to Case RAG!

---

## 12. Active Context Precedence

The current precedence order implemented in the codebase is inverted:

```
[CURRENT FLAWED PRECEDENCE]
1. Conversation History (Step 7: Short queries blindly inherit last intent)
2. Active Case Mode (is_case_mode overrides non-legal queries into Case RAG)
3. Hardcoded Capability Tokens (Overriding specific questions into boilerplate)
4. Out-of-Scope Regexes (Rejecting AI/technical questions)
5. Safe Ambiguous Fallback (Catch-all asking for clarification)
```

```
[CORRECT TARGET PRECEDENCE]
1. Current Query Explicit Intent & Entity Classification
2. System & Product Information Intent (Zero RAG, System Prompt Grounding)
3. General Technical & AI Knowledge (Zero RAG, Base Qwen Grounding)
4. Case Management / Portfolio Meta Intent (Database Query, Zero Vector RAG)
5. Explicit Statutory Legal Intent (General Legal RAG)
6. Explicit Case Matter Intent (Case RAG with active case)
7. Contextual Follow-Up (Only when current query is genuinely demonstrative/anaphoric)
8. Passive Active Case Context (Used ONLY if query refers to the active matter)
9. Out-of-Scope / Non-Legal Domain (Friendly redirection)
10. Ambiguous Fallback (Clarification request)
```

---

## 13. Adapter State Analysis

### Adapter Registration & Switching:
- Registered on model singleton during server startup in `lifespan()`:
  - Base Model: `Qwen/Qwen2.5-14B-Instruct`
  - Default Adapter: `outputs/qwen14b-legalai-v2` (`"default"`)
  - Case Adapter: `outputs/qwen14b-case-analysis-v1` (`"case_analysis_v1"`)
- **State Transition Test Matrix**:
  1. Case Query -> Activates `case_analysis_v1` -> Generates -> Restores `default`.
  2. System Query -> Currently bypasses model or uses `default`.
  3. General Legal Query -> Sets `default` -> Generates.
  4. Conversational Query -> Uses `default` -> Generates.
- **Finding on Static Leakage**:
  In a single-threaded sequential execution, the adapter resets cleanly because `_generate_with_case_analysis_v1` contains a `try ... finally` block.
- **Finding on Concurrency Leakage**:
  `model.set_adapter()` modifies global PEFT state. In FastAPI with multiple concurrent requests, if Request A calls `set_adapter("case_analysis_v1")` while Request B is generating a legal response on `default`, Request B may execute partially or fully through `case_analysis_v1`.

---

## 14. Context Leakage Analysis

Live sequential testing demonstrated severe context leakage across turns:

### Sequence A (Case Context Active):
- Turn 1: *"What evidence is missing?"* -> `CASE_QUERY` (Martinez documents retrieved, Case Analysis V1 used).
- Turn 2: *"What model does LegalAI use?"* -> `CONVERSATIONAL` (Captured by capability regex, returned canned list).
- Turn 3: *"What is RAG?"* -> **LEAKAGE FAILURE**:
  Step 7 in `query_router.py` saw the turn was 3 words ($<= 12$), found Turn 1 was `CASE_QUERY`, and classified *"What is RAG?"* as `CASE_QUERY`! It retrieved Martinez cargo documents and answered from the case file!

### Sequence B (Legal to General):
- Turn 1: *"What is Section 66C of the IT Act?"* -> `LEGAL_QUERY` (Exact provision, Qwen + LegalAI V2).
- Turn 2: *"What is Qwen?"* -> **LEAKAGE FAILURE**:
  Step 7 saw length $<= 12$, found Turn 1 was `LEGAL_QUERY`, and routed *"What is Qwen?"* to Statutory Legal RAG! RAG searched Indian statutes for "Qwen", found nothing, and abstained!
- Turn 3: *"How does fine-tuning work?"* -> **LEAKAGE FAILURE**:
  Again routed to Statutory Legal RAG and abstained!

### Sequence C (Case to System/Management):
- Turn 1: *"What is the Martinez case about?"* -> `AMBIGUOUS` (Failed to match strict case keywords).
- Turn 2: *"What model does LegalAI use?"* -> `CONVERSATIONAL` (Capability canned response).
- Turn 3: *"Which case should I focus on?"* -> `CASE_QUERY` (Treated as single-case query on Martinez instead of portfolio priority).
- Turn 4: *"What is RAG?"* -> `CASE_QUERY` (Retrieved Martinez case documents).

---

## 15. Query Decision Matrix

| Query Category | Example Query | Intended Route | Intended RAG | Intended Model / Adapter | Actual Route | Actual RAG | Actual Adapter | Architectural Problem |
|---|---|---|---|---|---|---|---|---|
| **Conversational** | *"Hey! How are you doing today?"* | `CONVERSATIONAL` | `NONE` | Base Qwen or Canned | `CONVERSATIONAL` | `NONE` | None (Static) | `EXPECTED_BEHAVIOR` |
| **System Info** | *"what is the model of legal ai"* | `SYSTEM_INFO` | `NONE` | Base Qwen + App Context | `AMBIGUOUS` (or `CASE_RAG` in case mode) | `NONE` (or `CASE_RAG`) | None (or `case_analysis_v1`) | `INTENT_TAXONOMY_GAP`, `ACTIVE_CASE_OVERRIDE` |
| **System Info** | *"What technology does LegalAI use?"* | `SYSTEM_INFO` | `NONE` | Base Qwen + App Context | `CONVERSATIONAL` | `NONE` | None (Canned) | `ROUTING_FAILURE` (collides with capability) |
| **Technical AI** | *"What is artificial intelligence?"* | `TECHNICAL_KNOWLEDGE` | `NONE` | Base Qwen | `OUT_OF_SCOPE` | `NONE` | None (Static rejection) | `INTENT_TAXONOMY_GAP`, `ROUTING_FAILURE` |
| **Technical AI** | *"What is machine learning?"* | `TECHNICAL_KNOWLEDGE` | `NONE` | Base Qwen | `OUT_OF_SCOPE` | `NONE` | None (Static rejection) | `INTENT_TAXONOMY_GAP`, `ROUTING_FAILURE` |
| **Technical AI** | *"What is an LLM?"* | `TECHNICAL_KNOWLEDGE` | `NONE` | Base Qwen | `OUT_OF_SCOPE` | `NONE` | None (Static rejection) | `INTENT_TAXONOMY_GAP`, `ROUTING_FAILURE` |
| **Technical AI** | *"Explain RAG."* (in case context) | `TECHNICAL_KNOWLEDGE` | `NONE` | Base Qwen | `CASE_QUERY` | `CASE_RAG` | `case_analysis_v1` | `CONTEXT_LEAKAGE`, `RAG_SELECTION_FAILURE` |
| **Technical AI** | *"What is Qwen?"* (after legal query) | `TECHNICAL_KNOWLEDGE` | `NONE` | Base Qwen | `LEGAL_QUERY` | `LEGAL_RAG` | None (Abstained) | `CONTEXT_LEAKAGE`, `RAG_SELECTION_FAILURE` |
| **Technical AI** | *"How does fine-tuning work?"* | `TECHNICAL_KNOWLEDGE` | `NONE` | Base Qwen | `OUT_OF_SCOPE` or `LEGAL_QUERY` | `NONE` or `LEGAL_RAG` | None | `ROUTING_FAILURE` |
| **Case Management** | *"what is the important thing i have to focus on now"* | `CASE_MANAGEMENT` | `CASE_METADATA_DB` | Base Qwen + Portfolio Context | `AMBIGUOUS` | `NONE` | None | `INTENT_TAXONOMY_GAP` |
| **Case Management** | *"like what case i have to focus more which have the high priority"* | `CASE_MANAGEMENT` | `CASE_METADATA_DB` | Base Qwen + Portfolio Context | `AMBIGUOUS` | `NONE` | None | `INTENT_TAXONOMY_GAP` |
| **Case Management** | *"What hearings are scheduled for this week?"* | `CASE_MANAGEMENT` | `CASE_METADATA_DB` | Base Qwen + Calendar Context | `CASE_QUERY` | `CASE_RAG` | `case_analysis_v1` | `RAG_SELECTION_FAILURE` |
| **Case Query** | *"What evidence is missing?"* (with case active) | `CASE_QUERY` | `CASE_RAG` | Qwen + `case_analysis_v1` | `CASE_QUERY` | `CASE_RAG` | `case_analysis_v1` | `EXPECTED_BEHAVIOR` |
| **Legal Query** | *"What is Section 66C of the IT Act?"* | `LEGAL_QUERY` | `LEGAL_RAG` | Qwen + `outputs/qwen14b-legalai-v2` | `LEGAL_QUERY` | `EXACT_PROVISION` | `outputs/qwen14b-legalai-v2` | `EXPECTED_BEHAVIOR` |
| **Legal Query** | *"What is the Tamil Nadu Payment of Salaries Act?"* | `LEGAL_QUERY` | `LEGAL_RAG` | Safe Abstention (`STATUTORY_ABSENCE`) | `LEGAL_QUERY` | `STATUTORY_ABSENCE` | None | `EXPECTED_BEHAVIOR` |
| **Out-of-Domain** | *"Who won the football match?"* | `OUT_OF_SCOPE` | `NONE` | Static Scope Boundary | `OUT_OF_SCOPE` | `NONE` | None | `EXPECTED_BEHAVIOR` |
| **Out-of-Domain** | *"Write me a Python program to sort a list."* | `OUT_OF_SCOPE` | `NONE` | Static Scope Boundary | `OUT_OF_SCOPE` | `NONE` | None | `EXPECTED_BEHAVIOR` |

---

## 16. Observed Failures

1. **Failure 1: System Question Contaminating Case RAG**
   - Symptom: *"what is the model of legal ai"* -> Returns *"Supported by case documents"* + *"The supplied case material does not establish a specific model of legal AI used."*
   - Root Cause: Inverted precedence where `is_case_mode` forces unclassified queries into `CaseRAGPipeline`.
2. **Failure 2: Capability Query Interception of Factual Technical Questions**
   - Symptom: *"What technology does LegalAI use?"* -> Returns canned text: *"I am LegalAI... 1. Statutory Research..."*
   - Root Cause: Broad regex token matching (`"what"` + `"legalai"` + `"use"`/`"do"`) intercepts questions about system architecture.
3. **Failure 3: Rejection of Legitimate AI & ML Educational Questions**
   - Symptom: *"What is artificial intelligence?"*, *"What is machine learning?"*, *"What is an LLM?"* -> Returns: *"That's outside my legal scope, buddy. 😊"*
   - Root Cause: Blanket categorization of computer science and AI terminology under `OUT_OF_SCOPE_PATTERNS`.
4. **Failure 4: Blind Follow-Up Context Contamination**
   - Symptom: *"What is RAG?"* following a case query gets routed to `CASE_QUERY`; *"What is Qwen?"* following a legal query gets routed to `LEGAL_QUERY`.
   - Root Cause: Step 7 in `query_router.py` applies a word-count threshold ($<= 12$ words) to copy the previous intent without checking whether the new query has an independent entity/topic.
5. **Failure 5: Case Priority and Management Incomprehension**
   - Symptom: *"what is the important thing i have to focus on now"*, *"like what case i have to focus more which have the high priority"* -> Returns: *"Could you provide a bit more detail on what you mean by..."*
   - Root Cause: The router lacks natural case-management understanding, and the backend lacks a bridge to the `cases` table in `legalai.db`.

---

## 17. Root Causes

### Root Cause 1: Intent Taxonomy Deficiency (`INTENT_TAXONOMY_GAP`)
The router only recognizes 5 categories (`CONVERSATIONAL`, `LEGAL_QUERY`, `CASE_QUERY`, `OUT_OF_SCOPE`, `AMBIGUOUS`). It has no concept of `SYSTEM_INFO`, `TECHNICAL_KNOWLEDGE`, or `CASE_MANAGEMENT`.

### Root Cause 2: Over-Aggressive Active Case Hijacking (`ACTIVE_CASE_OVERRIDE`)
In `server.py`, the presence of `mode: 'SINGLE_CASE'` or `caseId` in the request overrides non-legal queries and forwards them to Case Document RAG. Active case selection must serve as *context*, never as an *intent determinant*.

### Root Cause 3: Naive History Inheritance (`CONTEXT_LEAKAGE`)
Step 7 in `query_router.py` assumes that any query with 12 words or fewer is an anaphoric follow-up to the preceding turn. It does not verify whether the short query contains a new independent topic (e.g. "What is Qwen?", "What is RAG?").

### Root Cause 4: Overly Broad Out-of-Scope Blocking (`ROUTING_FAILURE`)
Terms like "artificial intelligence", "machine learning", and "LLM" were placed in `OUT_OF_SCOPE_PATTERNS` alongside sports, movies, and cooking. A legal AI assistant should be able to explain AI concepts to a lawyer using base model knowledge without invoking statutory RAG.

### Root Cause 5: Missing Case Portfolio Management Plane (`RAG_SELECTION_FAILURE`)
LegalAI has structured case metadata in SQLite (`cases` table: title, priority, court, status, nextHearing, countdown days), but `/api/v1/ai/chat` has no tool or handler to query this metadata. It can only query raw document chunks via `CaseRAGPipeline`.

### Root Cause 6: Incomplete Base Model Routing (`ADAPTER_SELECTION_FAILURE`)
There is no code path that executes `Qwen2.5-14B` with adapters disabled (`model.disable_adapter()`) or with an application-context system prompt. The model is only accessible through the fine-tuned adapters.

### Root Cause 7: Lack of Concurrency Mutex for PEFT Adapters (`CONCURRENCY_STATE_FAILURE`)
PEFT `model.set_adapter()` modifies the active adapter on the shared singleton model in GPU memory without an async/thread lock, making multi-user or sequential concurrent requests susceptible to adapter collision.

---

## 18. Generalization Risks

If fixes are implemented narrowly (e.g., adding `if "model of legal ai" in query`), the system will continue to fail when users ask:
- *"Which LLM is running under the hood?"*
- *"Are you based on Llama or Qwen?"*
- *"What neural network architecture powers your analysis?"*
- *"Summarize my calendar for tomorrow"*
- *"Which client matters require urgent filings this week?"*

**The architectural solution must generalize across entire intent classes rather than string matching.**

---

## 19. Recommended Target Architecture

```
                                 USER QUERY
                                     │
                                     ▼
                    Unified Query Intent & Entity Classifier
                                     │
      ┌───────────────┬──────────────┼──────────────┬──────────────┬──────────────┐
      ▼               ▼              ▼              ▼              ▼              ▼
CONVERSATIONAL   SYSTEM_INFO    TECHNICAL_AI   CASE_MGMT      LEGAL_QUERY    CASE_QUERY
      │               │              │              │              │              │
    NO RAG          NO RAG         NO RAG      METADATA DB     LEGAL RAG      CASE RAG
      │               │              │              │              │              │
   Base Qwen      Base Qwen      Base Qwen      Base Qwen      LegalAI V2     Case V1
      │               │              │              │              │              │
      └───────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                                     │
                                     ▼
                      Asynchronous Thread Lock (Mutex)
                                     │
                                     ▼
                       Qwen2.5-14B Generation Engine
                                     │
                                     ▼
                        Structured Response Renderer
```

### Routing Rules:
1. **`SYSTEM_INFO`**: Recognized via generalized system patterns (model, architecture, version, parameters, creator). Routes to **NO RAG**, runs Base Qwen with a system prompt describing LegalAI specifications.
2. **`TECHNICAL_AI`**: Recognized via AI/ML concept extraction. Routes to **NO RAG**, runs Base Qwen with general technical explanation prompt.
3. **`CASE_MGMT`**: Recognized via portfolio/schedule/priority intent. Queries `legalai.db` (`cases` table), formats structured case summary, runs Base Qwen to synthesize portfolio priorities.
4. **`LEGAL_QUERY`**: Recognized via statutory anchors. Queries `GeneralIndianLegalKnowledgePipeline`, runs LegalAI V2 LoRA.
5. **`CASE_QUERY`**: Recognized via explicit case evidence/matter references. Queries `CaseRAGPipeline` for active case, runs Case Analysis V1 LoRA.
6. **`CONTEXT_FOLLOW_UP`**: Only applied if the query contains explicit demonstratives (*"what about that"*, *"explain that point"*, *"why"*) AND does not introduce a new noun/concept.

---

## 20. Recommended Fix Plan

> **Note**: As mandated by the audit requirements, NO production code or models have been modified during this investigation. This plan provides the roadmap for the implementation phase.

### Phase 1: Expand Intent Taxonomy (`src/api/query_router.py`)
- Add enum values: `SYSTEM_INFO`, `TECHNICAL_KNOWLEDGE`, `CASE_MANAGEMENT`.
- Move AI, ML, LLM, RAG, and fine-tuning patterns out of `OUT_OF_SCOPE` into `TECHNICAL_KNOWLEDGE`.
- Implement generalized intent recognizers:
  - System inquiries: patterns matching queries about model, LLM, parameters, version, backend technology.
  - Case management inquiries: patterns matching priority, focus, upcoming hearings, deadlines, case calendar across matters.
- Fix Step 7 Context Follow-Up: only inherit previous turn intent if the query contains an explicit anaphoric pronoun (*"this"*, *"that"*, *"it"*, *"the former"*) and does not contain independent substantive nouns.

### Phase 2: Implement System Information & Technical Handlers (`src/api/server.py`)
- Define `LEGALAI_SYSTEM_SPECS`:
  - Name: LegalAI
  - Foundation Model: Qwen 2.5 14B Instruct
  - Fine-Tuning: Parameter-Efficient LoRA (LegalAI V2 & Case Analysis V1)
  - Knowledge Base: General Indian Legal Knowledge Pipeline (840+ Central & State Acts) + Case Document RAG
- Route `SYSTEM_INFO` and `TECHNICAL_KNOWLEDGE` to Base Qwen with `model.disable_adapter()` and zero RAG retrieval.

### Phase 3: Implement Case Management Database Bridge (`src/api/server.py`)
- When `CASE_MANAGEMENT` intent is detected:
  - Query SQLite `cases` table: `SELECT caseNumber, title, court, priority, nextHearing, hearingCountdownDays FROM cases ORDER BY hearingCountdownDays ASC`.
  - Pass structured portfolio data to Qwen to answer questions like: *"Which case should I focus on?"* or *"What hearings are scheduled this week?"*.

### Phase 4: Thread-Safe Adapter Concurrency (`src/rag/integration/rag_legalai.py` & `src/case_rag/pipeline.py`)
- Introduce an `asyncio.Lock()` around all generation calls on the shared `pipeline.model` singleton to prevent adapter state collision under concurrent requests.

### Phase 5: Frontend Context Decoupling (`AIAssistantView.jsx`)
- Ensure the frontend does not force `mode = 'SINGLE_CASE'` for queries that are classified as general or system inquiries.

---

## 21. Audit Verification Summary

| Metric | Result | Notes |
|---|---|---|
| **Query categories tested** | **11** | Conversational, System Info, Technical AI, Case Management, Legal In-Corpus, Legal Unindexed, Case Query, Ambiguous, Out-of-Domain, Mixed, Follow-ups |
| **Individual test queries executed** | **47** | 4 multi-turn sequences (18 queries) + 1 broad diagnostic matrix (29 queries) |
| **Routing failures identified** | **24** | System questions, AI questions, case management, and follow-ups misrouted |
| **RAG-selection failures identified** | **16** | Erroneous Case RAG or Legal RAG activation on non-RAG queries |
| **Case RAG contamination cases** | **6** | Queries regarding RAG, Qwen, priorities, and system model retrieving Martinez case docs |
| **Adapter-selection failures** | **16** | Case Analysis V1 or LegalAI V2 invoked when Base Qwen should have been selected |
| **Adapter state-leakage cases** | **0 static / 1 concurrency risk** | Clean sequential reset, but global PEFT state lacks mutex for concurrent calls |
| **Context-leakage cases** | **14** | Step 7 naive word-count threshold causing cross-turn intent inheritance |
| **Frontend-state problems** | **3** | Stale mode retention, hardcoded `SINGLE_CASE` attachment, lack of context clearing |
| **Prompt-construction problems** | **4** | Missing prompts for system specs, technical AI, and portfolio management |
| **Generation-grounding problems** | **5** | Case RAG hallucinating absence of system facts; Legal RAG abstaining on tech terms |
| **Root causes identified** | **7** | Taxonomy gap, active case override, history inheritance, broad out-of-scope, missing portfolio DB plane, missing base Qwen route, adapter concurrency |
| **Qwen base model modified?** | **NO** | Strictly read-only audit |
| **LoRA adapters modified?** | **NO** | Strictly read-only audit |
| **RAG databases modified?** | **NO** | Strictly read-only audit |
| **GPU processes modified?** | **NO** | Physical GPU 2 process untouched |
| **Audit Report Artifact** | `results/legalai_universal_query_behavior_audit.md` | Successfully generated and mirrored |

