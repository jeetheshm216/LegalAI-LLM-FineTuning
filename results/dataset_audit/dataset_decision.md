# LegalAI Dataset Strategic Decisions & Recommendation Matrix

**Date:** 2026-09-14  
**Status:** Audit Complete — Zero Weights Modified — Zero Finetuning Started  

---

## 1. Summary of Strategic Classifications

| Dataset Name | Source Identifier | Audit Recommendation | Strategic Role in LegalAI Ecosystem |
| :--- | :--- | :---: | :--- |
| **legalai_1000_realistic_lawyer_queries** | `data/legal_train.jsonl` | **PRIMARY_TRAINING** | Core high-fidelity instruction and reasoning backbone. |
| **IndicLegalQA** | GitHub: `R-A-J-1-3/Law-Advisor/data/indiclegalqa.json` | **FILTER_FIRST** | Secondary training dataset for Supreme Court Case Analysis (after removing ~3,500 mechanical 'Who is appellant' questions). |
| **Sakib-Dalal/IndianLegal-QA** | Hugging Face: `Sakib-Dalal/IndianLegal-QA` | **FILTER_FIRST** | Domain expansion corpus for non-criminal statutes (Constitution, Contract, Consumer Law) after stripping repealed IPC/CrPC & document layout artifacts. |
| **faizmubeen/legal_queries_data** | Hugging Face: `faizmubeen/legal_queries_data` | **EVALUATION_ONLY** | Held-out real-world public query evaluation set (after manual PII anonymization and alignment scrubbing). |

---

## 2. Granular Dataset Decisions & Justifications

### Decision 1: `legalai_1000_realistic_lawyer_queries` → `PRIMARY_TRAINING`
- **Role:** Foundational training curriculum.
- **Justification:**
  - 100% compliant with the post-1 July 2024 legal framework (BNS, BNSS, BSA).
  - 0% hallucinated statutes or provisions.
  - Zero PII exposure.
  - Formatted strictly in standard conversational `messages` schema compatible with modern LoRA/SFT trainers.

### Decision 2: `IndicLegalQA` → `FILTER_FIRST` (Target: ~6,500 High-Yield Case Analysis Records)
- **Role:** Specialized Case Analysis and Judicial Precedent module.
- **Filtering Rules Required Before Any Training:**
  1. **Drop Identity Trivia:** Discard all records matching regex `r"who (is|was) the (appellant|respondent|petitioner)"i`.
  2. **Retain Legal Doctrines:** Keep questions addressing holdings, statutory interpretations, constitutional determinations, and legal principles applied by the Supreme Court.
  3. **Format Standardization:** Convert from flat `case_name / judgement_date / question / answer` into structured legal analysis prompts:
     `"Case Context: [case_name] ([judgement_date])
Question: [question]"` → `"Legal Holding: [answer]"`.

### Decision 3: `Sakib-Dalal/IndianLegal-QA` → `FILTER_FIRST` (Target: ~15,000–20,000 Clean Statutory Records)
- **Role:** Broad statutory coverage expansion.
- **Filtering Rules Required Before Any Training:**
  1. **Purge Repealed Law:** Completely filter out all records referencing the Indian Penal Code, 1860, Code of Criminal Procedure, 1973, or Indian Evidence Act, 1872.
  2. **Purge Layout Artifacts:** Filter out any record containing `"in this document"`, `"in this edition"`, `"in Appendix"`, `"Schedule table"`.
  3. **Isolate High-Value Civil/Constitutional Law:** Retain verified QA on the Constitution of India, Indian Contract Act, Arbitration Act, and Consumer Protection Act.

### Decision 4: `faizmubeen/legal_queries_data` → `EVALUATION_ONLY` / `DO_NOT_USE` for Training
- **Role:** Out-of-domain evaluation benchmark.
- **Justification:**
  - Containing only 422 rows, it offers negligible volume for model training.
  - Data corruption (mismatched question-answer pairs like row 2) would degrade model precision.
  - Real un-anonymized citizen PII makes it unsafe for weight ingestion.
  - Evaluators can use a curated, anonymized 100-question subset to benchmark how well LegalAI interprets messy layperson queries without citing wrong statutes.

---

## 3. Strict Execution Boundary Confirmation

In strict compliance with user instructions:
- **Zero fine-tuning was initiated.**
- **V2 LoRA adapter remains untouched.**
- **Existing RAG database and integration remain untouched.**
- **Zero GPU training processes were started.**
- **Zero git commits or pushes were executed.**
