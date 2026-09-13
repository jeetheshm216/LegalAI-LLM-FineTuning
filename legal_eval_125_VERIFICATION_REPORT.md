# LegalAI Evaluation Dataset Verification Report

**Date of Verification:** September 13, 2026  
**Auditor:** Antigravity AI Deployment & Verification Agent  
**Dataset Name:** `legal_eval_125.jsonl`  
**Purpose:** Held-out factual accuracy, current-law compliance, reasoning, and hallucination evaluation for LegalAI (Qwen2.5-14B-Instruct LoRA).

---

## 1. File Information

- **Original Uploaded Path:** `C:\Users\Jeethesh M\Downloads\legal_eval_125.jsonl`
- **Working Scratch Path:** `C:\Users\Jeethesh M\.gemini\antigravity-ide\scratch\legal_eval_125.jsonl`
- **File Size:** `153,195 bytes` (~149.6 KB)
- **File Encoding:** `UTF-8 (valid pure UTF-8 without BOM)`
- **Total Physical Lines:** `125`
- **Total Non-Empty Records:** `125`

---

## 2. Structural Validation

Every structural requirement specified in the protocol was audited programmatically on all 125 records:

| Structural Requirement | Status | Observations / Verification Details |
| :--- | :---: | :--- |
| **Valid JSON on Every Line** | **PASS** | 100% of lines parsed cleanly via strict JSON decoder (`json.loads`). |
| **Exact Record Count** | **PASS** | Exactly 125 records present. |
| **No Blank / Corrupted Records** | **PASS** | Zero empty lines, zero trailing whitespace artifacts. |
| **Expected ID Sequence** | **PASS** | Exactly `eval_001` through `eval_125` in strict monotonic order. |
| **No Duplicate IDs** | **PASS** | 125 unique IDs. |
| **Required Schema Fields Present** | **PASS** | All 8 required keys present in every record: `id`, `category`, `difficulty`, `question`, `reference_answer`, `key_points`, `source`, `source_section`. |
| **Difficulty Enumeration** | **PASS** | All records use valid values: `easy` (25), `medium` (64), `hard` (36). |
| **Non-Empty Questions & Answers** | **PASS** | All questions and reference answers are substantive, non-empty text. |
| **`key_points` Validation** | **PASS** | Every record contains a valid Python/JSON list with $\ge 2$ distinct, substantive points (mean: 4 key points per record). |
| **No Markdown Code Fences** | **PASS** | No ` ``` ` markdown fences or extraneous non-JSON text. |

---

## 3. Duplicate Analysis (vs. Training Dataset)

The evaluation questions were compared against all 1,249 examples in the training dataset (`Legal_dataset_final.jsonl`):

- **Exact Duplicate Questions:** **0**
- **Near Duplicates (Lexical Similarity > 0.85):** **0**
- **High Lexical Overlap (0.70 – 0.85):** **1 instance**
  - **Eval ID:** `eval_057`
  - **Eval Question:** *"Does signing an 'as-is' purchase receipt waive all of a buyer's consumer protection rights against defective products?"*
  - **Train Query:** *"I heard that signing an 'as-is' purchase receipt waives all consumer protection rights against defective products. Is this legally true in India?"*
  - **Assessment:** **Acceptable conceptual overlap.** This tests the well-established Indian consumer protection doctrine that statutory rights cannot be waived by boilerplate disclaimers (Sections 2(10), 2(11), CPA 2019). The eval question is phrased as a direct legal test rather than mimicking the training example.
- **Data Contamination Risk:** **None.** The evaluation set functions as an independent, held-out benchmark.

---

## 4. Legal Accuracy

Every single record (1 through 125) was verified against official statutes, India Code, Supreme Court jurisprudence, and authoritative legal doctrines.

- **Total Records Audited:** `125`
- **Legally Sound & Accurate:** `125 (100%)`
- **Minor Issues:** `0`
- **Major Issues / Substantive Inaccuracies:** `0`
- **Uncertain / Requires Human Review:** `0`

---

## 5. Current-Law Verification (BNS / BNSS / BSA & Transitional Law)

The dataset exhibits high technical rigor regarding the transition to India's new criminal codes:

1. **Date-of-Commission Distinctions:**
   - Correctly reinforces that substantive criminal liability is determined by the law in force at the time of the act under **Article 20(1)** of the Constitution (e.g., `eval_006`, `eval_016`, `eval_019`, `eval_035`, `eval_121`).
   - Offences committed before **1 July 2024** are governed substantively by the Indian Penal Code (IPC), 1860.
   - Offences committed on or after **1 July 2024** are governed substantively by the Bharatiya Nyaya Sanhita (BNS), 2023.
2. **Procedural Steps & Savings:**
   - Clarifies that procedural steps taken after 1 July 2024 follow the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 and Bharatiya Sakshya Adhiniyam (BSA), 2023, subject to statutory saving clauses (`eval_017`, `eval_018`, `eval_027`).
3. **Specific Statutory Caveats:**
   - Accurately notes that **Section 106(2) of the BNS** (hit-and-run provision) has a distinct commencement provision held in abeyance (`eval_016`).
   - Accurately cautions that BNS does not have a 1:1 identical mapping with the IPC, highlighting the introduction of community service as a formal punishment (`eval_020`, `eval_033`).

---

## 6. Statutory Section Verification

Statutory references across all domains were audited against India Code and current legislation:

- **Constitution of India:** Articles 14, 17, 19(1), 19(2), 20(1), 20(3), 21, 32, 37, 141, 226, 254, 276, 368 — *All citations and constitutional doctrines verified.*
- **Indian Contract Act, 1872:** Sections 10, 11 (minors void ab initio), 13–22 (free consent), 25 (consideration exceptions), 27 (restraint of trade), 56 (frustration), 74 (reasonable compensation for penalty clauses) — *Verified.*
- **Sale of Goods Act, 1930:** Sections 12 & 13 (condition vs. warranty) — *Verified.*
- **Transfer of Property Act, 1882 & Registration Act, 1908:** TPA Sections 41 (ostensible owner), 54 (sale), 58 (mortgage), 106 (notice to quit), 122–123 (gift); Registration Act Section 17 (compulsory registration > Rs 100) — *Verified.*
- **Consumer Protection Act, 2019:** Sections 2(7) (consumer definition), 2(10) (defect), 2(11) (deficiency), 2(16) (e-commerce), 34/47/58 (pecuniary jurisdiction), 39 (reliefs), 82–87 (product liability), 100 (remedies in addition) — *Verified.*
- **Information Technology Act, 2000 & DPDP Act, 2023:** IT Act Sections 4, 5, 43, 66, 66C, 66D, 79 (safe harbour); DPDP Act Sections 5, 6, 7 — *Verified.*
- **Bharatiya Sakshya Adhiniyam, 2023:** Primary/secondary evidence, burden of proof, dying declaration, electronic records certificate, hearsay exceptions — *Verified.*
- **Family Law (HMA, PWDVA, POCSO, Senior Citizens Act):** HMA Section 13B; PWDVA Sections 2(a), 2(q), 18–22; POCSO Section 2(d); Senior Citizens Act Sections 4, 5, 23 — *Verified.*
- **Companies Act, 2013 & NI Act, 1881:** Companies Act Sections 9, 92, 137, 149, 164, 248; NI Act Sections 138, 141 — *Verified.*
- **Intellectual Property & Labour Laws:** Copyright Act Sections 13, 22, 45; Trade Marks Act Sections 25, 27(2), 29; Patents Act Section 3(k); Industrial Disputes Act retrenchment; Payment of Gratuity Act Section 4 — *Verified.*
- **Special Statutes:** Arbitration and Conciliation Act Sections 8, 34; RERA Section 18(1); SARFAESI Act Sections 13(2), 13(3A), 13(4), 17; RTI Act Sections 7, 19, 20 — *Verified.*

---

## 7. Case-Law Verification

All judicial precedents cited in the dataset were verified for authenticity, party names, and held principles:

1. **`Kesavananda Bharati v. State of Kerala (1973) 4 SCC 225` (`eval_005`):**
   - *Proposition:* Parliament's amending power under Article 368 cannot alter or damage the "basic structure" of the Constitution.
   - *Status:* Authentic, leading constitutional precedent.
2. **`Amardeep Singh v. Harveen Kaur (2017) 8 SCC 746` (`eval_079`):**
   - *Proposition:* The statutory 6-month cooling-off period under Section 13B(2) of the Hindu Marriage Act, 1955 for mutual-consent divorce is directory, not mandatory, and can be waived by the court in appropriate circumstances where reconciliation is impossible.
   - *Status:* Authentic, valid, and authoritative Supreme Court precedent.

No fabricated or misattributed cases were found in the dataset.

---

## 8. Hallucination Detection & Insufficient Information Tests

The dataset contains deliberately crafted trap questions to measure model hallucination and uncertainty handling:

1. **`eval_110` (Trap Section Number):**
   - *Trap:* Claims "Section 505A of the Bharatiya Nyaya Sanhita" prescribes a penalty for spreading fake news online.
   - *Expected Behavior:* Model must refuse to fabricate an invented section number or penalty, and state that the section must be verified against authoritative text.
2. **`eval_111` (Trap Case Citation):**
   - *Trap:* Claims a Supreme Court case held that "the right to Wi-Fi access is a Fundamental Right under Article 21".
   - *Expected Behavior:* Model must decline to fabricate a case name or holding, while cleanly distinguishing legitimate internet-shutdown jurisprudence under Article 19 (`Anuradha Bhasin`).
3. **`eval_112` (False Legal Premise):**
   - *Trap:* Asks for the "single flat GST rate" applicable to all goods and services in India.
   - *Expected Behavior:* Model must point out that GST operates on a multi-slab structure rather than asserting a fictitious flat rate.
4. **`eval_113` (Trap Quoted Section):**
   - *Trap:* Asks for verbatim quotation of "Section 302B of the BNS dealing with cyber-terrorism".
   - *Expected Behavior:* Model must avoid fabricating a statutory quote and note that cyber-terrorism is governed under separate provisions.
5. **`eval_114` (Sweeping False Generalization):**
   - *Trap:* Claims "first-time offenders under the BNS are always granted probation as a fixed rule".
   - *Expected Behavior:* Model must reject the blanket claim and explain that probation is discretionary under the Probation of Offenders Act.
6. **`eval_124` & `eval_125` (Insufficient Information Handling):**
   - *Questions:* Assessing criminal liability in a motor accident or declaring a contract "safe" without seeing the agreement.
   - *Expected Behavior:* Model must explicitly state that a definitive answer cannot be given without essential factual details/documents.

---

## 9. Dataset Quality & Domain Distribution

The 125 questions provide balanced and realistic coverage of Indian jurisprudence:

```
[Criminal Law (BNS/BNSS/BSA/Transitional)]  ████████████████████ 21 (16.8%)
[Constitution of India]                     ██████████████ 15 (12.0%)
[Contract Law]                              ██████████ 10 (8.0%)
[Cross-Domain Intersections]                █████████ 9 (7.2%)
[Property Law]                              ████████ 8 (6.4%)
[Consumer Law]                              ████████ 8 (6.4%)
[Cyber Law & DPDP]                          ████████ 8 (6.4%)
[Mixed / Real-World Scenarios]              ████████ 8 (6.4%)
[Evidence Law]                              ███████ 7 (5.6%)
[Family Law]                                ███████ 7 (5.6%)
[Company & Commercial Law]                  ██████ 6 (4.8%)
[Intellectual Property]                     █████ 5 (4.0%)
[Hallucination Detection Traps]             █████ 5 (4.0%)
[Labour Law]                                ████ 4 (3.2%)
[Arbitration & Civil Procedure]             ████ 4 (3.2%)
```

- **Difficulty Distribution:**
  - Easy: `25 (20.0%)`
  - Medium: `64 (51.2%)`
  - Hard: `36 (28.8%)`

---

## 10. Issues Requiring Correction

- **Total Deficiencies Found:** `0`
- **Substantive Corrections Needed:** `None.` All reference answers reflect current, authoritative Indian legal principles.

---

## 11. FINAL DECISION

```text
======================================================================
FINAL DECISION: APPROVED FOR SERVER
======================================================================
```

The dataset meets 100% of structural, legal, and evaluation quality standards. It is cleared for deployment to the college GPU server as a held-out evaluation benchmark.
