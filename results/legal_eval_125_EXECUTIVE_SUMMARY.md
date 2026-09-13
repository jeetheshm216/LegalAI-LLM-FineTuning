# LegalAI Evaluation — Executive Summary

**Date:** 13 September 2026  
**Audience:** Project Mentor / Faculty Review Committee  
**Evaluation Scope:** 125-Question Held-Out Benchmark (`data/legal_eval_125.jsonl`)

---

### Core Performance Metrics

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **Model Evaluated** | `Qwen/Qwen2.5-14B-Instruct` + LoRA | 1-epoch LoRA checkpoint (`outputs/qwen14b-first-run-final-dataset`) |
| **Benchmark Size** | 125 held-out questions | 15 Indian law categories; Easy, Medium, and Hard tiers |
| **Evaluation Completeness** | 125 / 125 (100%) | Zero generation failures; zero dropped questions |
| **Overall Preliminary Accuracy** | **86.8%** | 100 Substantially Correct, 17 Partially Correct, 8 Incorrect |
| **Hallucination Rate** | **8.0%** (Clear: 4.0%, Possible: 4.0%) | 5 clear fabricated provisions/claims; 5 statutory naming mixups |
| **Outdated-Law Rate** | **3.2%** (4 / 125 questions) | Stating CrPC/Evidence Act remain in force or applying BNS retrospectively |
| **Current Criminal Law Accuracy** | **72.7%** (8 / 11 transition questions) | Mixed performance distinguishing BNS/BNSS/BSA from IPC/CrPC/IEA |
| **Deliberate Trap Handling** | **5 / 7 passed** (71.4%) | Successfully rejected non-existent cases/sections; failed flat GST rate trap & BNS Sec 505A trap |
| **Cases Requiring Human Review** | **15 / 125** (12.0%) | Documented in `legal_eval_125_HUMAN_REVIEW_REQUIRED.md` |

---

### Major Strengths
1. **Strong Foundational Constitutional & Civil Law Reasoning:** Demonstrates deep and accurate knowledge of Fundamental Rights (Articles 14, 19, 21, 32), contract principles (Section 10, 23, 73 ICA), consumer protection procedures, and property transfer formalities.
2. **Effective Uncertainty & Fact-Deficiency Recognition:** Consistently identifies when factual inputs are insufficient (e.g., motor accident liability, contract safety assessments) and appropriately requests missing facts rather than guessing.
3. **Resilience on Fabricated Case Traps:** Correctly asserted that the Supreme Court has never declared a standalone 'right to Wi-Fi access' under Article 21, avoiding hallucination on non-existent precedents.
4. **Structured and Professional Advisory Tone:** Provides cautious, well-structured explanations accompanied by practical guidance and mandatory legal disclaimers.

---

### Major Weaknesses
1. **New Criminal Law (BNS/BNSS/BSA) Nomenclature Conflation:** Often confuses the acronyms and names between BNS (Bharatiya Nyaya Sanhita — substantive penal law) and BNSS (Bharatiya Nagarik Suraksha Sanhita — criminal procedural law), such as referring to "Bharatiya Nagarik Suraksha Sanhita (BNS)".
2. **Transition Date & Savings Provision Blindspots:** Stated in `eval_017` that CrPC 1973 has not been replaced, in `eval_018` that BSA is still at draft stage, and in `eval_019` misapplied BNS to an offence committed on 15 June 2024 (prior to the 1 July 2024 commencement).
3. **Susceptibility to Complex Statutory Section Traps:** In `eval_110`, fabricated a non-existent "Section 505A of BNS" and an associated 5-year prison sentence when prompted with a fake section name.
4. **False-Premise Susceptibility:** In `eval_112`, accepted the false premise that India has a single flat GST rate and asserted it was 18%.

---

### Final Assessment
**`Promising but needs improvement`**

The model exhibits strong domain competence in general Indian substantive and procedural law, but its hallucination rate of 8.0% and confusion regarding the 1 July 2024 criminal law transitions (BNS/BNSS/BSA) prevent it from being safe as an autonomous legal assistant.

---

### Recommended Next Step
**Option E: Combine Improved Fine-Tuning + Retrieval-Augmented Generation (RAG)**

*Fine-tuning alone cannot guarantee exact statutory section numbers or date-boundary precision for rapidly evolving statutory codes.*  
The recommended path forward is:
1. Retain the current fine-tuned model for conversational fluency, legal reasoning, and tone.
2. Integrate an authoritative RAG layer (Bare Acts of BNS, BNSS, BSA, Constitution of India, and Supreme Court judgments) to ground statutory references, sections, and penalties in verified legal text before generation.
3. Add a post-processing validator specifically checking statutory section existence and effective commencement dates.
