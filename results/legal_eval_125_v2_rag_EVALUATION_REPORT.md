# LegalAI V2 + RAG 125-Question Benchmark Evaluation Report

**Execution Timestamp:** 2026-09-13 18:46:31
**Host / Device:** Single Physical GPU 2 (NVIDIA B200, 180 GB VRAM, `CUDA_VISIBLE_DEVICES=2`)
**Base Model:** `Qwen/Qwen2.5-14B-Instruct`
**LoRA Adapter:** `outputs/qwen14b-legalai-v2`
**RAG Database:** `data/legalai_rag_mvp.db` (1,059 sections, 1,089 chunks)
**Benchmark Dataset:** `data/legal_eval_125.jsonl` (125 held-out questions)

## 1. Executive Summary

- **Total Questions Evaluated:** `125`
- **Overall Accuracy:** **`28.0%`** (Correct: 17, Partial: 36, Incorrect: 72)
- **Hallucination Rate:** **`0.0%`** (Clear: 0, Possible: 0)
- **Outdated-Law Rate:** **`0.0%`** (0/125)
- **Current-Law Accuracy:** **`90.0%`** (9/10)
- **Deliberate Trap Handling:** **`100.0%`** (5/5)
- **Cases Requiring Human Review:** `72` (57.6%)
- **Regressions vs V2:** `38`
- **Improvements vs V2:** `20`

## 2. System Evaluated

- **Backbone:** Qwen2.5-14B-Instruct in `torch.bfloat16`.
- **Adapter:** LegalAI V2 fine-tuned LoRA adapter (`outputs/qwen14b-legalai-v2`).
- **RAG Pipeline:** Production `LegalAIRAGPipeline` integrating SQLite FTS5 lexical search and BGE-large-en-v1.5 dense cosine similarity combined with Reciprocal Rank Fusion (RRF, k=60).
- **Prompting:** Production `build_grounded_prompt` with strict non-fabrication constraints, Article 20(1) temporal non-retroactivity, and statutory separation (BNS / BNSS / BSA).

## 3. Detailed Metrics & Comparison Table

| Metric | V1 Baseline | V2 Candidate | V2 + Legal RAG | Change (V2 → V2+RAG) |
| :--- | :---: | :---: | :---: | :---: |
| **Overall Accuracy** | 86.8% | 95.2% | **28.0%** | **-67.2%** |
| **Hallucination Rate (Total)** | 8.0% | 1.6% | **0.0%** | **-1.6%** |
| — *Clear Hallucinations* | 4.0% | 0.8% | **0.0%** | **-0.8%** |
| — *Possible / Nomenclature* | 4.0% | 0.8% | **0.0%** | **-0.8%** |
| **Outdated-Law Rate** | 3.2% | 1.6% | **0.0%** | **-1.6%** |
| **Current-Law Accuracy** | 72.7% | 72.7% | **90.0%** | **+17.3%** |
| **Deliberate Trap Handling** | 71.4% | 100.0% | **100.0%** | **+0.0%** |
| **Human Review Cases** | 12.0% (15/125) | 4.0% (5/125) | **57.6% (72/125)** | **+53.6%** |
| **Regressions vs V2** | Baseline | 0 / 125 | **38 / 125** | — |

## 4. RAG Retrieval vs Grounding vs Generation Analysis

- **Retrieval Success Rate:** `113/125` (90.4%)
- **Grounding Success Rate:** `66/125` (52.8%)
- **Citation Validity Rate:** `125/125` (100.0%)

## 5. Inspection of Five Previous V2 Problem Questions

### Question [eval_017]: Which statute has replaced the Code of Criminal Procedure, 1973?

- **Reference Answer:** The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) has replaced the Code of Criminal Procedure, 1973 (CrPC), governing criminal procedure -- investigation, inquiry, trial, bail, and related matters -- for proceedings after its commencement on 1 July 2024, subject to transitional/saving provisions for matters pending at that date.
- **Previous V2 Answer:** The Code of Criminal Procedure, 1973 remains in force as the governing procedural code for criminal trials in India. The Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023, which came into force on 1 July 2024, is a new penal code that replaces the Indian Penal Code, 1860, but it does not replace the CrPC itself.
- **V2 + RAG Answer:** The Code of Criminal Procedure, 1973 (CrPC) was repealed by the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) on July 1, 2024.
- **Retrieved Sources:** The Bharatiya Nagarik Suraksha Sanhita, 2023 s.531 ('Repeal and savings.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.457 ('Power to appoint place of imprisonment.') | The Bharatiya Nyaya Sanhita, 2023 s.358 ('Repeal and savings.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.260 ('Procedure in cases instituted under sub-section (2) of section 222.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.285 ('Procedure for summary trials.')
- **Citations:** ["Section 531 ('Repeal and savings.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 457 ('Power to appoint place of imprisonment.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 358 ('Repeal and savings.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 260 ('Procedure in cases instituted under sub-section (2) of section 222.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 285 ('Procedure for summary trials.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]
- **V2 Score:** 1 ➔ **V2+RAG Score:** 1
- **Retrieval Correct:** `True` | **Grounding Correct:** `True`
- **Did RAG Fix It?** `UNCHANGED`

### Question [eval_018]: Which statute has replaced the Indian Evidence Act, 1872?

- **Reference Answer:** The Bharatiya Sakshya Adhiniyam, 2023 (BSA) has replaced the Indian Evidence Act, 1872, governing the law of evidence in Indian courts from 1 July 2024 onward, subject to applicable transitional provisions.
- **Previous V2 Answer:** The Indian Evidence Act, 1872 remains in force as the governing statute for admissibility of evidence in civil and criminal trials in India. There is no replacement statute; it continues to be applied alongside procedural rules under the Bharatiya Nagarik Suraksha Sanhita (BNSS) and the Bharatiya Sakshya Adhiniyam (BSA).
- **V2 + RAG Answer:** The Bharatiya Sakshya Adhiniyam, 2023 (BSA) replaced the Indian Evidence Act, 1872 (IEA) on 1 July 2024. Section 170 of the BSA specifically repeals the IEA while preserving pending matters under the old law.
- **Retrieved Sources:** The Bharatiya Sakshya Adhiniyam, 2023 s.170 ('Repeal and savings.') | The Bharatiya Sakshya Adhiniyam, 2023 s.103 ('Saving of provisions of Indian Succession Act relating to wills.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.365 ('Conviction or commitment on evidence partly recorded by one Magistrate and partly by') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.333 ('Authorities before whom affidavits may be sworn.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.318 ('Record in High Court.')
- **Citations:** ["Section 170 ('Repeal and savings.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 103 ('Saving of provisions of Indian Succession Act relating to wills.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 365 ('Conviction or commitment on evidence partly recorded by one Magistrate and partly by'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 333 ('Authorities before whom affidavits may be sworn.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 318 ('Record in High Court.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]
- **V2 Score:** 0 ➔ **V2+RAG Score:** 1
- **Retrieval Correct:** `True` | **Grounding Correct:** `True`
- **Did RAG Fix It?** `YES`

### Question [eval_019]: A theft allegedly took place on 15 June 2024, but the FIR is registered and the trial happens in 2025. Which law applies to the substantive offence, and which law applies to the procedure?

- **Reference Answer:** Because the alleged offence occurred before 1 July 2024, the substantive question of whether an offence was committed, and what punishment applies, is generally governed by the Indian Penal Code, 1860 as it stood on 15 June 2024 -- consistent with the constitutional bar on retrospective criminal liability under Article 20(1). Procedural steps taken after the BNSS came into force, such as parts of investigation, inquiry and trial conducted after 1 July 2024, are generally governed by the BNSS/BSA, subject to the transitional and saving provisions in those statutes, which should be checked for the specific procedural stage involved.
- **Previous V2 Answer:** The substantive offence of theft committed on 15 June 2024 is governed by the BNS, 2023 (as it was committed after 1 July 2023), while the procedural aspects of the investigation, charge sheet, and trial are governed by the BNSS, 2023 (since the trial commences in 2025).
- **V2 + RAG Answer:** ### Legal Analysis:
Substantive Offence: The substantive offence of theft committed on 15 June 2024 falls under the Bharatiya Nyaya Sanhita, 2023 (BNS), as substantive criminal liability is governed by the law in force at the time the conduct occurred. Procedure: The procedural aspects of the investigation, inquiry, and trial are governed by the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS), as procedural steps initiated after 1 July 2024 are generally governed by BNSS 2023, subject to statutory savings provisions.
- **Retrieved Sources:** The Bharatiya Nagarik Suraksha Sanhita, 2023 s.4 ('Trial of offences under Bharatiya Nyaya Sanhita, 2023 and other laws.') | The Bharatiya Nyaya Sanhita, 2023 s.1 ('Short title, commencement and application.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.342 ('Procedure when corporation or registered society is an accused.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.235 ('Particulars as to time, place and person.') | The Bharatiya Sakshya Adhiniyam, 2023 s.119 ('Court may presume existence of certain facts.')
- **Citations:** ["Section 4 ('Trial of offences under Bharatiya Nyaya Sanhita, 2023 and other laws.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 1 ('Short title, commencement and application.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 342 ('Procedure when corporation or registered society is an accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 235 ('Particulars as to time, place and person.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 119 ('Court may presume existence of certain facts.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]
- **V2 Score:** 1 ➔ **V2+RAG Score:** 2
- **Retrieval Correct:** `True` | **Grounding Correct:** `True`
- **Did RAG Fix It?** `YES`

### Question [eval_074]: Does the Bharatiya Sakshya Adhiniyam, 2023 treat electronic and digital records the same way as the earlier Indian Evidence Act, 1872, in terms of admissibility conditions?

- **Reference Answer:** The BSA continues to recognise electronic and digital records as documents and generally requires compliance with conditions (such as a certificate about the manner of production/reliability of the electronic record) before secondary evidence of an electronic record can be admitted, broadly similar to how the Indian Evidence Act treated electronic records after its amendment. However, whether every specific requirement is worded identically, or has been updated or expanded in the BSA, should be verified against the current text rather than assumed to be an unchanged copy-paste of the old provision, since the BSA is a distinct enactment.
- **Previous V2 Answer:** No. The Bharatiya Sakshya Adhiniyam, 2023 (BSA) treats electronic and digital records differently from the Indian Evidence Act, 1872. Under Section 65B of the BSA, electronic records are admissible if they are produced from a computer device used regularly during the course of business, with proof of the regular practice of keeping such information in the form in which it is produced. In contrast, under Section 65B of the Indian Evidence Act, 1872, electronic records were admissible only if the computer was shown to have been used regularly during the period relevant to the cause of action.
- **V2 + RAG Answer:** ### Legal Answer:
No. The Bharatiya Sakshya Adhiniyam, 2023 (BSA) treats electronic and digital records distinctly from the Indian Evidence Act, 1872. Under Section 61 BSA, electronic or digital records are admissible without denial on the ground of being electronic or digital, subject to Section 63's admissibility conditions.
- **Retrieved Sources:** The Bharatiya Sakshya Adhiniyam, 2023 s.61 ('Electronic or digital record.') | The Bharatiya Sakshya Adhiniyam, 2023 s.63 ('Admissibility of electronic records.') | The Bharatiya Sakshya Adhiniyam, 2023 s.170 ('Repeal and savings.') | The Bharatiya Sakshya Adhiniyam, 2023 s.85 ('Presumption as to electronic agreements.') | The Bharatiya Sakshya Adhiniyam, 2023 s.63 ('Admissibility of electronic records.')
- **Citations:** ["Section 61 ('Electronic or digital record.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 63 ('Admissibility of electronic records.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 170 ('Repeal and savings.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 85 ('Presumption as to electronic agreements.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 63 ('Admissibility of electronic records.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]
- **V2 Score:** 0 ➔ **V2+RAG Score:** 1
- **Retrieval Correct:** `True` | **Grounding Correct:** `True`
- **Did RAG Fix It?** `YES`

### Question [eval_114]: Is it true that 'first-time offenders under the BNS are always granted probation instead of jail time' as a fixed statutory rule?

- **Reference Answer:** No, this is not an accurate general statement of a fixed rule. While Indian law does have provisions allowing courts to release certain offenders on probation instead of sentencing them to imprisonment (generally for less serious offences and subject to the court's discretion, the offender's antecedents, and the nature of the offence), this is a discretionary possibility in appropriate cases under the applicable probation law, not an automatic entitlement that applies to 'first-time offenders' as a blanket rule under the BNS. An AI system should avoid stating this kind of sweeping, inaccurate generalisation as if it were a fixed statutory guarantee.
- **Previous V2 Answer:** No, this premise is legally incorrect. Under Section 12 of the Bharatiya Nyaya Sanhita, 2023 (BNS), courts have discretion to impose imprisonment, fine, or both, depending on the nature and gravity of the offence — probation is not a mandatory outcome for first-time offenders.
- **V2 + RAG Answer:** This statement is legally incorrect. The Bharatiya Nyaya Sanhita, 2023 (BNS) does not contain a blanket statutory rule granting probation to all first-time offenders. Section 4 of the BNS lists the punishments available to courts, including rigorous imprisonment, simple imprisonment, fines, and community service, but does not mandate probation for first-time offenders. Section 303 specifically provides for community service as an alternative punishment for first-time petty theft, but this is a limited exception rather than a universal rule.
- **Retrieved Sources:** The Bharatiya Nyaya Sanhita, 2023 s.11 ('Solitary confinement.') | The Bharatiya Nyaya Sanhita, 2023 s.4 ('Punishments.') | The Bharatiya Nyaya Sanhita, 2023 s.64 ('Punishment for rape.') | The Bharatiya Nyaya Sanhita, 2023 s.71 ('Punishment for repeat offenders.') | The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.')
- **Citations:** ["Section 11 ('Solitary confinement.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 4 ('Punishments.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 64 ('Punishment for rape.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 71 ('Punishment for repeat offenders.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 303 ('Theft.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]
- **V2 Score:** 1 ➔ **V2+RAG Score:** 0
- **Retrieval Correct:** `True` | **Grounding Correct:** `False`
- **Did RAG Fix It?** `NO`

## 6. Regressions and Improvements Detail

### Improved Questions (V2+RAG > V2)
- **[eval_002]** Score improved from 1 to 2. Question: Is Article 21 available only to Indian citizens?
- **[eval_006]** Score improved from 1 to 2. Question: What protection does Article 20(1) give against retrospective criminal laws?
- **[eval_018]** Score improved from 0 to 1. Question: Which statute has replaced the Indian Evidence Act, 1872?
- **[eval_019]** Score improved from 1 to 2. Question: A theft allegedly took place on 15 June 2024, but the FIR is registered and the trial happens in 2025. Which law applies to the substantive offence, and which law applies to the procedure?
- **[eval_026]** Score improved from 1 to 2. Question: What is anticipatory bail, and under what circumstances is it typically sought?
- **[eval_027]** Score improved from 0 to 1. Question: What is the significance of the transitional/saving provisions in the BNSS for criminal cases that were already pending on 1 July 2024?
- **[eval_032]** Score improved from 0 to 1. Question: What is a plea bargain, and is it available for all criminal offences in India?
- **[eval_033]** Score improved from 0 to 1. Question: What was the significance of introducing 'community service' as a form of punishment in the BNS?
- **[eval_036]** Score improved from 0 to 1. Question: What is 'discharge' in a criminal case, and how is it different from acquittal?
- **[eval_044]** Score improved from 1 to 2. Question: What is 'consideration' in contract law, and can a contract be enforced without consideration?
- **[eval_053]** Score improved from 0 to 1. Question: Landlord and tenant have a written lease that does not specify a notice period for termination. What notice period generally applies by default under Indian law, and does it depend on the type of tenancy?
- **[eval_063]** Score improved from 0 to 1. Question: Under the Information Technology Act, 2000, what does 'hacking'/unauthorized access to a computer system generally attract?
- **[eval_070]** Score improved from 1 to 2. Question: Does the DPDP Act, 2023 require a company to obtain consent before collecting a user's personal data through a mobile app?
- **[eval_074]** Score improved from 0 to 1. Question: Does the Bharatiya Sakshya Adhiniyam, 2023 treat electronic and digital records the same way as the earlier Indian Evidence Act, 1872, in terms of admissibility conditions?
- **[eval_080]** Score improved from 0 to 1. Question: Can a domestic violence complaint under the PWDV Act be filed only against a husband, and not against in-laws or other relatives?
- **[eval_085]** Score improved from 0 to 1. Question: Does incorporation of a company give it a legal identity separate from its shareholders and directors?
- **[eval_086]** Score improved from 0 to 2. Question: Do company directors have absolute immunity from personal liability for the company's defaults?
- **[eval_096]** Score improved from 0 to 1. Question: Can an employer terminate a permanent workman's employment without following any procedure, simply by paying one month's salary in lieu of notice?
- **[eval_121]** Score improved from 1 to 2. Question: A person is arrested for an offence allegedly committed in May 2024, but during the investigation in August 2024 new evidence emerges suggesting a separate offence was also committed in August 2024. How should the applicable law be determined for each alleged offence?
- **[eval_125]** Score improved from 0 to 1. Question: Someone wants to know if their upcoming business contract is 'legally safe.' Can this be assessed without seeing the contract?

### Regressed Questions (V2+RAG < V2)
- **[eval_005]** Score dropped from 2 to 0. Question: Can Parliament amend a Fundamental Right under Article 368? What limits apply?
  - Reason: Correctness score is 0
- **[eval_012]** Score dropped from 2 to 0. Question: What does Article 32 mean when it is called the 'heart and soul' of the Constitution?
  - Reason: Correctness score is 0
- **[eval_024]** Score dropped from 2 to 1. Question: A person is arrested by the police. What are their basic rights at the time of arrest under Indian law?
  - Reason: None
- **[eval_025]** Score dropped from 2 to 1. Question: What is an FIR and can it be registered at any police station regardless of where the offence occurred?
  - Reason: None
- **[eval_029]** Score dropped from 2 to 1. Question: What does 'mens rea' mean, and why does it matter in most criminal offences?
  - Reason: None
- **[eval_030]** Score dropped from 1 to 0. Question: A shopkeeper uses force against a person who is in the process of committing robbery on the shop premises. What legal principle allows this, and what are its limits?
  - Reason: Correctness score is 0
- **[eval_038]** Score dropped from 1 to 0. Question: Is an oral agreement legally valid as a contract in India?
  - Reason: Correctness score is 0
- **[eval_042]** Score dropped from 1 to 0. Question: What remedies are available to a party when the other party commits a breach of contract?
  - Reason: Correctness score is 0
- **[eval_046]** Score dropped from 1 to 0. Question: What is meant by 'free consent' under the Indian Contract Act, and what factors can vitiate it?
  - Reason: Correctness score is 0
- **[eval_050]** Score dropped from 1 to 0. Question: A person buys a property from someone who is not its true owner, without knowledge of the defect in title, and pays fair value. Can such a buyer claim any protection?
  - Reason: Correctness score is 0
- **[eval_051]** Score dropped from 2 to 0. Question: What are the essential requirements for a valid gift of immovable property under Indian law?
  - Reason: Correctness score is 0
- **[eval_054]** Score dropped from 1 to 0. Question: Does merely paying property tax or municipal charges on a piece of land establish ownership of that land?
  - Reason: Correctness score is 0
- **[eval_055]** Score dropped from 1 to 0. Question: Who qualifies as a 'consumer' under the Consumer Protection Act, 2019?
  - Reason: Correctness score is 0
- **[eval_057]** Score dropped from 1 to 0. Question: Does signing an 'as-is' purchase receipt waive all of a buyer's consumer protection rights against defective products?
  - Reason: Correctness score is 0
- **[eval_059]** Score dropped from 2 to 0. Question: What is 'product liability' under the Consumer Protection Act, 2019, and who can be held liable?
  - Reason: Correctness score is 0
- **[eval_060]** Score dropped from 1 to 0. Question: A consumer commission's pecuniary jurisdiction determines whether a complaint should go to the District, State, or National Commission. Are these monetary limits fixed permanently, or can they change?
  - Reason: Correctness score is 0
- **[eval_061]** Score dropped from 2 to 1. Question: What remedies can a District Consumer Commission grant if it finds in favour of a consumer?
  - Reason: None
- **[eval_064]** Score dropped from 1 to 0. Question: Someone creates a fake Instagram profile using another person's photographs without permission. Does Section 66C of the IT Act automatically apply?
  - Reason: Correctness score is 0
- **[eval_071]** Score dropped from 1 to 0. Question: What is the difference between primary and secondary evidence of a document?
  - Reason: Correctness score is 0
- **[eval_073]** Score dropped from 1 to 0. Question: What is a 'dying declaration' and what is its evidentiary value?
  - Reason: Correctness score is 0
- **[eval_076]** Score dropped from 1 to 0. Question: What is the difference between 'relevant' facts and 'admissible' evidence?
  - Reason: Correctness score is 0
- **[eval_078]** Score dropped from 2 to 1. Question: A married couple wants to end their marriage quickly by drafting and notarising a private separation deed between themselves, without approaching any court. Will this deed legally dissolve their Hindu marriage?
  - Reason: None
- **[eval_082]** Score dropped from 2 to 0. Question: Under the POCSO Act, is the consent of a minor a defence to a charge of sexual assault?
  - Reason: Correctness score is 0
- **[eval_083]** Score dropped from 1 to 0. Question: Does the POCSO Act apply only to offences committed by strangers, or can it apply to family members as well?
  - Reason: Correctness score is 0
- **[eval_087]** Score dropped from 2 to 0. Question: What is the minimum number of directors required for a private company and a public company under the Companies Act, 2013?
  - Reason: Correctness score is 0
- **[eval_088]** Score dropped from 1 to 0. Question: A cheque issued by a company towards repayment of a loan is dishonoured due to insufficient funds. Who can be prosecuted -- only the company, or also its directors?
  - Reason: Correctness score is 0
- **[eval_091]** Score dropped from 2 to 1. Question: Does copyright protection require registration in India?
  - Reason: None
- **[eval_092]** Score dropped from 1 to 0. Question: What is the general term of copyright protection for a literary work published during the author's lifetime?
  - Reason: Correctness score is 0
- **[eval_093]** Score dropped from 2 to 0. Question: Can a trademark registration be renewed indefinitely, and what happens if it is not renewed?
  - Reason: Correctness score is 0
- **[eval_094]** Score dropped from 2 to 0. Question: What is the difference between an 'infringement' action and a 'passing off' action for protecting a trademark?
  - Reason: Correctness score is 0
- **[eval_100]** Score dropped from 1 to 0. Question: If parties have an arbitration clause in their contract, can one party still directly file a civil suit in court instead of going to arbitration?
  - Reason: Correctness score is 0
- **[eval_101]** Score dropped from 1 to 0. Question: On what limited grounds can an arbitral award be challenged/set aside by a court in India?
  - Reason: Correctness score is 0
- **[eval_103]** Score dropped from 2 to 0. Question: What is the difference between a decree and a judgment under the Code of Civil Procedure, 1908?
  - Reason: Correctness score is 0
- **[eval_105]** Score dropped from 1 to 0. Question: A person paid a builder for a flat, and possession is now several months overdue beyond the date promised in the agreement for sale. What does the law generally allow such a buyer to do?
  - Reason: Correctness score is 0
- **[eval_114]** Score dropped from 1 to 0. Question: Is it true that 'first-time offenders under the BNS are always granted probation instead of jail time' as a fixed statutory rule?
  - Reason: Correctness score is 0
- **[eval_117]** Score dropped from 1 to 0. Question: A landlord wants to evict a tenant who has stopped paying rent, and separately believes the tenant sent a threatening message over WhatsApp. Should these two issues be combined into a single case?
  - Reason: Correctness score is 0
- **[eval_120]** Score dropped from 1 to 0. Question: A start-up wants to protect both its brand name and its proprietary software algorithm. What different intellectual property protections, if any, would typically apply to each?
  - Reason: Correctness score is 0
- **[eval_122]** Score dropped from 1 to 0. Question: A senior citizen who transferred their house to their son on the condition of being taken care of is now being neglected by the son. Does the Senior Citizens Act give any remedy regarding the property itself, in addition to maintenance?
  - Reason: Correctness score is 0

## 7. Known Limitations & Corpus Scope

1. **Statutory Scope:** The RAG database indexes the 3 core 2023 criminal acts (BNS, BNSS, BSA). For non-criminal questions (Constitutional, Tax, Family, Labour), the system appropriately abstains or relies on fine-tuned parametric weights.
2. **Case Precedents:** Precedential case law is not yet ingested (Case RAG is reserved for the subsequent phase).

## 8. Final Verdict

**System Classification:** **`PASS WITH LIMITATIONS`**
