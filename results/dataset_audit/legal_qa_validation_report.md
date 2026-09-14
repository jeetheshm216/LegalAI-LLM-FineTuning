# Legal QA Automated Validation Audit Report

**Execution Date:** 2026-09-14 12:59:02  
**Input Cleaned Dataset:** `data/case_analysis/legal_qa_cleaned.jsonl`  
**Output Validated Dataset:** `data/case_analysis/legal_qa_validated.jsonl`  
**Authoritative Reference DB:** `data/legalai_rag_mvp.db` (BNS: 358, BNSS: 531, BSA: 170)  
**Total Records Audited:** 128,372  
**Processing Duration:** 13.34 seconds  

---

## 1. Executive Validation Classification

A dataset answer is **not automatically legally correct**. The automated validation pipeline evaluated all records for statutory citation accuracy, temporal non-retroactivity (Article 20(1)), authoritative RAG backing, question-answer relevance, and domain consistency.

| Validation Status | Count | Percentage | Fine-Tuning SFT Recommendation |
| :--- | :---: | :---: | :--- |
| **VALIDATED** | **1,803** | **1.40%** | **Approved**: Safe for direct SFT fine-tuning. Grounded in authoritative statute or verified historical precedent. |
| **LIKELY_VALID** | **101,319** | **78.93%** | **Permitted**: Substantive, domain-consistent reasoning. External source not in 3-Act local corpus (`LEGAL_SOURCE_NOT_AVAILABLE`). |
| **REVIEW_REQUIRED** | **22,434** | **17.48%** | **Hold for Legal Review**: Contains minor defects (terse extract, potential outdated repealed reference, or borderline relevance). |
| **UNSUPPORTED** | **0** | **0.00%** | **Exclude**: Unsubstantiated claims lacking statutory or precedential backing. |
| **INVALID** | **2,816** | **2.19%** | **DO NOT USE**: Fatal defects detected (anachronistic citation, out-of-bounds section, Article 20(1) retroactivity violation, or gross Q-A mismatch). |

---

## 2. Dataset-Wise Validation Breakdown

| Dataset | Total | VALIDATED | LIKELY_VALID | REVIEW_REQUIRED | UNSUPPORTED | INVALID | SFT Safe Rate (Val + Likely) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **IndicLegalQA** | 9,694 | 852 | 8,840 | 2 | 0 | 0 | **99.98%** |
| **Sakib-Dalal/IndianLegal-QA** | 117,135 | 788 | 91,111 | 22,426 | 0 | 2,810 | **78.46%** |
| **faizmubeen/legal_queries_data** | 419 | 6 | 404 | 6 | 0 | 3 | **97.85%** |
| **legalai_1000_realistic_lawyer_queries** | 1,124 | 157 | 964 | 0 | 0 | 3 | **99.73%** |

---

## 3. Detailed Validation Dimension Metrics

### A. Statutory Citation Check
| Citation Status | Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **VALID_STATUTORY_CITATIONS** | 193 | 0.15% | Validated against BNS/BNSS/BSA authoritative section registry |
| **LEGAL_SOURCE_NOT_AVAILABLE** | 5,604 | 4.37% | Statutory source outside local 3-Act corpus (Constitution, CPC, NI Act, etc.) |
| **NO_STATUTORY_CITATIONS** | 122,571 | 95.48% | Principle-based or procedural question without explicit section citation |
| **INVALID_CITATION_DETECTED** | 4 | 0.00% | Confabulation detected (e.g. Section 65B BSA, Section 999 BNS) |

### B. Temporal & Article 20(1) Non-Retroactivity Check
| Temporal Status | Count | Percentage | Notes |
| :--- | :---: | :---: | :--- |
| **CURRENT_LAW** | 197 | 0.15% | Reflects post-July 1, 2024 active enactments (BNS, BNSS, BSA) |
| **HISTORICALLY_VALID** | 2,333 | 1.82% | Valid historical Supreme Court precedent under IPC/CrPC |
| **TEMPORAL_NEUTRAL** | 125,837 | 98.03% | Procedural, constitutional, or timeless legal principles |
| **OUTDATED_REPEALED_LAW** | 5 | 0.00% | Modern query invoking repealed IPC/CrPC without transition context |
| **RETROACTIVE_APPLICATION_SUSPECTED** | 0 | 0.00% | Offence committed pre-July 2024 charged under new Sanhita (Article 20(1) violation) |

### C. Legal Authoritative Source Support (Local RAG Corpus)
| Authoritative Support Status | Count | Percentage |
| :--- | :---: | :---: |
| **AUTHORITATIVELY_SUPPORTED** | 193 | 0.15% |
| **LEGAL_SOURCE_NOT_AVAILABLE** | 128,175 | 99.85% |
| **CONTRADICTS_AUTHORITATIVE_STATUTE** | 4 | 0.00% |
| **UNSUPPORTED** | 0 | 0.00% |

---

## 4. Top Detected Issues & Anomalies

| Detected Issue Category | Occurrences | Action Taken |
| :--- | :---: | :--- |
| **Answer is excessively terse (0 words)** | 17,964 | Flagged in record validation object |
| **Answer is excessively terse (1 words)** | 2,854 | Flagged in record validation object |
| **Answer has zero semantic overlap with question keywords** | 2,812 | Flagged in record validation object |
| **Answer is excessively terse (2 words)** | 1,215 | Flagged in record validation object |
| **Question asks about current law but answer exclusively relies on repealed IPC/CrPC without transition caveat** | 5 | Flagged in record validation object |
| **Section 375 BNS exceeds maximum statutory bound of 358** | 1 | Flagged in record validation object |
| **Anachronistic/Fabricated citation** | 1 | Flagged in record validation object |
| **Section 512 BNS exceeds maximum statutory bound of 358** | 1 | Flagged in record validation object |
| **Section 378 BNS exceeds maximum statutory bound of 358** | 1 | Flagged in record validation object |

---

## 5. Exemplary Flagged Records Unsuitable for Fine-Tuning

Below are representative examples flagged by the pipeline:

### Sample 1: `LQD_000010` (faizmubeen/legal_queries_data)
- **Question:** A user was in a relationship for 12 to 15 years with a person who said he was divorced and proposed ...
- **Answer Extract:** The advice states that an aggrieved woman can file multiple cases against a person who cheated her with false promises of marriage if she can prove th...
- **Flagged Issues:**
  - ⚠️ `Section 375 BNS exceeds maximum statutory bound of 358`

### Sample 2: `LQD_000092` (faizmubeen/legal_queries_data)
- **Question:** If a person was taken into the 12th grade as a regular student, attended classes, and his father, a ...
- **Answer Extract:** ...
- **Flagged Issues:**
  - ⚠️ `Answer is excessively terse (0 words)`
  - ⚠️ `Answer has zero semantic overlap with question keywords`

### Sample 3: `LQD_000180` (faizmubeen/legal_queries_data)
- **Question:** Who is guilty of abetting an offence according to the text?...
- **Answer Extract:** Person A, whether the act is committed or not....
- **Flagged Issues:**
  - ⚠️ `Answer has zero semantic overlap with question keywords`

### Sample 4: `INLQA_000011` (Sakib-Dalal/IndianLegal-QA)
- **Question:** What is the subject matter of laws made by Parliament and by the Legislatures of States?...
- **Answer Extract:** This information is covered under Article 246....
- **Flagged Issues:**
  - ⚠️ `Answer has zero semantic overlap with question keywords`

### Sample 5: `INLQA_000352` (Sakib-Dalal/IndianLegal-QA)
- **Question:** Name three types of goods that fell under the temporary powers granted to Parliament....
- **Answer Extract:** These include cotton and woollen textiles, food-stuffs, and coal....
- **Flagged Issues:**
  - ⚠️ `Answer has zero semantic overlap with question keywords`

---

## 6. Execution Safeguards Confirmed

- **Zero fine-tuning was performed.**
- **LegalAI V2 LoRA adapter remains untouched.**
- **Production RAG database remains untouched.**
- **All 128,372 cleaned records were preserved** in `data/case_analysis/legal_qa_validated.jsonl` with enriched validation metadata.
