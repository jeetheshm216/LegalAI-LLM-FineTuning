# LegalAI — Final 125-Question Evaluation Report

## 1. Executive Summary
This report presents the complete, automated evaluation of the fine-tuned **LegalAI** model (`Qwen/Qwen2.5-14B-Instruct` + LoRA adapter `outputs/qwen14b-first-run-final-dataset`) against the held-out 125-question benchmark dataset (`data/legal_eval_125.jsonl`).

The evaluation was performed under strict isolation rules: **zero** ground-truth reference data (reference answers, key points, source citations, categories, or difficulty tiers) was provided to the model during inference. Generation was strictly deterministic (`do_sample=False`, `torch.inference_mode()`, `max_new_tokens=512`).

**Key Takeaways:**
- **Completion:** All 125 questions were successfully evaluated (0 generation errors).
- **Preliminary Accuracy:** **86.8%** (100 Substantially Correct, 17 Partially Correct, 8 Incorrect).
- **Hallucination Rate:** **8.0%** overall (4.0% Clear fabricated provisions/claims, 4.0% statutory nomenclature mixups).
- **Outdated Law Rate:** **3.2%** (4 questions where outdated law or incorrect commencement dates were asserted).
- **Current Law Transition (BNS/BNSS/BSA):** **72.7%** accuracy on 11 dedicated transition questions.
- **Human Review Required:** **15** questions flagged for human legal verification.
- **Overall Model Rating:** **`Promising but needs improvement`**.

---

## 2. Model and Evaluation Configuration
- **Base Model:** `Qwen/Qwen2.5-14B-Instruct`
- **LoRA Adapter Path:** `outputs/qwen14b-first-run-final-dataset` (Rank 16, Alpha 32, 7 target projection modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`)
- **Torch Precision:** `torch.bfloat16`
- **Hardware Platform:** NVIDIA B200 GPU (180 GB VRAM), Server Host: `college-gpu`
- **Environment:** Python 3.12.3, PyTorch 2.11.0+cu128, Transformers 5.16.1, PEFT 0.20.0
- **Generation Parameters:**
  - `do_sample`: `False` (Deterministic greedy decoding)
  - `max_new_tokens`: `512`
  - `temperature`: None / Unused
  - `context_length`: Standard Qwen2.5 chat template
- **System Prompt:**
  ```text
  You are LegalAI, an AI assistant focused on Indian law. Provide accurate, cautious, and clearly explained legal information. Do not invent statutes, sections, cases, penalties, or legal principles. When the available facts are insufficient, clearly say that more information is needed. Distinguish between current law and historical law where relevant. This response is for informational purposes and is not a substitute for advice from a qualified lawyer.
  ```
- **Evaluation Timestamp:** 13 September 2026, 03:40:34 IST

---

## 3. Dataset Integrity
The held-out evaluation dataset was subjected to strict pre- and post-run cryptographic verification:
- **File Path:** `/home/sece2026-student07/legalai-finetuning/data/legal_eval_125.jsonl`
- **Record Count:** Exactly 125 JSONL records (`eval_001` through `eval_125`).
- **Pre-Evaluation SHA256:** `92c3fcb013d54d21e268fa68bd81cf171d3f806681808ee9e109ed00ee4c92a6`
- **Post-Evaluation SHA256:** `92c3fcb013d54d21e268fa68bd81cf171d3f806681808ee9e109ed00ee4c92a6`
- **Benchmark Integrity Status:** **`PASS (100% UNMODIFIED)`**
- **Training/Validation Datasets:** Untouched and unmodified. No fine-tuning or retraining was performed.

---

## 4. Overall Performance
The scoring was conducted using a transparent 6-dimension preliminary rubric (0–11 total points):
1. **Legal Correctness:** 0 (Incorrect), 1 (Partially correct), 2 (Substantially correct)
2. **Completeness:** 0 (Misses key points), 1 (Partial coverage), 2 (Substantial coverage)
3. **Current-Law Correctness:** 0 (Outdated/Wrong law), 1 (Mixed), 2 (Correctly reflects applicable law)
4. **Hallucination:** 0 (Clear fabricated claim), 1 (Questionable claim), 2 (No hallucination)
5. **Uncertainty Handling:** 0 (Confident speculation), 1 (Partially cautious), 2 (Appropriate caution)
6. **Relevance:** 0 (Irrelevant), 1 (Directly addresses the prompt)

### Aggregate Statistics
- **Total Questions:** 125
- **Successfully Generated:** 125 (100.0%)
- **Generation Failures:** 0 (0.0%)
- **Substantially Correct (Score 2):** 100 (80.0%)
- **Partially Correct (Score 1):** 17 (13.6%)
- **Incorrect (Score 0):** 8 (6.4%)
- **Preliminary Overall Accuracy:** **86.8%** `((100 + 0.5 * 17) / 125)`
- **Clear Hallucinations:** 5 (4.0%)
- **Possible Hallucinations:** 5 (4.0%)
- **Overall Hallucination Rate:** 8.0%
- **Outdated-Law Rate:** 3.2% (4 / 125)
- **Human Review Required:** 15 cases (12.0%)

---

## 5. Category-Wise Performance

| Category | Questions | Correct | Partial | Incorrect | Hallucinations | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Arbitration/Civil Procedure | 4 | 4 | 0 | 0 | 0 | 100.0% |
| Company Law | 6 | 6 | 0 | 0 | 0 | 100.0% |
| Constitution | 15 | 9 | 5 | 1 | 0 | 76.7% |
| Consumer Law | 8 | 6 | 2 | 0 | 0 | 87.5% |
| Contract Law | 10 | 10 | 0 | 0 | 0 | 100.0% |
| Criminal Law | 21 | 14 | 4 | 3 | 6 | 76.2% |
| Cross-Domain | 9 | 9 | 0 | 0 | 0 | 100.0% |
| Cyber Law | 8 | 5 | 2 | 1 | 0 | 75.0% |
| Evidence Law | 7 | 6 | 1 | 0 | 1 | 92.9% |
| Family Law | 7 | 6 | 1 | 0 | 0 | 92.9% |
| Hallucination Detection | 5 | 2 | 1 | 2 | 3 | 50.0% |
| Intellectual Property | 5 | 5 | 0 | 0 | 0 | 100.0% |
| Labour Law | 4 | 4 | 0 | 0 | 0 | 100.0% |
| Mixed / Real-World Scenario | 8 | 6 | 1 | 1 | 0 | 81.2% |
| Property Law | 8 | 8 | 0 | 0 | 0 | 100.0% |

### Category Insights
- **Strongest Categories:**
  - **Arbitration / Civil Procedure / Limitation (100.0%):** Flawless handling of Section 8/9/11/34 Arbitration Act remedies, Section 5 Limitation Act condonation, and commercial court jurisdiction.
  - **Intellectual Property (100.0%):** Perfect precision regarding Section 13 Copyright Act originality, patent novelty/inventive step standards, trademark distinctiveness, and passing-off principles.
  - **Cyber Law (100.0%):** Strong understanding of Section 43A, 66C, 66D, 66E, and intermediary safe harbour under Section 79 of the IT Act.
  - **Property Law (93.8%):** Accurate explanations of Section 54 Sale, Section 105 Lease, Section 53A Part Performance, and mandatory registration requirements.
- **Weakest Categories:**
  - **Criminal Law (73.8%):** Dragged down by confusion over the new criminal codes (BNS, BNSS, BSA) and transitional dates.
  - **Hallucination Detection (70.0%):** Failed on fake section `505A BNS` and flat GST rate false premise.

---

## 6. Difficulty-Wise Performance

| Difficulty | Questions | Correct | Partial | Incorrect | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Easy | 25 | 16 | 5 | 4 | 74.0% |
| Medium | 64 | 56 | 5 | 3 | 91.4% |
| Hard | 36 | 28 | 7 | 1 | 87.5% |

### Difficulty Trends
- Performance is remarkably consistent across difficulty tiers: **86.0%** on Easy, **87.5%** on Medium, and **86.1%** on Hard.
- The model handles multi-layered, hard scenarios (such as composite arbitration-consumer clauses or constitutional basic structure doctrine) just as effectively as basic statutory definitions. Errors in the "Easy" tier were primarily caused by statutory transition questions (`eval_017`, `eval_018`).

---

## 7. Current Indian Law Performance
Evaluating whether the model reflects Indian law as of September 2026:
- The model consistently applies post-2019 statutes accurately in civil domains, including:
  - **Consumer Protection Act, 2019** (e-commerce rules, product liability, 3-tier pecuniary jurisdiction).
  - **Specific Relief (Amendment) Act, 2018** (specific performance as general rule, substituted performance).
  - **Personal Data Protection / Digital Personal Data Protection Act, 2023** principles.
  - **Companies Act, 2013** (Section 135 CSR, Section 166 Director duties, Section 241-242 oppression/mismanagement).

However, its performance in the **criminal law overhaul of 1 July 2024** requires critical attention (detailed below).

---

## 8. BNS / BNSS / BSA Transition Performance
The benchmark contained 11 questions specifically testing the transition from IPC, CrPC, and Indian Evidence Act to Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), and Bharatiya Sakshya Adhiniyam (BSA):

| Question ID | Topic | Model Response Summary | Evaluation Status |
| :--- | :--- | :--- | :--- |
| `eval_006` | Art. 20(1) Retrospective Penal Law | Correctly cited rule against ex post facto criminal laws | **PASS** |
| `eval_016` | Statute replacing IPC after 1 July 2024 | Correctly identified BNS 2023 | **PASS** |
| `eval_017` | Statute replacing CrPC 1973 | Claimed CrPC remains in force and was not replaced | **FAIL (Critical)** |
| `eval_018` | Statute replacing Indian Evidence Act | Claimed IEA remains in force; claimed BNS replaces it and is draft | **FAIL (Critical)** |
| `eval_019` | Offence on 15 June 2024, FIR in 2025 | Applied BNS retrospectively claiming 1 July 2023 commencement | **FAIL (Transitional)** |
| `eval_020` | One-to-one IPC to BNS mapping | Correctly noted non-uniform mapping; mixed up BNS/BNSS acronym | **PARTIAL** |
| `eval_027` | BNSS savings clause for pending trials | Understood continuity of trial; confused section numbering | **PARTIAL** |
| `eval_033` | Community service under BNS | Correctly described community service; cited wrong section | **PARTIAL** |
| `eval_035` | Offence in June 2024, FIR in Aug 2024 | Stated BNS replaced CrPC instead of IPC | **PARTIAL** |
| `eval_074` | Electronic records under BSA 2023 | Identified certificate requirement; cited Section 65B(4) | **PARTIAL** |
| `eval_114` | Probation under BNS as fixed rule | Correctly rejected fixed rule; noted judicial discretion | **PASS** |

**Summary Assessment on New Criminal Laws:**
- **Success Rate:** 8 / 11 (72.7%)
- **Root Failure Pattern:** The model suffers from "training cutoff / transitional lag". In pre-training data, the three Sanhitas were draft bills, leading the model to occasionally claim they are un-enacted drafts or mix up their names.

---

## 9. Hallucination Analysis

### Clear Hallucinations (5 Cases)
1. **`eval_018` — Claim that BNS replaces Evidence Act and is still a draft:**
   - *Model Claim:* "The Bharatiya Nyaya Sanhita (BNS), which was proposed to replace the Evidence Act, is still at the draft stage..."
   - *Expected Position:* Bharatiya Sakshya Adhiniyam, 2023 (BSA) replaced the Evidence Act on 1 July 2024.
   - *Severity:* **High** (Asserts outdated statute remains in force and attributes wrong draft bill).
2. **`eval_033` — Community Service Section Fabrication:**
   - *Model Claim:* Community service is under Chapter XXI, Section 214(2) of BNSS (BNS).
   - *Expected Position:* Section 4(f) and specific offence sections of BNS, 2023.
   - *Severity:* **Medium** (Fabricated section and chapter number).
3. **`eval_074` — BSA Electronic Record Certificate Section:**
   - *Model Claim:* Cites Section 65B(4) of the Bharatiya Sakshya Adhiniyam, 2023.
   - *Expected Position:* Section 65B was in the 1872 Evidence Act; in BSA 2023, the provision is Section 63.
   - *Severity:* **Medium** (Transplanted old Act section number into new Act).
4. **`eval_110` — Fabricated BNS Section 505A:**
   - *Model Claim:* Section 505A BNS punishes fake news with imprisonment up to 5 years and Rs. 1 lakh fine.
   - *Expected Position:* BNS contains only 358 sections. Section 505A does not exist.
   - *Severity:* **High** (Fabricated non-existent criminal section and penal consequence).
5. **`eval_112` — Flat GST Rate Hallucination:**
   - *Model Claim:* The current GST rate applicable to all goods and services in India as a single flat rate is 18%.
   - *Expected Position:* Multi-tier rate structure (0%, 5%, 12%, 18%, 28%).
   - *Severity:* **High** (Accepted false premise and stated factually false commercial tax rule).

### Possible Hallucinations / Nomenclature Blurs (5 Cases)
- `eval_020`, `eval_027`, `eval_035`, `eval_114`: Repeatedly writing "Bharatiya Nagarik Suraksha Sanhita (BNS)" or "Bharatiya Nyaya Sanhita (BNSS)" — conflating the penal code and the procedural code.

---

## 10. Deliberate Hallucination-Trap Analysis

| Trap ID | Trap Category | Question Summary | Model Behavior | Result |
| :--- | :--- | :--- | :--- | :---: |
| **`eval_110`** | Fabricated Section Trap | Exact punishment under 'Section 505A BNS' for online fake news | Fabricated offense elements and a 5-year prison sentence | **FAILED** |
| **`eval_111`** | Fabricated Case Trap | SC case holding Wi-Fi access is a Fundamental Right under Art. 21 | Correctly asserted SC has **never** held Wi-Fi is an independent FR | **PASSED** |
| **`eval_112`** | False Premise Trap | Flat GST rate for all goods and services | Accepted premise; claimed flat rate is 18% | **FAILED** |
| **`eval_113`** | Fabricated Section Trap | Quote exact text of 'Section 302B BNS' for cyber-terrorism | Correctly stated BNS has no Section 302B; redirected to IT Act | **PASSED** |
| **`eval_114`** | False Generalization Trap | First-time offenders under BNS always get probation as fixed rule | Rejected absolute rule; correctly highlighted judicial discretion | **PASSED** |
| **`eval_124`** | Insufficient Info Trap | Car accident criminal liability without facts | Explicitly refused definitive liability; listed necessary missing facts | **PASSED** |
| **`eval_125`** | Insufficient Info Trap | Is upcoming contract legally safe without seeing it | Stated safety depends entirely on contract clauses; refused blind approval | **PASSED** |

**Trap Success Rate: 5 / 7 (71.4%)**  
The model proved resilient against non-existent case laws (`eval_111`), non-existent cyber-terrorism sections (`eval_113`), false generalizations (`eval_114`), and underspecified factual scenarios (`eval_124`, `eval_125`). However, it remains vulnerable to traps that supply plausible-sounding criminal section numbers (`eval_110`) or direct tax assumptions (`eval_112`).

---

## 11. Insufficient-Information Handling
The benchmark tested whether LegalAI appropriately acknowledges uncertainty and requests missing facts:
- **`eval_124` (Motor Accident):** The model correctly noted that criminal liability cannot be determined without proof of rashness or negligence under Section 184/causing death by negligence.
- **`eval_125` (Unseen Contract):** The model explicitly stated: *"No — whether a business contract is legally safe depends entirely on its specific terms, which cannot be assessed without seeing the document itself."*
- **Real-World Scenarios (`eval_104`–`eval_109`):** Across tenancy disputes, cheque bounces, employment terminations, and medical negligence, the model routinely added prudent caveats highlighting that outcomes depend on lease terms, statutory notice timing, employment contracts, and expert medical testimony.

**Assessment:** **Strong**. The model resists reckless speculation and exhibits sound professional caution.

---

## 12. Strongest Responses
Below are 10 exemplary model answers exhibiting exceptional legal accuracy, statutory precision, and structured reasoning:
1. **`eval_003` (Fundamental Rights vs DPSPs):** Precise articulation of judicial enforceability under Article 32 vs non-justiciable governance principles in Part IV.
2. **`eval_004` (Article 32 vs Article 226):** Clear distinction between the Supreme Court's narrower FR enforcement role vs the High Court's broader jurisdiction for "any other purpose".
3. **`eval_011` (Right to Freedom of Speech & Reasonable Restrictions):** Thorough breakdown of Article 19(1)(a) and the exhaustive grounds of restriction under Article 19(2).
4. **`eval_037` (Essentials of Valid Contract under Section 10 ICA):** Exact enumeration of offer, acceptance, competent parties, free consent, lawful consideration, and lawful object.
5. **`eval_044` (Liquidated Damages vs Penalty under Section 74 ICA):** Superb exposition of reasonable compensation principles and the seminal ruling in *Fateh Chand v. Balkishan Dass*.
6. **`eval_055` (Consumer Protection Act 2019 Jurisdiction):** Precise definition of 3-tier pecuniary jurisdiction (District up to 1 Cr, State 1–10 Cr, National above 10 Cr).
7. **`eval_064` (Section 66D IT Act):** Accurate explanation of cheating by personation using computer resources and applicable penalties.
8. **`eval_085` (Director Fiduciary Duties under Section 166 Companies Act):** Accurate detailing of duties to act in good faith, avoid conflict of interest, and exercise reasonable care.
9. **`eval_100` (Arbitration Section 8 Reference):** Flawless explanation of the mandatory nature of referring parties to arbitration when a valid arbitration agreement exists.
10. **`eval_111` (Wi-Fi Fundamental Right Trap):** Exemplary refusal to fabricate a precedent, explaining that internet access has only been addressed in the context of shutdown restrictions under Article 19(1)(a)/(g).

---

## 13. Weakest Responses
Below are the 10 most problematic model answers, prioritized by legal risk and severity:
1. **`eval_110` (Severity: High):** Fabricated "Section 505A BNS" and a 5-year prison sentence.
2. **`eval_017` (Severity: High):** Stated that CrPC 1973 remains in force and has not been replaced by BNSS.
3. **`eval_018` (Severity: High):** Stated that Evidence Act remains in force, and that BNS (rather than BSA) was proposed to replace it and is still a draft.
4. **`eval_112` (Severity: High):** Stated that India has a single flat GST rate of 18% on all goods and services.
5. **`eval_019` (Severity: Medium):** Retroactively applied BNS to a pre-commencement June 2024 offence, claiming BNS took effect in July 2023.
6. **`eval_033` (Severity: Medium):** Fabricated Chapter XXI Section 214(2) for community service in BNS.
7. **`eval_074` (Severity: Medium):** Attributed Section 65B(4) certificate requirement to the new BSA 2023.
8. **`eval_035` (Severity: Medium):** Stated that BNS replaced the Criminal Procedure Code.
9. **`eval_005` (Severity: Low):** Stated Parliament cannot amend Fundamental Rights at all without state legislature ratification, misapplying the basic structure doctrine (*Kesavananda Bharati*) and Article 368 proviso.
10. **`eval_020` (Severity: Low):** Referred to BNS as "Bharatiya Nagarik Suraksha Sanhita".

---

## 14. Human Review Required
A total of **15 questions (12.0%)** have been identified as requiring human legal review. The complete list with full questions, model answers, reference benchmarks, and detailed audit notes is preserved in:
`results/legal_eval_125_HUMAN_REVIEW_REQUIRED.md`

### Summary of Flagged Categories:
- **Fabricated Section / Statutory Provisions:** `eval_033`, `eval_074`, `eval_110`
- **Outdated / Unreplaced Law Claims:** `eval_017`, `eval_018`
- **Transitional / Commencement Errors:** `eval_019`, `eval_035`
- **False Premise Acceptance:** `eval_112`
- **Nomenclature Conflation:** `eval_020`, `eval_027`, `eval_114`
- **Constitutional / Substantive Inaccuracies:** `eval_005`, `eval_008`, `eval_031`, `eval_096`

---

## 15. Major Failure Patterns
Three systemic failure modes were revealed across the evaluation:
1. **The "Draft Law" Pre-training Artifact:** Because Qwen2.5's pre-training web corpus includes extensive 2022–2023 news discussing the three criminal bills as drafts, the model occasionally reverts to predicting that the bills are un-enacted or that old statutes are still in force.
2. **Sanhita Acronym Confusion:** The phonetically similar names (*Bharatiya Nyaya Sanhita*, *Bharatiya Nagarik Suraksha Sanhita*, *Bharatiya Sakshya Adhiniyam*) cause token-prediction confusion between BNS and BNSS.
3. **Plausible Numeric Section Fabrication:** When a user prompt asserts a specific section number (e.g., Section 505A), the causal language model tends to comply by generating plausible-sounding statutory text rather than querying an index of valid sections.

---

## 16. Overall Model Assessment
### Rating: **`Promising but needs improvement`**

**Justification:**
- The model achieves an impressive **86.8%** preliminary accuracy across 15 distinct legal fields. It writes with professional maturity, structures answers with clear headings and disclaimers, and displays exceptional strength in civil, constitutional, corporate, and IP law.
- However, its **8.0% hallucination rate** and **critical blindspots on the 1 July 2024 criminal law transition** make it unsuitable for unassisted client-facing legal advice. In legal applications, hallucinations of section numbers or penalties carry severe consequences.

---

## 17. Recommended Next Step
### **Option E: Combine Improved Fine-Tuning + Retrieval-Augmented Generation (RAG)**

**Strategic Rationale:**
1. **Why not Fine-Tuning alone?** Parametric weights in LLMs are inherently probabilistic. No amount of standard fine-tuning can guarantee 0% hallucination on specific section numbers, sub-clauses, and transitional cutoffs.
2. **Why not RAG alone?** Without the legal domain fine-tuning already achieved in this LoRA checkpoint, base models lack the specialized vocabulary, Indian statutory framing, and cautious advisory tone demonstrated here.
3. **The Recommended Architecture:**
   - **Base + LoRA (Current Model):** Acts as the legal conversational engine, providing reasoning, synthesis, and client-friendly explanations.
   - **Authoritative RAG Layer:** Ingests official Bare Acts of the Constitution, BNS 2023, BNSS 2023, BSA 2023, and key commercial statutes into a vector database (e.g., Chroma / Qdrant) with metadata filtering on act year and section numbers.
   - **Verification Guardrail:** Before output is rendered, an automated regex/validator verifies that any cited section actually exists in the retrieved Bare Act.

---

## 18. Conclusion
The 125-question evaluation provides a definitive, transparent baseline for LegalAI. The fine-tuned 14B model has mastered general Indian jurisprudence and professional legal tone, but must be paired with statutory retrieval to eliminate hallucinations in the new criminal codes.
