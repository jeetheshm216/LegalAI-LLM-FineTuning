# LegalAI V2 + RAG Fixed Architecture 125-Question Benchmark Evaluation Report

**Execution Timestamp:** 2026-09-13 20:41:03
**Host / Device:** Single Physical GPU 2 (NVIDIA B200, 180 GB VRAM, `CUDA_VISIBLE_DEVICES=2`)
**Base Model:** `Qwen/Qwen2.5-14B-Instruct`
**LoRA Adapter:** `outputs/qwen14b-legalai-v2`
**RAG Database:** `data/legalai_rag_mvp.db` (1,059 sections, 1,089 chunks)
**Benchmark Dataset:** `data/legal_eval_125.jsonl` (125 held-out questions)

## 1. Executive Summary

- **Total Questions Evaluated:** `125`
- **Effective System Accuracy (Safe Grounded & Abstentions):** **`50.0%`**
- **In-Corpus Statutory Accuracy (Criminal & Evidence Law):** **`23.2%`**
- **Out-of-Corpus Handling Safety Rate:** **`61.9%`**
- **Justified Abstention Rate:** **`35.2%`** (44/125)
- **Wrong-Domain Retrieval Rate:** **`12.0%`** (15/125)
- **Hallucination Rate:** **`0.0%`** (0/125)
- **Outdated-Law Rate:** **`0.0%`** (0/125)
- **Temporal Error Rate:** **`0.0%`** (0/125)
- **Deliberate Trap Handling:** **`100.0%`** (5/5)
- **Cases Requiring Human Review:** `54` (43.2%)

## 2. Nine-Class Legal Performance Breakdown

| Classification Category | Count | Percentage | Legal Assessment |
| :--- | :---: | :---: | :--- |
| **CORRECT** | 10 | 8.0% | Grounded substantive match with complete statutory precision |
| **PARTIALLY_CORRECT** | 17 | 13.6% | Substantively sound with minor omissions |
| **JUSTIFIED_ABSTENTION** | 44 | 35.2% | High-fidelity refusal due to statute outside 3-Act corpus |
| **INCORRECT** | 38 | 30.4% | Fails substantive legal test without hallucinating |
| **HALLUCINATION** | 0 | 0.0% | Fabricated provisions, fake cases, or invented citations |
| **WRONG_DOMAIN_RETRIEVAL** | 15 | 12.0% | Inappropriately cited BNS/BNSS for non-criminal queries |
| **OUTDATED_LAW** | 0 | 0.0% | Relied on repealed law without noting 2024 transition |
| **TEMPORAL_ERROR** | 0 | 0.0% | Applied BNS retroactively to pre-July 1, 2024 acts |
| **CITATION_ERROR** | 1 | 0.8% | Cited provision unsupported by retrieved context |

## 3. Inspection of Five Target Problem Questions

### Question [eval_017]: Which statute has replaced the Code of Criminal Procedure, 1973?

- **Reference Answer:** The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) has replaced the Code of Criminal Procedure, 1973 (CrPC), governing criminal procedure -- investigation, inquiry, trial, bail, and related matters -- for proceedings after its commencement on 1 July 2024, subject to transitional/saving provisions for matters pending at that date.
- **Fixed Pipeline Answer:** The Code of Criminal Procedure, 1973 (CrPC) was repealed by the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) on 1 July 2024.
- **Retrieved Sources:** The Bharatiya Nagarik Suraksha Sanhita, 2023 s.531 ('Repeal and savings.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.457 ('Power to appoint place of imprisonment.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.260 ('Procedure in cases instituted under sub-section (2) of section 222.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.285 ('Procedure for summary trials.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.361 ('Procedure in cases which Magistrate cannot dispose of.')
- **Classification:** `PARTIALLY_CORRECT` (Score: 1/2)
- **Evidence Status:** `ANSWERABLE`

### Question [eval_018]: Which statute has replaced the Indian Evidence Act, 1872?

- **Reference Answer:** The Bharatiya Sakshya Adhiniyam, 2023 (BSA) has replaced the Indian Evidence Act, 1872, governing the law of evidence in Indian courts from 1 July 2024 onward, subject to applicable transitional provisions.
- **Fixed Pipeline Answer:** The Bharatiya Sakshya Adhiniyam, 2023 (BSA) replaced the Indian Evidence Act, 1872. The BSA came into force on 1 July 2024, repealing the Indian Evidence Act, 1872.
- **Retrieved Sources:** The Bharatiya Sakshya Adhiniyam, 2023 s.170 ('Repeal and savings.') | The Bharatiya Sakshya Adhiniyam, 2023 s.103 ('Saving of provisions of Indian Succession Act relating to wills.') | The Bharatiya Sakshya Adhiniyam, 2023 s.94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of') | The Bharatiya Sakshya Adhiniyam, 2023 s.166 ('Giving, as evidence, of document called for and produced on notice.') | The Bharatiya Sakshya Adhiniyam, 2023 s.62 ('Special provisions as to evidence relating to electronic record.')
- **Classification:** `CORRECT` (Score: 2/2)
- **Evidence Status:** `ANSWERABLE`

### Question [eval_019]: A theft allegedly took place on 15 June 2024, but the FIR is registered and the trial happens in 2025. Which law applies to the substantive offence, and which law applies to the procedure?

- **Reference Answer:** Because the alleged offence occurred before 1 July 2024, the substantive question of whether an offence was committed, and what punishment applies, is generally governed by the Indian Penal Code, 1860 as it stood on 15 June 2024 -- consistent with the constitutional bar on retrospective criminal liability under Article 20(1). Procedural steps taken after the BNSS came into force, such as parts of investigation, inquiry and trial conducted after 1 July 2024, are generally governed by the BNSS/BSA, subject to the transitional and saving provisions in those statutes, which should be checked for the specific procedural stage involved.
- **Fixed Pipeline Answer:** ### Legal Answer:
Substantive Criminal Liability: Strictly governed by the Indian Penal Code, 1860 under Article 20(1) of the Constitution. The Bharatiya Nyaya Sanhita, 2023 CANNOT be applied retrospectively to penalize acts committed prior to July 1, 2024.
- **Retrieved Sources:** The Bharatiya Nyaya Sanhita, 2023 s.1 ('Short title, commencement and application.') | The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.') | The Bharatiya Nyaya Sanhita, 2023 s.305 ('Theft in a dwelling house, or means of transportation or place of worship, etc.') | The Bharatiya Nyaya Sanhita, 2023 s.112 ('Petty organised crime.') | The Bharatiya Nyaya Sanhita, 2023 s.15 ('Act of Judge when acting judicially.')
- **Classification:** `INCORRECT` (Score: 0/2)
- **Evidence Status:** `TEMPORALLY_UNCERTAIN`

### Question [eval_074]: Does the Bharatiya Sakshya Adhiniyam, 2023 treat electronic and digital records the same way as the earlier Indian Evidence Act, 1872, in terms of admissibility conditions?

- **Reference Answer:** The BSA continues to recognise electronic and digital records as documents and generally requires compliance with conditions (such as a certificate about the manner of production/reliability of the electronic record) before secondary evidence of an electronic record can be admitted, broadly similar to how the Indian Evidence Act treated electronic records after its amendment. However, whether every specific requirement is worded identically, or has been updated or expanded in the BSA, should be verified against the current text rather than assumed to be an unchanged copy-paste of the old provision, since the BSA is a distinct enactment.
- **Fixed Pipeline Answer:** Statutory Citation Warning: The generated answer referenced unverified or non-existent provisions: Section 65B of BSA (non-existent provision; BSA equivalent is Section 63). In accordance with strict legal fidelity rules, this citation cannot be validated from authoritative sources.
- **Retrieved Sources:** The Bharatiya Sakshya Adhiniyam, 2023 s.61 ('Electronic or digital record.') | The Bharatiya Sakshya Adhiniyam, 2023 s.63 ('Admissibility of electronic records.') | The Bharatiya Sakshya Adhiniyam, 2023 s.170 ('Repeal and savings.') | The Bharatiya Sakshya Adhiniyam, 2023 s.85 ('Presumption as to electronic agreements.') | The Bharatiya Sakshya Adhiniyam, 2023 s.63 ('Admissibility of electronic records.')
- **Classification:** `CITATION_ERROR` (Score: 0/2)
- **Evidence Status:** `ANSWERABLE`

### Question [eval_114]: Is it true that 'first-time offenders under the BNS are always granted probation instead of jail time' as a fixed statutory rule?

- **Reference Answer:** No, this is not an accurate general statement of a fixed rule. While Indian law does have provisions allowing courts to release certain offenders on probation instead of sentencing them to imprisonment (generally for less serious offences and subject to the court's discretion, the offender's antecedents, and the nature of the offence), this is a discretionary possibility in appropriate cases under the applicable probation law, not an automatic entitlement that applies to 'first-time offenders' as a blanket rule under the BNS. An AI system should avoid stating this kind of sweeping, inaccurate generalisation as if it were a fixed statutory guarantee.
- **Fixed Pipeline Answer:** This statement is legally false. Under Section 4 of the Bharatiya Nyaya Sanhita, 2023, the punishment for offences is imprisonment, fine, or community service, with no blanket statutory rule granting probation to first-time offenders.
- **Retrieved Sources:** The Bharatiya Nyaya Sanhita, 2023 s.11 ('Solitary confinement.') | The Bharatiya Nyaya Sanhita, 2023 s.4 ('Punishments.') | The Bharatiya Nyaya Sanhita, 2023 s.64 ('Punishment for rape.') | The Bharatiya Nyaya Sanhita, 2023 s.71 ('Punishment for repeat offenders.') | The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.')
- **Classification:** `INCORRECT` (Score: 0/2)
- **Evidence Status:** `ANSWERABLE`

## 4. Final Verdict

**System Classification:** **`PASS WITH LIMITATIONS`**
