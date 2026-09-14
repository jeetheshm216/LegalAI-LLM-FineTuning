# LegalAI Case Analysis Training Dataset Generation Report

**Date:** 2026-09-14 13:22:05  
**Total Unique Cases:** 2,377  
**Total Generated Examples:** 7,260  
**Splitting Strategy:** Strictly by `case_id` (Random Seed = 42)  
**Split Proportions:** 80% Train, 10% Validation, 10% Test  

---

## 1. Executive Summary & Split Statistics

| Split | Number of Unique Cases | Case Percentage | Number of Examples | Example Percentage | Output Path |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Train** | **1,901** | 80.00% | **5,786** | **79.70%** | `data/case_analysis/case_analysis_train.jsonl` |
| **Validation** | **237** | 10.00% | **730** | **10.06%** | `data/case_analysis/case_analysis_validation.jsonl` |
| **Test** | **239** | 10.00% | **744** | **10.25%** | `data/case_analysis/case_analysis_test.jsonl` |
| **Total Master** | **2,377** | 100.00% | **7,260** | 100.00% | `data/case_analysis/case_analysis_master.jsonl` |

> [!IMPORTANT]
> **Zero Case Leakage Verified**: Documents and questions from the same case are strictly quarantined within a single split. No case present in `train` appears in `validation` or `test`.

---

## 2. Coverage Across 24 Case Analysis Tasks (`CA01` - `CA24`)

| Task Code | Task Description | Total Examples | Train | Validation | Test |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **CA01_CASE_OVERVIEW** | Provide a comprehensive case overview, identi... | 281 | 224 | 23 | 34 |
| **CA02_KEY_FACTS** | Extract and organize the operative material f... | 296 | 243 | 28 | 25 |
| **CA03_CHRONOLOGY** | Construct a chronological timeline of events ... | 296 | 228 | 37 | 31 |
| **CA04_LEGAL_ISSUES** | Identify and formulate the substantive legal ... | 315 | 250 | 31 | 34 |
| **CA05_EVIDENCE_ANALYSIS** | Evaluate the evidence currently available on ... | 306 | 249 | 32 | 25 |
| **CA06_EVIDENCE_GAPS** | Identify critical evidentiary gaps in the sup... | 337 | 268 | 34 | 35 |
| **CA07_CONTRADICTION_DETECTION** | Examine the record for internal factual incon... | 308 | 254 | 24 | 30 |
| **CA08_STRENGTH_ANALYSIS** | Analyze the strongest factual and legal pilla... | 284 | 224 | 31 | 29 |
| **CA09_WEAKNESS_ANALYSIS** | Identify potential vulnerabilities, evidentia... | 306 | 243 | 33 | 30 |
| **CA10_ARGUMENT_GENERATION** | Formulate a structured legal argument on beha... | 281 | 218 | 31 | 32 |
| **CA11_COUNTERARGUMENTS** | Anticipate the primary counterarguments the a... | 332 | 251 | 37 | 44 |
| **CA12_WITNESS_CROSS_EXAMINATION** | Draft key lines of cross-examination and impe... | 310 | 256 | 28 | 26 |
| **CA13_DOCUMENT_REVIEW** | Conduct a critical legal review of the primar... | 307 | 243 | 30 | 34 |
| **CA14_FACT_TO_LAW_MAPPING** | Map the specific facts established on record ... | 311 | 254 | 29 | 28 |
| **CA15_PRECEDENT_RESEARCH** | Formulate legal research directions, identify... | 292 | 232 | 31 | 29 |
| **CA16_HEARING_PREPARATION** | Prepare a focused bench-hearing strategy, inc... | 286 | 222 | 32 | 32 |
| **CA17_PROCEDURE** | Advise on the correct procedural route, neces... | 292 | 234 | 27 | 31 |
| **CA18_LIMITATION_JURISDICTION** | Assess the limitation period for filing this ... | 313 | 242 | 28 | 43 |
| **CA19_DRAFT_REVIEW** | Review the draft pleadings/petition for essen... | 298 | 250 | 25 | 23 |
| **CA20_APPEAL_ANALYSIS** | Analyze the appealability of the impugned ord... | 299 | 241 | 32 | 26 |
| **CA21_RISK_ANALYSIS** | Perform a comprehensive risk assessment, quan... | 304 | 244 | 30 | 30 |
| **CA22_SETTLEMENT** | Evaluate the feasibility of settlement, calcu... | 306 | 248 | 33 | 25 |
| **CA23_CLIENT_INTAKE** | Conduct a legal intake analysis, identifying ... | 308 | 241 | 36 | 31 |
| **CA24_CASE_STRATEGY** | Develop a comprehensive litigation roadmap an... | 292 | 227 | 28 | 37 |

---

## 3. Practice Area Distribution

| Practice Area | Count of Examples | Percentage |
| :--- | :---: | :---: |
| **Criminal Law** | 2,878 | 39.64% |
| **Civil & Appellate Law** | 1,092 | 15.04% |
| **Constitutional Law** | 692 | 9.53% |
| **Service & Administrative Law** | 676 | 9.31% |
| **Commercial Law** | 668 | 9.20% |
| **Family Law** | 320 | 4.41% |
| **General Law** | 282 | 3.88% |
| **Contract Law** | 236 | 3.25% |
| **Company Law** | 86 | 1.18% |
| **Property Law** | 80 | 1.10% |
| **Evidence Law** | 58 | 0.80% |
| **Arbitration Law** | 52 | 0.72% |
| **Intellectual Property** | 50 | 0.69% |
| **Consumer Law** | 36 | 0.50% |
| **Banking & Negotiable Instruments** | 22 | 0.30% |
| **Customs & Tariff** | 18 | 0.25% |
| **Cyber & Data Privacy Law** | 14 | 0.19% |

---

## 4. Factual Traceability & Grounding Guardrails Enforced

1. **Strict Factual Traceability**:
   - All factual statements in model responses are anchored exclusively in the supplied `CASE MATERIAL`.
   - Never hallucinates dates, quotations, sections, or witnesses not in record.

2. **Honesty on Missing Information**:
   - When evidence is absent, the model explicitly responds:
     > *"The supplied case material does not establish this."*
   - Absence of evidence is not converted into a factual finding.

3. **8-Part Argument Schema**:
   - Every argument task adheres to:
     `Argument` → `Supporting facts` → `Supporting evidence` → `Applicable law` → `Reasoning` → `Likely counterargument` → `Response` → `Remaining uncertainty`.

4. **Non-Dogmatic Weakness & Tactical Restraint**:
   - Avoids defeatist statements (*"We will lose"*); uses *"Potential weakness"*, *"Potential risk"*, *"Requires verification"*.
   - Never guarantees judicial outcomes; uses *"possible approach"*, *"potential argument"*, *"subject to verification"*.

---

## 5. Sample Formatted Training Example (`messages` Schema)

```json
{
  "id": "CA_000001",
  "case_id": "CASE_SC_0001",
  "task_type": "CA15_PRECEDENT_RESEARCH",
  "practice_area": "Service & Administrative Law",
  "split": "train",
  "messages": [
    {
      "role": "user",
      "content": "CASE MATERIAL:\n...\n\nLAWYER QUERY:\nCA15_PRECEDENT_RESEARCH"
    },
    {
      "role": "assistant",
      "content": "LEGAL ISSUES
- Precedential authority governing Service & Administrative Law.

ANALYSIS
RESEARCH DIRECTIONS:
1. Identify binding Supreme Court or jurisdictional High Court decisions addressing the exact statutory section in dispute.
2. Distinguish unfavorable rulings by establishing that those cases..."
    }
  ]
}
```

---

## 6. Execution Safeguards Confirmed

- **Fine-tuning was NOT started.**
- **Existing LegalAI V2 LoRA adapter remains untouched.**
- **Production RAG database remains untouched.**
- **Raw datasets remain untouched.**
