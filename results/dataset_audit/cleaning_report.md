# LegalAI Dataset Cleaning and Deduplication Report

**Execution Timestamp:** 2026-09-14 12:42:56  
**Input Master Corpus:** `data/case_analysis/query_corpus_master.jsonl`  
**Output Cleaned Corpus:** `data/case_analysis/legal_qa_cleaned.jsonl`  
**Output Rejected Corpus:** `data/case_analysis/legal_qa_rejected.jsonl`  

---

## 1. Executive Summary & Quality Retention

| Metric | Count | Percentage of Input |
| :--- | :---: | :---: |
| **Total Input Records** | **132,186** | 100.00% |
| **Cleaned & Accepted Records** | **128,372** | **97.11%** |
| **Total Rejected Records** | **3,814** | **2.89%** |
| **Exact / Normalized Duplicates Removed** | 3,753 | 2.84% |
| **Mechanical Identity Templates Removed** | 5 | 0.00% |
| **Document-Layout Artifacts Removed** | 23 | 0.02% |
| **Low-Information Questions Filtered** | 30 | 0.02% |
| **Corrupted Scrapes / Meta-Artifacts Filtered** | 1 | 0.00% |
| **Spam / Solicitation Filtered** | 2 | 0.00% |

---

## 2. Dataset-Wise Retention & Quality Audit

| Dataset Name | Input Records | Accepted Records | Retention Rate | Primary Rejection Reasons |
| :--- | :---: | :---: | :---: | :--- |
| **legalai_1000_realistic_lawyer_queries** | 1,124 | **1,124** | **100.00%** | None (Gold standard synthetic curriculum) |
| **IndicLegalQA** | 10,000 | **9,694** | **96.94%** | Mechanical identity queries (*"Who is appellant/respondent"*) |
| **Sakib-Dalal/IndianLegal-QA** | 120,640 | **117,135** | **97.09%** | Document artifacts (*"in this edition"*, *"in Appendix"*), duplicates |
| **faizmubeen/legal_queries_data** | 422 | **419** | **99.29%** | Scrape corruption (mixed answers), solicitation |

---

## 3. Answer Quality Distribution (Cleaned Corpus)

| Answer Quality Grade | Count | Percentage | Definition & Criteria |
| :--- | :---: | :---: | :--- |
| **HIGH** | 5,461 | 4.25% | Substantive, reasoned answer with statutory citation or canonical query structure |
| **MEDIUM** | 87,420 | 68.10% | Legally sound explanation (>15 words) or historical context |
| **LOW** | 35,491 | 27.65% | Terse or factual extract (<10 words) |
| **REVIEW_REQUIRED** | 0 | 0.00% | Flagged for manual legal review |

---

## 4. PII Classification & Risk Breakdown

| PII Status | Count | Percentage | Handling Protocol |
| :--- | :---: | :---: | :--- |
| **NONE** | 128,345 | 99.98% | Clean; hypothetical or public statutory text |
| **POSSIBLE** | 21 | 0.02% | Contains personal narrative context (e.g. matrimonial disputes) |
| **REVIEW_REQUIRED** | 6 | 0.00% | Contains direct contact patterns; isolated for human review |

---

## 5. Duplicate Grouping Integrity

- **Total Deduplication Groups Created:** 1,250
- **Primary Representative Retention:** In every duplicate cluster, the highest-quality representative was preserved with `dedup_group_id` and provenance tracking (`duplicate_ids: [...]`).
- **Zero Loss of Meaningful Short Questions:** Meaningful short questions such as *"What is the limitation period?"*, *"What are the grounds for bail?"*, and *"Can this order be challenged?"* were strictly preserved.

---

## 6. Execution Safeguards Confirmed

- **Zero fine-tuning was initiated.**
- **V2 LoRA adapter remains untouched.**
- **Production RAG database remains untouched.**
- **Zero raw dataset files were modified.**
