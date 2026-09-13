# LegalAI v2: 125-Question Evaluation Report

**Execution Timestamp:** 2026-09-13 10:40:14
**Base Model:** `Qwen/Qwen2.5-14B-Instruct`
**LoRA Adapter:** `outputs/qwen14b-legalai-v2`
**Evaluation Benchmark:** `data/legal_eval_125.jsonl` (Total: 125)

## 1. Executive Summary

- **Total Questions:** `125`
- **Generation Completed:** `125/125`
- **Preliminary Accuracy:** **`38.4%`**
- **Overall Hallucination Rate:** **`0.0%`** (Clear: 0, Possible: 0)
- **Outdated Law Rate:** **`0.0%`** (0/125)
- **Cases Requiring Human Review:** `53`

## 2. Overall Performance Breakdown

- Substantially Correct (Score 2): `24` (19.2%)
- Partially Correct (Score 1): `48` (38.4%)
- Incorrect (Score 0): `53` (42.4%)

## 3. Category Performance

| Category | Questions | Correct | Partial | Incorrect | Hallucinations | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Arbitration/Civil Procedure | 4 | 1 | 2 | 1 | 0 | 50.0% |
| Company Law | 6 | 1 | 1 | 4 | 0 | 25.0% |
| Constitution | 15 | 5 | 5 | 5 | 0 | 50.0% |
| Consumer Law | 8 | 2 | 3 | 3 | 0 | 43.8% |
| Contract Law | 10 | 3 | 6 | 1 | 0 | 60.0% |
| Criminal Law | 21 | 4 | 8 | 9 | 0 | 38.1% |
| Cross-Domain | 9 | 0 | 6 | 3 | 0 | 33.3% |
| Cyber Law | 8 | 0 | 3 | 5 | 0 | 18.8% |
| Evidence Law | 7 | 1 | 4 | 2 | 0 | 42.9% |
| Family Law | 7 | 2 | 2 | 3 | 0 | 42.9% |
| Hallucination Detection | 5 | 0 | 1 | 4 | 0 | 10.0% |
| Intellectual Property | 5 | 3 | 1 | 1 | 0 | 70.0% |
| Labour Law | 4 | 0 | 0 | 4 | 0 | 0.0% |
| Mixed / Real-World Scenario | 8 | 1 | 2 | 5 | 0 | 25.0% |
| Property Law | 8 | 1 | 4 | 3 | 0 | 37.5% |

## 4. Difficulty Performance

| Difficulty | Questions | Correct | Partial | Incorrect | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Easy | 25 | 3 | 10 | 12 | 32.0% |
| Medium | 64 | 15 | 26 | 23 | 43.8% |
| Hard | 36 | 6 | 12 | 18 | 33.3% |

## 5. Current-Law Performance

- **Total Criminal Law Questions:** `21`
- **Accurate Current/Transitional Law Citations:** `20`
- **Outdated Statute Citations Detected:** `0`

## 6. Hallucination Analysis

No clear hallucinations were detected during automated scoring.

## 7. Outdated-Law Analysis

No problematic reliance on outdated criminal law was detected.

## 8. Sample Strongest Responses (Top 10)

### 1. [eval_003] (Constitution | Score: 11/11)
- **Question:** What is the difference between a Fundamental Right and a Directive Principle of State Policy?
- **Model Answer:** The Constitution of India contains two distinct sets of provisions: Fundamental Rights (Articles 12 to 35) and Directive Principles of State Policy (Articles 36 to 51). Fundamental Rights are enforceable judicially against the state and private parties, while Directive Principles are non-enforceable...

### 2. [eval_004] (Constitution | Score: 11/11)
- **Question:** What remedy is available under Article 32, and how is it different from Article 226?
- **Model Answer:** Article 32 of the Constitution of India provides the right to move the Supreme Court by appropriate proceedings for enforcement of fundamental rights. Article 226 empowers High Courts to issue writs for the enforcement of any of the rights conferred by Part III of the Constitution. The primary diffe...

### 3. [eval_005] (Constitution | Score: 11/11)
- **Question:** Can Parliament amend a Fundamental Right under Article 368? What limits apply?
- **Model Answer:** The power of Parliament to amend the Constitution under Article 368(1) is subject to the doctrine of limited amending power. In Kesavananda Bharati v. State of Kerala (1973), the Supreme Court held that Parliament cannot use its constituent power to destroy the basic structure of the Constitution, i...

### 4. [eval_010] (Constitution | Score: 11/11)
- **Question:** What is a writ of habeas corpus and when is it used?
- **Model Answer:** A writ of habeas corpus is a judicial order requiring a person holding another in custody to produce the detained individual before a court and justify the detention's legality. It is a fundamental remedy under Article 22(1) of the Constitution, available even against private individuals who wrongfu...

### 5. [eval_012] (Constitution | Score: 11/11)
- **Question:** What does Article 32 mean when it is called the 'heart and soul' of the Constitution?
- **Model Answer:** The phrase "heart and soul" of the Constitution refers to Article 32, which establishes the fundamental right to move the Supreme Court by appropriate proceedings for enforcement of the rights conferred by Part III (fundamental rights). In Kesavananda Bharati v. State of Kerala (1973), the Supreme C...

### 6. [eval_024] (Criminal Law | Score: 11/11)
- **Question:** A person is arrested by the police. What are their basic rights at the time of arrest under Indian law?
- **Model Answer:** The Supreme Court in D.K. Basu v. State of West Bengal (1997) laid down detailed guidelines to be followed by police officers at the time of arrest: (1) Inform the person of the grounds of arrest; (2) Record the fact of arrest in the diary; (3) Advise the person of their right to communicate with a ...

### 7. [eval_025] (Criminal Law | Score: 11/11)
- **Question:** What is an FIR and can it be registered at any police station regardless of where the offence occurred?
- **Model Answer:** An FIR (First Information Report) is the first written record of a cognizable offence made by a victim or witness to a police officer under Section 173(1) of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS). It is not a complaint or a police report — it must be recorded verbatim in the prescribed...

### 8. [eval_029] (Criminal Law | Score: 11/11)
- **Question:** What does 'mens rea' mean, and why does it matter in most criminal offences?
- **Model Answer:** 'Mens rea' means 'guilty mind.' In criminal law, it refers to the mental element of intent, knowledge, or recklessness that must accompany the physical act (actus reus) to establish criminal liability. The principle that mens rea is required for conviction is deeply rooted in Indian criminal jurispr...

### 9. [eval_034] (Criminal Law | Score: 11/11)
- **Question:** What is the purpose of a charge in a criminal trial, and what must it contain?
- **Model Answer:** The charge sheet is the formal document that sets out the specific offences alleged against the accused, based on the police investigation and evidence collected. It must be prepared by the Public Prosecutor or the Assistant Public Prosecutor and presented to the court within 60 days of the accused'...

### 10. [eval_037] (Contract Law | Score: 11/11)
- **Question:** What are the essential elements of a valid contract under the Indian Contract Act, 1872?
- **Model Answer:** The essential elements of a valid contract under Section 10 of the Indian Contract Act, 1872 are: (1) Free consent of parties; (2) Competent contracting parties; (3) Lawful consideration; (4) Lawful object; (5) Genuine intention to create legal relations; (6) Certainty and possibility of performance...

## 9. Sample Weakest Responses (Bottom 10)

### 1. [eval_125] (Mixed / Real-World Scenario | Score: 6/11)
- **Question:** Someone wants to know if their upcoming business contract is 'legally safe.' Can this be assessed without seeing the contract?
- **Model Answer:** No. Assessing whether a business contract is legally safe requires reviewing its specific terms, conditions, and governing law — it cannot be done based solely on general assumptions about the other party's reputation or past dealings....
- **Review Reason:** Correctness score is 0

### 2. [eval_001] (Constitution | Score: 7/11)
- **Question:** What does Article 21 of the Constitution of India protect?
- **Model Answer:** Article 21 of the Constitution of India protects the right to life and personal liberty, which includes the right to health, education, and a clean environment. It also prohibits arbitrary deprivation of life or personal liberty except according to procedure established by law....
- **Review Reason:** Correctness score is 0

### 3. [eval_007] (Constitution | Score: 7/11)
- **Question:** What is protected under Article 14 of the Constitution?
- **Model Answer:** Article 14 of the Constitution of India protects all persons within India's territory against discrimination by the State. It does not require proof of a fundamental right being violated; it applies to any person affected by an arbitrary or discriminatory State action....
- **Review Reason:** Correctness score is 0

### 4. [eval_008] (Constitution | Score: 7/11)
- **Question:** What is the scope of the freedoms guaranteed under Article 19(1)?
- **Model Answer:** The freedoms guaranteed under Article 19(1) of the Constitution of India are: (a) freedom of speech and expression; (b) freedom to assemble peacefully and without arms; (c) freedom to form associations or unions; (d) freedom to move freely throughout the territory of India; (e) freedom to reside and...
- **Review Reason:** Correctness score is 0

### 5. [eval_013] (Constitution | Score: 7/11)
- **Question:** Can a Fundamental Right be waived by the person entitled to it, such as by agreeing in a contract not to challenge unconstitutional State action?
- **Model Answer:** No. Fundamental Rights under Part III of the Constitution cannot be waived by private agreement or consent. The Supreme Court has repeatedly held that Fundamental Rights are absolute and non-derogable, and cannot be bargained away by individuals. In practice, this means that even if a person signs a...
- **Review Reason:** Correctness score is 0

### 6. [eval_015] (Constitution | Score: 7/11)
- **Question:** A newly enacted central law appears to conflict with an existing state law on a subject in the Concurrent List. Which law prevails?
- **Model Answer:** The doctrine of pith and substance applies: if the core object of the enactment falls within the central legislative competence, the central law prevails even if it incidentally touches upon matters within state jurisdiction....
- **Review Reason:** Correctness score is 0

### 7. [eval_018] (Criminal Law | Score: 7/11)
- **Question:** Which statute has replaced the Indian Evidence Act, 1872?
- **Model Answer:** The Indian Evidence Act, 1872 remains in force as the governing statute for admissibility of evidence in civil and criminal trials in India. There is no replacement statute; it continues to be applied alongside procedural rules under the Bharatiya Nagarik Suraksha Sanhita (BNSS) and the Bharatiya Sa...
- **Review Reason:** Correctness score is 0

### 8. [eval_020] (Criminal Law | Score: 7/11)
- **Question:** Is it always safe to assume that a given IPC section maps one-to-one onto a single BNS section with the same content?
- **Model Answer:** No. The assumption that every IPC section has a direct equivalent in the Bharatiya Nyaya Sanhita (BNS) with identical wording is incorrect. The BNS is a separate criminal code enacted in 2023, replacing the Indian Penal Code (IPC), and while it retains many of the same offences, the specific section...
- **Review Reason:** Correctness score is 0

### 9. [eval_023] (Criminal Law | Score: 7/11)
- **Question:** Can a person simply ignore a summons issued by a criminal court because they believe the case against them is false?
- **Model Answer:** No. Ignoring a summons is a serious error under Section 482 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023. Once a summons is served, the accused must appear before the court on the specified date. Failing to do so can result in the court issuing a warrant for the accused's arrest, and if th...
- **Review Reason:** Correctness score is 0

### 10. [eval_027] (Criminal Law | Score: 7/11)
- **Question:** What is the significance of the transitional/saving provisions in the BNSS for criminal cases that were already pending on 1 July 2024?
- **Model Answer:** The transitional/saving provisions in the Bharatiya Nagarik Suraksha Sanhita (BNSS) are crucial because they determine whether a case pending on 1 July 2024 continues under the old IPC or is transferred to the new code. In practice, this means a person arrested on 30 June 2024 for a crime under the ...
- **Review Reason:** Correctness score is 0

