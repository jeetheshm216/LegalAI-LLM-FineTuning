# LegalAI 125-Question Evaluation Report

## 1. Evaluation Configuration

- **Base Model:** `Qwen/Qwen2.5-14B-Instruct`
- **LoRA Adapter Path:** `outputs/qwen14b-first-run-final-dataset`
- **Evaluation Dataset:** `data/legal_eval_125.jsonl`
- **Total Questions:** `125`
- **Primary GPU:** `NVIDIA B200`
- **Python Environment:** `3.12.3 (PyTorch 2.11.0+cu128)`
- **Generation Parameters:** `do_sample=False, max_new_tokens=512, torch.inference_mode()`
- **Evaluation Timestamp:** `2026-09-13 03:40:31`

## 2. Overall Results

- **Total Questions Evaluated:** `125`
- **Generation Success:** `125` (`0` failures)
- **Substantially Correct (2/2):** `23`
- **Partially Correct (1/2):** `53`
- **Incorrect (0/2):** `49`
- **Preliminary Accuracy:** `39.6%`
- **Hallucination Rate (Clear):** `0.8%` (1 clear, 0 possible)
- **Outdated-Law Rate:** `0.8%` (1 flagged)
- **Cases Flagged for Human Review:** `49`

## 3. Category Performance

| Category | Questions | Correct | Partial | Incorrect | Hallucinations | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Arbitration/Civil Procedure | 4 | 2 | 1 | 1 | 0 | 62.5% |
| Company Law | 6 | 0 | 2 | 4 | 0 | 16.7% |
| Constitution | 15 | 4 | 5 | 6 | 0 | 43.3% |
| Consumer Law | 8 | 1 | 4 | 3 | 0 | 37.5% |
| Contract Law | 10 | 4 | 3 | 3 | 0 | 55.0% |
| Criminal Law | 21 | 3 | 11 | 7 | 0 | 40.5% |
| Cross-Domain | 9 | 3 | 5 | 1 | 0 | 61.1% |
| Cyber Law | 8 | 0 | 5 | 3 | 0 | 31.2% |
| Evidence Law | 7 | 0 | 3 | 4 | 0 | 21.4% |
| Family Law | 7 | 2 | 2 | 3 | 0 | 42.9% |
| Hallucination Detection | 5 | 0 | 1 | 4 | 1 | 10.0% |
| Intellectual Property | 5 | 1 | 2 | 2 | 0 | 40.0% |
| Labour Law | 4 | 0 | 0 | 4 | 0 | 0.0% |
| Mixed / Real-World Scenario | 8 | 1 | 4 | 3 | 0 | 37.5% |
| Property Law | 8 | 2 | 5 | 1 | 0 | 56.2% |

## 4. Difficulty Performance

| Difficulty | Questions | Correct | Partial | Incorrect | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Easy | 25 | 4 | 9 | 12 | 34.0% |
| Medium | 64 | 12 | 30 | 22 | 42.2% |
| Hard | 36 | 7 | 14 | 15 | 38.9% |

## 5. Current-Law Performance

The evaluation specifically assessed how the model handles the transition from legacy criminal statutes (IPC, CrPC, Indian Evidence Act) to India's modern criminal codes (BNS, BNSS, BSA) effective 1 July 2024.
- **Total Current-Law Transition Questions:** `21`
- **Accurate Current/Transitional Law Citations:** `18`
- **Outdated Statute Citations Detected:** `1`

## 6. Hallucination Analysis

### Question [eval_111]
- **Question:** Which Supreme Court case held that 'the right to Wi-Fi access is a Fundamental Right under Article 21'?
- **Model Claim:** The Supreme Court has never held that 'the right to Wi-Fi access' is a fundamental right under Article 21 of the Constitution. The right to internet access, including Wi-Fi, has been treated as a facet of the right to privacy, but it has never been c...
- **Expected Legal Position:** There is no well-established, verifiable Supreme Court judgment holding that 'the right to Wi-Fi access' as such is a Fundamental Right under Article 21. An AI system should not invent or attribute a case name and holding of this kind; if it is not c...
- **Hallucination Diagnosis:** Fabricated case holding Wi-Fi access as Art 21 Fundamental Right.

## 7. Outdated-Law Analysis

- **[eval_017] Which statute has replaced the Code of Criminal Procedure, 1973?**: Cites legacy provisions without noting BNS/BNSS/BSA transition.
## 8. Insufficient-Information Analysis

Testing model caution when facts are deliberately underspecified:

- **[eval_104] A person's employer deducts a sum from their salary every mo...**
  - **Caution Score:** `1/2`
  - **Model Excerpt:** "The deduction of Rs 20 per month as professional tax under Section 17(3) of the Maharashtra State Goods and Services Tax Act, 2018 is lawful, since it falls within the Rs 2,500 ann..."

- **[eval_106] A small business owner receives a formal notice from a secur...**
  - **Caution Score:** `1/2`
  - **Model Excerpt:** "This is a demand notice under Section 13(2) of the SARFAESI Act, 2002, issued by a secured creditor (bank or NBFC) before initiating formal action to take possession of security. T..."

- **[eval_124] A person was in a car accident and wants to know whether the...**
  - **Caution Score:** `1/2`
  - **Model Excerpt:** "No — criminal liability under Section 184 of the Motor Vehicles Act, 1988 requires proof of negligence causing death or injury, and the punishment (up to two years' imprisonment an..."

- **[eval_125] Someone wants to know if their upcoming business contract is...**
  - **Caution Score:** `2/2`
  - **Model Excerpt:** "No — whether a business contract is legally safe depends entirely on its specific terms, which cannot be assessed without seeing the document itself. Common risks include inadequat..."

## 9. Strongest Responses (Sample Top 10)

### 1. [eval_003] (Constitution | Score: 11/11)
- **Question:** What is the difference between a Fundamental Right and a Directive Principle of State Policy?
- **Model Answer:** The distinction between a Fundamental Right and a Directive Principle of State Policy is crucial under Article 32 of the Constitution. Fundamental Rights are enforceable by courts against the state, while Directive Principles are non-enforceable guidelines meant to guide the state in governance....

### 2. [eval_004] (Constitution | Score: 11/11)
- **Question:** What remedy is available under Article 32, and how is it different from Article 226?
- **Model Answer:** Article 32 of the Constitution of India provides the right to move the Supreme Court by appropriate proceedings for enforcement of Fundamental Rights, and the Supreme Court has power to issue directions, orders, or writs, including habeas corpus, mandamus, prohibition, quo warranto, and certiorari, ...

### 3. [eval_009] (Constitution | Score: 11/11)
- **Question:** A state law imposes a restriction on freedom of speech that is not linked to any of the grounds listed in Article 19(2). Is such a restriction valid?
- **Model Answer:** No, such a restriction is invalid under Article 19(1)(a) of the Constitution. The Supreme Court has held that restrictions on free speech must be narrowly tailored to one of the specific grounds listed in Article 19(2): security of the State, friendly relations with foreign States, public order, dec...

### 4. [eval_015] (Constitution | Score: 11/11)
- **Question:** A newly enacted central law appears to conflict with an existing state law on a subject in the Concurrent List. Which law prevails?
- **Model Answer:** Under Article 254(1) of the Constitution, if a central law and a state law dealing with a matter in the Concurrent List (such as criminal law, marriage and divorce, or education) conflict, the central law prevails to the extent of the repugnancy, but Parliament must notify the President within one m...

### 5. [eval_025] (Criminal Law | Score: 11/11)
- **Question:** What is an FIR and can it be registered at any police station regardless of where the offence occurred?
- **Model Answer:** An FIR (First Information Report) is a written record of the first information about a cognizable offence given to the police by a victim or witness. It is the first step in criminal proceedings under Section 154 CrPC. In practice, an FIR can be registered at any police station, regardless of whethe...

### 6. [eval_029] (Criminal Law | Score: 11/11)
- **Question:** What does 'mens rea' mean, and why does it matter in most criminal offences?
- **Model Answer:** 'Mens rea' means 'guilty mind.' In criminal law, mens rea refers to the mental element of a crime — the intention, knowledge, or recklessness with which an act was committed. It's a key component of most substantive offences under the BNS, 2023, since the Act generally requires proof of both actus r...

### 7. [eval_036] (Criminal Law | Score: 11/11)
- **Question:** What is 'discharge' in a criminal case, and how is it different from acquittal?
- **Model Answer:** 'Discharge' under Section 245 of the CrPC is distinct from acquittal: while an acquittal means the court has found the accused not guilty of the offence, discharge means the court has decided the trial cannot proceed because the offence is barred by limitation, the accused was not present at the sce...

### 8. [eval_037] (Contract Law | Score: 11/11)
- **Question:** What are the essential elements of a valid contract under the Indian Contract Act, 1872?
- **Model Answer:** Section 10 of the Indian Contract Act, 1872 requires free consent, competent parties, lawful consideration, lawful object, and genuine intention to create legal relations for a contract to be enforceable. In practice, courts have held that a contract lacking any of these elements is void ab initio....

### 9. [eval_039] (Contract Law | Score: 11/11)
- **Question:** What is the difference between a void agreement and a voidable contract?
- **Model Answer:** A void agreement has no legal existence from the start — it's as if it never existed at all. A voidable contract, by contrast, is one that can be ratified or rescinded by the aggrieved party — it exists until challenged, but once challenged, it becomes void ab initio....

### 10. [eval_040] (Contract Law | Score: 11/11)
- **Question:** What is the difference between a 'condition' and a 'warranty' in a contract for the sale of goods?
- **Model Answer:** Under Section 16(1) of the Sale of Goods Act, 1930, a condition is a stipulation essential to the main purpose of the contract, breach of which gives the aggrieved party the right to treat the contract as repudiated and claim damages. In contrast, a warranty is a promise collateral to the main purpo...

## 10. Weakest Responses (Sample Bottom 10)

### 1. [eval_017] (Criminal Law | Score: 5/11)
- **Question:** Which statute has replaced the Code of Criminal Procedure, 1973?
- **Model Answer:** The Code of Criminal Procedure, 1973 remains in force today; it has not been replaced by a newer statute....
- **Review Reason:** Outdated law flag: clear; Correctness score is 0; Low total score (5/11)

### 2. [eval_111] (Hallucination Detection | Score: 5/11)
- **Question:** Which Supreme Court case held that 'the right to Wi-Fi access is a Fundamental Right under Article 21'?
- **Model Answer:** The Supreme Court has never held that 'the right to Wi-Fi access' is a fundamental right under Article 21 of the Constitution. The right to internet access, including Wi-Fi, has been treated as a facet of the right to privacy, but it has never been categorically declared a standalone fundamental rig...
- **Review Reason:** Hallucination flag: clear (Fabricated case holding Wi-Fi access as Art 21 Fundamental Right.); Correctness score is 0; Low total score (5/11)

### 3. [eval_124] (Mixed / Real-World Scenario | Score: 6/11)
- **Question:** A person was in a car accident and wants to know whether they can be held criminally liable. Can this be answered definitively without more facts?
- **Model Answer:** No — criminal liability under Section 184 of the Motor Vehicles Act, 1988 requires proof of negligence causing death or injury, and the punishment (up to two years' imprisonment and/or a fine) applies only if that element is established....
- **Review Reason:** Correctness score is 0

### 4. [eval_005] (Constitution | Score: 7/11)
- **Question:** Can Parliament amend a Fundamental Right under Article 368? What limits apply?
- **Model Answer:** Parliament cannot amend a Fundamental Right under Article 368(4) in a manner that takes away or abridges it; any such amendment must be upheld by a two-thirds majority of both Houses of Parliament and ratification by at least half of the state legislatures....
- **Review Reason:** Correctness score is 0

### 5. [eval_006] (Constitution | Score: 7/11)
- **Question:** What protection does Article 20(1) give against retrospective criminal laws?
- **Model Answer:** Article 20(1) of the Constitution of India protects a person from being convicted of an offence unless it was defined as such by law at the time the act was committed — this is known as the principle of legality or the rule against ex post facto criminal legislation. In practice, this means that Par...
- **Review Reason:** Correctness score is 0

### 6. [eval_007] (Constitution | Score: 7/11)
- **Question:** What is protected under Article 14 of the Constitution?
- **Model Answer:** Article 14 of the Constitution protects against discrimination by the State, but it does not protect against private discrimination. In practice, this means that while a government department cannot refuse to register a complaint based on a person's caste, religion, or gender, a private employer can...
- **Review Reason:** Correctness score is 0

### 7. [eval_011] (Constitution | Score: 7/11)
- **Question:** Which Article of the Constitution abolishes untouchability?
- **Model Answer:** Untouchability was abolished by Article 17 of the Constitution, which came into force on 26 January 1950. The Preamble to the Constitution also commits India to equality and fraternity, reflecting the underlying principle against untouchability....
- **Review Reason:** Correctness score is 0

### 8. [eval_012] (Constitution | Score: 7/11)
- **Question:** What does Article 32 mean when it is called the 'heart and soul' of the Constitution?
- **Model Answer:** The phrase "heart and soul" of the Constitution refers to Article 32, which gives citizens the right to move the Supreme Court by way of a writ petition for enforcement of fundamental rights. This provision is considered central because it provides a direct remedy against any authority or person vio...
- **Review Reason:** Correctness score is 0

### 9. [eval_013] (Constitution | Score: 7/11)
- **Question:** Can a Fundamental Right be waived by the person entitled to it, such as by agreeing in a contract not to challenge unconstitutional State action?
- **Model Answer:** No, a Fundamental Right cannot be waived by the person entitled to it. The Supreme Court has held that Fundamental Rights are not mere private rights that can be bargained away; they are public guarantees against the State's arbitrary power, and so cannot be waived even by express agreement. In prac...
- **Review Reason:** Correctness score is 0

### 10. [eval_020] (Criminal Law | Score: 7/11)
- **Question:** Is it always safe to assume that a given IPC section maps one-to-one onto a single BNS section with the same content?
- **Model Answer:** No — the assumption that every IPC section has a direct equivalent in the Bharatiya Nagarik Suraksha Sanhita (BNS) with identical wording is incorrect. The BNS was drafted as a standalone criminal code intended to replace the entire Indian Penal Code, so its structure and numbering differ from the I...
- **Review Reason:** Correctness score is 0

## 11. Human Review

A total of **49** items have been logged in `legal_eval_125_HUMAN_REVIEW_REQUIRED.md` for manual expert validation.

## 12. Final Assessment

**Assessment Verdict:** Significant reliability issues — Requires further dataset regularization and LoRA hyperparameter tuning before interactive deployment.
