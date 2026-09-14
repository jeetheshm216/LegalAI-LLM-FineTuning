# LegalAI Dataset Acquisition & Normalization Report

**Timestamp:** 2026-09-14 12:40:24  
**Target Environment:** `/home/sece2026-student07/legalai-finetuning`  
**Pipeline Status:** COMPLETE — 100% Data Fidelity Achieved  

---

## 1. Input vs Normalized Counts Summary

| Dataset Name | Source Identifier | Raw Input Count | Normalized Count | Errors / Discarded | Retention Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **faizmubeen/legal_queries_data** | Hugging Face: `faizmubeen/legal_queries_data` | 422 | 422 | 0 | **100.0%** |
| **IndicLegalQA** | GitHub: `R-A-J-1-3/Law-Advisor` | 10,000 | 10,000 | 0 | **100.0%** |
| **Sakib-Dalal/IndianLegal-QA** | Hugging Face: `Sakib-Dalal/IndianLegal-QA` | 120,640 | 120,640 | 0 | **100.0%** |
| **legalai_1000_realistic_lawyer_queries** | Local canonical: `data/legal_train.jsonl` | 1,124 | 1,124 | 0 | **100.0%** |
| **TOTAL UNIFIED MASTER CORPUS** | `data/case_analysis/query_corpus_master.jsonl` | **132,186** | **132,186** | **0** | **100.0%** |

---

## 2. Source Type Distribution

| Canonical Source Type | Record Count | Percentage | Primary Legal Role |
| :--- | :---: | :---: | :--- |
| `legal_document_derived_qa` | 120,640 | 91.27% | Statutory reading comprehension & legislative structure |
| `judgment_derived_question` | 10,000 | 7.57% | Supreme Court precedent holding & case law reasoning |
| `synthetic_realistic_lawyer_query` | 1,124 | 0.85% | Core realistic practitioner advisory curriculum |
| `public_user_legal_query` | 422 | 0.32% | Real-world layperson forum consultation testing |

---

## 3. Domain & Legal Practice Area Distribution

| Practice Area Domain | Record Count | Percentage |
| :--- | :---: | :---: |
| **General Law** | 87,814 | 66.43% |
| **Criminal Law** | 12,815 | 9.69% |
| **Family Law** | 7,175 | 5.43% |
| **Company Law** | 5,230 | 3.96% |
| **Constitutional Law** | 5,137 | 3.89% |
| **Property Law** | 3,755 | 2.84% |
| **Contract Law** | 3,152 | 2.38% |
| **Customs & Tariff** | 2,892 | 2.19% |
| **Evidence Law** | 2,653 | 2.01% |
| **Arbitration Law** | 767 | 0.58% |
| **Intellectual Property** | 295 | 0.22% |
| **Consumer Law** | 220 | 0.17% |
| **Banking & Negotiable Instruments** | 189 | 0.14% |
| **Cyber & Data Privacy Law** | 92 | 0.07% |

---

## 4. Language & Field Integrity

- **Language Distribution:**
  - `en`: 132,186 records (100.00%)

- **Records with Answer Provided:** 132,185 (100.00%)
- **Records with Answer=Null (Query-Only):** 1 (0.00%)
- **Records with Extracted Citations:** 23,508 (17.78%)
- **Normalization Errors Logged:** 0 (Logged in `data/external/normalization_errors.jsonl`)

---

## 5. Master Files & Checksums

| File Artifact | File Path | Record Count | SHA-256 Checksum |
| :--- | :--- | :---: | :--- |
| **Legal Queries Data (Raw)** | `data/external/raw/legal_queries_data/legal_queries_data.csv` | 422 | `708ed8f894bb5366...` |
| **Legal Queries Data (Norm)** | `data/external/normalized/legal_queries_data.jsonl` | 422 | `e2a537427c367e33...` |
| **IndicLegalQA (Raw)** | `data/external/raw/indiclegalqa/indiclegalqa.json` | 10,000 | `ab4bcd1168d7d22c...` |
| **IndicLegalQA (Norm)** | `data/external/normalized/indiclegalqa.jsonl` | 10,000 | `f6c1261dca6540bc...` |
| **IndianLegal-QA (Raw)** | `data/external/raw/indianlegalqa/question_answers.csv` | 120,640 | `49178756a338f99c...` |
| **IndianLegal-QA (Norm)** | `data/external/normalized/indianlegalqa.jsonl` | 120,640 | `caa6cb4dacfa0ed3...` |
| **Synthetic Lawyer Queries (Raw)** | `data/external/raw/legalai_1000_realistic_lawyer_queries/legalai_1000_realistic_lawyer_queries.jsonl` | 1,124 | `98b2bed669130a46...` |
| **Synthetic Lawyer Queries (Norm)** | `data/external/normalized/legalai_1000_realistic_lawyer_queries.jsonl` | 1,124 | `3169f073d571b8a2...` |
| **Unified Master Query Corpus** | `data/case_analysis/query_corpus_master.jsonl` | **132,186** | `9eff2271b69c76b0...` |
| **Dataset Manifest** | `data/external/metadata/dataset_manifest.json` | 1 | `0d639e81f6dcda2d...` |

---

## 6. Execution Safeguards Confirmed

- **Zero fine-tuning was initiated.**
- **V2 LoRA adapter remains untouched.**
- **Production RAG database remains untouched.**
- **Zero git commits or pushes executed.**
