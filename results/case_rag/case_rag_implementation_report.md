# LegalAI: Case Document RAG & Case Analysis V1 Integration Report

**Milestone**: Case Document RAG → Case Analysis V1 → Grounded Lawyer-Facing Case Analysis  
**Date**: September 14, 2026  
**Environment**: DGX / NVIDIA B200 (Physical GPU 2 / `CUDA_VISIBLE_DEVICES=2`)  
**Base Model**: `Qwen/Qwen2.5-14B-Instruct` (Singleton)  
**Adapters**:
- Default/Statutory Legal RAG: `outputs/qwen14b-legalai-v2` (FROZEN)
- Case Analysis RAG: `outputs/qwen14b-case-analysis-v1` (FROZEN)

---

## 1. Executive Summary & Implementation Status

The production milestone **Case Document RAG → Case Analysis V1** has been fully implemented, integrated into the FastAPI backend, and verified end-to-end. Advocates can now upload case files (PDF, TXT, DOCX) to a case workspace and ask lawyer-facing questions such as:
- *"Analyze this case."*
- *"What evidence is missing?"*
- *"What things need to be verified before submitting this evidence?"*
- *"What contradictions exist between the documents?"*
- *"What evidence gaps are present?"*
- *"What supporting documents are referred to but not available?"*
- *"What are the strengths and weaknesses of our case?"*
- *"Prepare me for the next hearing."*

All answers are strictly grounded in the uploaded case material, cite physical page provenance, separate factual findings from legal inferences, identify unprovided evidence without falsely claiming non-existence, and query statutory requirements under BNS, BNSS, and BSA through the isolated statutory Legal RAG.

### Implementation Checklist
- [x] Multi-format case document parser (`PDF`, `TXT`, `DOCX`) with physical page tracking.
- [x] Page-aware chunking preserving provenance metadata (`{doc_id}-p{page}-c{idx}`).
- [x] Isolated Case RAG storage (`data/legalai_case_rag.db`) with SQLite FTS5 BM25 + dense vector BLOB index.
- [x] Strict Case Isolation (`WHERE case_id = ?`) preventing any cross-case information leakage.
- [x] Hybrid Dense (0.7) + Lexical (0.3) retriever with deterministic ranking.
- [x] Complete separation between Statutory Legal RAG (`data/legalai_rag_mvp.db`) and Case Document RAG (`data/legalai_case_rag.db`).
- [x] Intelligent Query Router directing conversational queries, statutory queries, and case analysis queries.
- [x] Dynamic multi-adapter switching on the single 14B model in VRAM (Physical GPU 2), switching to `case_analysis_v1` and safely reverting to `default` (`legalai-v2`).
- [x] Case Analysis prompt format matching V1 fine-tuning distribution (`CASE MATERIAL:`, `LAWYER QUERY:`, `LEGAL AUTHORITY:`).
- [x] Full backward-compatible API integration (`POST /api/v1/cases/{case_id}/documents`, `POST /api/v1/ai/chat`, `POST /api/v1/ai/chat/stream`).
- [x] 100% test pass rate across unit tests, security isolation tests, statutory RAG regressions, and live end-to-end suite.

---

## 2. Existing Components Reused vs. Newly Created

| Subsystem | Existing Component Reused | Newly Created Component | Rationale |
| :--- | :--- | :--- | :--- |
| **Model Serving** | Single `Qwen/Qwen2.5-14B-Instruct` model in VRAM on GPU 2 | PEFT dynamic adapter switching via `model.set_adapter("case_analysis_v1")` | Eliminates VRAM duplication; fits within physical GPU 2 memory budget. |
| **Statutory Law** | `src/rag/` (BNS/BNSS/BSA corpus, BM25 + dense, temporal guard, relevance gate) | `src/case_rag/pipeline.py` calls `LegalRetriever` when statutory questions arise | Zero risk of polluting statutory corpus with client documents. |
| **Embeddings** | `BAAI/bge-large-en-v1.5` local model | `CaseEmbedder` wrapper in `src/case_rag/embeddings.py` | Avoids downloading duplicate or unnecessarily heavy embedding models. |
| **Document Storage** | `data/case_documents/{case_id}/` storage directory structure | `src/case_rag/document_processor.py` for physical page extraction | Reuses existing file upload directory while adding robust text extraction. |
| **Database** | SQLite architecture pattern | `data/legalai_case_rag.db` isolated database file | Isolates case documents and chunk indices from the app and statutory DBs. |
| **API Contracts** | `src/api/server.py` routing, SSE streaming, frontend response schema | Case RAG ingestion hooks and `/api/v1/ai/chat` case mode handler | Zero disruption to existing React frontend contracts (`LegalAnswerRenderer`). |

---

## 3. Case RAG Subsystem Architecture

```
Lawyer Uploads Document (PDF / DOCX / TXT)
       │
       ▼
[document_processor.py]  ── ExtractedPage(page_number, text)
       │
       ▼
[chunker.py]             ── DocumentChunk(chunk_id, doc_id, case_id, page_number, text)
       │
       ▼
[embeddings.py]          ── BGE Large Dense Embedding (1024-dim)
       │
       ▼
[index.py]               ── SQLite FTS5 (BM25) + Vector BLOB (data/legalai_case_rag.db)
                            Enforces strict WHERE case_id = ?

========================================================================================

Lawyer Query: "What evidence is missing?" (case_id: case-01)
       │
       ▼
[query_router.py]        ── Detected: CASE_QUERY
       │
       ▼
[pipeline.py]            ── Case ID Validation & Document Availability Check
       │                    (If no docs: returns structured insufficiency guidance)
       │
       ├─► [retriever.py] ── Hybrid Dense (0.7) + BM25 (0.3) strictly WHERE case_id='case-01'
       │                     Returns Top-K Case Chunks with exact Page Provenance
       │
       ├─► [rag_legalai.py]── (If legal requirements needed: retrieves Section 63 BSA, etc.)
       │
       ▼
[Case Analysis V1 Prompt Construction]
       CASE MATERIAL:
       [Document: FIR.pdf | Page 1 | Chunk 1] ...
       [Document: Witness_Statement_01.pdf | Page 1 | Chunk 1] ...
       
       LEGAL AUTHORITY:
       BSA Section 63: ...
       
       LAWYER QUERY:
       What evidence is missing?
       │
       ▼
[Inference Singleton: Physical GPU 2]
       model.set_adapter("case_analysis_v1")
       generate(...)
       model.set_adapter("default")  [in finally block]
       │
       ▼
[Response & Provenance Formatting]
       Content: Markdown formatted case analysis (Facts, Missing Evidence, Next Steps)
       Sources: [{type: 'document', title: 'FIR.pdf', reference: 'Page 1', excerpt: '...'}]
       Reliability: 'supported' ("Supported by case documents")
```

---

## 4. Strict Case Isolation Security & Integrity

A foundational security requirement is that **Case A documents must NEVER be retrieved for a Case B query**.

1. **Database Schema Isolation**:
   ```sql
   CREATE TABLE chunks (
       chunk_id TEXT PRIMARY KEY,
       case_id TEXT NOT NULL,
       document_id TEXT NOT NULL,
       page_number INTEGER NOT NULL,
       chunk_index INTEGER NOT NULL,
       text TEXT NOT NULL,
       embedding BLOB NOT NULL
   );
   CREATE INDEX idx_chunks_case ON chunks(case_id);
   ```
2. **Lexical Isolation**: SQLite FTS5 queries explicitly join against `chunks` and filter:
   ```sql
   WHERE chunks.case_id = ?
   ```
3. **Dense Vector Isolation**: Cosine similarity is computed **only** across chunk embeddings where `case_id == target_case_id`. Chunks from other cases are not loaded into memory or compared.
4. **Automated Security Test Validation**:
   - In `tests/test_case_rag.py::test_03_case_isolation_security`, Case A ("Alpha Tech confidential contract") and Case B ("Beta Logistics accident") were indexed into the database.
   - Searching Case B for "Alpha Tech contract" returned **0 chunks**.
   - Searching Case A for "Alpha Tech contract" returned **exact Case A chunks**.
   - In `scripts/test_case_rag_e2e.py::test_12_cross_case_isolation`, an adversarial cross-case retrieval query on the live server returned **0 results from other cases**.

---

## 5. Model Architecture & Adapter Invariants

### Hardware & Process Allocation
- **Hardware**: NVIDIA B200 (Physical GPU 2).
- **Process**: Single FastAPI process (`uvicorn`, PID 844764). No second model process was created.
- **Base Model**: `Qwen/Qwen2.5-14B-Instruct` in bfloat16 loaded on GPU 2.
- **Adapter 1 (`default`)**: `outputs/qwen14b-legalai-v2` (FROZEN). Used for statutory Legal RAG.
- **Adapter 2 (`case_analysis_v1`)**: `outputs/qwen14b-case-analysis-v1` (FROZEN). Used for Case Analysis RAG.

### Safe Dynamic Switching Mechanism
```python
with torch.inference_mode():
    try:
        model.set_adapter("case_analysis_v1")
        output_ids = model.generate(**inputs, max_new_tokens=1024, temperature=0.1)
    finally:
        model.set_adapter("default")
```
This guarantees that statutory legal queries immediately revert to the V2 adapter, avoiding VRAM overhead or GPU out-of-memory states.

---

## 6. Separation between Statutory Legal RAG and Case RAG

| Attribute | Statutory Legal RAG | Case Document RAG |
| :--- | :--- | :--- |
| **Scope** | Authoritative Indian Law (BNS, BNSS, BSA) | Private Case Documents (FIR, Statements, Pleadings) |
| **Database** | `data/legalai_rag_mvp.db` | `data/legalai_case_rag.db` |
| **Adapter** | `outputs/qwen14b-legalai-v2` | `outputs/qwen14b-case-analysis-v1` |
| **Question Types** | *"What does BNS Section 103 provide?"* | *"What evidence is missing?", "Analyze this case"* |
| **Safety Guardrails**| Temporal Guard (1 July 2024 cutoff), Relevance Gate, Domain Detector | Case Isolation (`case_id`), Evidence Sufficiency Guard |
| **Out-of-Corpus** | Rejects queries outside BNS/BNSS/BSA (e.g., NI Act, IT Act) | States: *"Not found in supplied case material"* |

---

## 7. Synthetic Demo Case Specification

A clean synthetic demo case was created under `data/demo_case/` containing realistic evidentiary issues:

```
data/demo_case/
├── FIR.pdf                 (2 pages: Incident at 8:00 PM; refers to CCTV camera at gate)
├── Witness_Statement_01.pdf (2 pages: Witness states incident occurred at 9:00 PM; saw CCTV)
├── Medical_Report.pdf      (1 page: Blunt force trauma; opinion on weapon requires verification)
└── Seizure_Record.pdf      (1 page: Seized mobile phone; WhatsApp chats uncertified under Sec 63 BSA)
```

### Intentional Realistic Issues Verified:
1. **Missing Referenced Evidence**: Both FIR and Witness Statement refer to CCTV footage, but the actual CCTV recording was not provided.
2. **Contradiction**: FIR records time as 8:00 PM; Witness Statement records time as 9:00 PM.
3. **Evidentiary Verification**: WhatsApp chats seized on mobile phone lack mandatory electronic evidence certificate under Section 63 of Bharatiya Sakshya Adhiniyam (BSA), and chain of custody documentation is absent.
4. **Allegation vs. Fact**: Injury origin is stated as an allegation by the complainant, labeled as requiring independent medical-legal verification.

---

## 8. Test Execution & Verification Results

### Unit Tests (`tests/test_case_rag.py`)
| Test ID | Test Name | Status | Description |
| :--- | :--- | :---: | :--- |
| 01 | `test_01_pdf_page_extraction_preserves_provenance` | **PASSED** | Extracts text with 100% physical page number preservation. |
| 02 | `test_02_chunk_metadata_preservation` | **PASSED** | Verifies `chunk_id`, `page_number`, `document_name`, `case_id`. |
| 03 | `test_03_case_isolation_security` | **PASSED** | Proves Case A documents can never be retrieved for Case B. |
| 04 | `test_04_contradiction_retrieval` | **PASSED** | Retrieves both FIR and Witness chunks covering 8:00 PM vs 9:00 PM. |
| 05 | `test_05_evidence_gap_cctv_retrieval` | **PASSED** | Retrieves CCTV references from both documents for gap synthesis. |
| 06 | `test_06_empty_case_handling` | **PASSED** | Safely detects 0 documents and returns structured guidance. |
| 07 | `test_07_source_provenance_page_accuracy` | **PASSED** | Ensures source references match exact physical pages (Page 1, 2). |
| 08 | `test_08_statutory_and_case_rag_separation` | **PASSED** | Verifies statutory corpus is never mixed with case documents. |

**Summary: 8 passed in 15.92s.**

---

### Statutory RAG Regression Tests (`tests/test_rag_pipeline_fixed.py`)
| Test ID | Test Name | Status | Invariant Verified |
| :--- | :--- | :---: | :--- |
| 01 | `test_1_bns_section_103_in_corpus` | **PASSED** | BNS murder provision retrieved accurately. |
| 02 | `test_2_bnss_section_482_in_corpus` | **PASSED** | BNSS anticipatory bail retrieved accurately. |
| 03 | `test_3_bsa_section_63_in_corpus` | **PASSED** | BSA electronic records retrieved accurately. |
| 04 | `test_4_bns_bnss_bsa_domain_separation` | **PASSED** | Domain boundaries strictly enforced. |
| 05 | `test_5_fake_bns_999_rejection` | **PASSED** | Non-existent sections rejected by relevance gate. |
| 06-14 | Out-of-Corpus Safety Tests (NI Act, IT Act, etc.) | **PASSED** | Safely abstains on non-BNS/BNSS/BSA law. |
| 15-17 | Temporal Guard Tests (June 15 vs July 1/2, 2024) | **PASSED** | Enforces Indian Penal Code vs. BNS timeline cutoffs. |

**Summary: 17 passed in 8.79s.**

---

### Live End-to-End Integration Tests (`scripts/test_case_rag_e2e.py`)
Executed against the running server (`http://localhost:8008`):

| Test ID | Test Description | Live Result |
| :---: | :--- | :--- |
| 1 | Health check confirms both `rag` and `case_rag` loaded | `healthy`, `is_loaded: true`, GPU 2 |
| 2 | Conversational bypass ("Hi") | Returns conversational reply, 0 sources, 0 RAG overhead |
| 3 | Statutory query ("What is BNS Section 103?") | Uses Legal RAG + V2 adapter, returns BNS statute sources |
| 4 | Out-of-corpus statutory query (NI Act Section 138) | Safely abstains; does NOT allow Case Analysis adapter to guess |
| 5 | Empty case question ("Analyze this case") | Returns: *"Insufficient case material. No case documents are currently available..."* |
| 6 | Synthetic demo documents upload & indexing | 4/4 documents processed: FIR (2p), Witness (2p), Medical (1p), Seizure (1p) |
| 7 | Document list verification | Returns 4 indexed documents with correct page counts |
| 8 | Evidence gap query ("What evidence is missing?") | Identifies CCTV footage referenced in FIR & Witness but missing from supplied files |
| 9 | Contradiction query ("Are there contradictions?") | Identifies timing discrepancy: FIR records 8:00 PM while Witness records 9:00 PM |
| 10 | Evidentiary verification query ("Check electronic evidence") | Identifies lack of Section 63 BSA certificate and chain of custody documentation |
| 11 | Hearing prep query ("Prepare me for next hearing") | Returns structured case strengths, weaknesses, and hearing preparation recommendations |
| 12 | Cross-case isolation security check | Querying Case B for Case A content returns 0 Case A documents |

**Summary: 12 passed, 0 failed.**

---

## 9. Immutability & File Invariants

The following critical files and models were **strictly untouched and unaltered**:

1. `outputs/qwen14b-legalai-v2/` — **UNTOUCHED / FROZEN**
2. `outputs/qwen14b-case-analysis-v1/` — **UNTOUCHED / FROZEN**
3. `data/legal_eval_125.jsonl` — **UNTOUCHED (125 lines, sha256: `92c3fcb013...`)**
4. `src/rag/` statutory pipeline files — **UNTOUCHED**
5. `data/legalai_rag_mvp.db` — **UNTOUCHED**

---

## 10. Known Limitations & Operating Boundaries

1. **Document Formats**: Native text extraction is supported for standard text-based PDF, UTF-8 TXT, and DOCX (via python-docx). Scanned image PDFs without embedded OCR text layers require an upstream OCR engine (e.g., Tesseract or OCR-my-PDF) before ingestion.
2. **Retrieval Granularity**: Retrieval chunks are bounded to individual physical pages (typically 500 characters with 100 character overlap). Multi-page tables spanning continuous leaves are indexed as page-specific segments.
3. **Statutory Coverage**: Statutory legal grounding is limited to the current authoritative corpus (Bharatiya Nyaya Sanhita, Bharatiya Nagarik Suraksha Sanhita, Bharatiya Sakshya Adhiniyam). Outside statutes (e.g., Negotiable Instruments Act, Companies Act) safely trigger the statutory abstention gate.
4. **Legal Admissibility**: The system functions strictly as a lawyer-support and case-analysis copilot. It explicitly identifies evidentiary verification requirements and does not guarantee court admissibility or outcome. Final legal determinations remain the advocate's professional responsibility.
