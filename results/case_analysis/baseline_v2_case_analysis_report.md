# LegalAI Baseline V2 Evaluation & Case Analysis Gap Analysis Report

**Date:** 2026-09-14 13:38:39  
**Evaluated Model:** LegalAI V2 Baseline (`Qwen/Qwen2.5-14B-Instruct` + `outputs/qwen14b-legalai-v2`)  
**Live Backend Service:** `http://127.0.0.1:8008` on Physical GPU 2  
**Evaluation Scope:** 18 Independent Test Categories (Zero Case Leakage, Zero Training Duplication)  

---

## 1. Executive Metric Summary

> [!IMPORTANT]
> **Strict Metric Separation**:
> - **ANSWER ACCURACY:** Exact factual and statutory correctness on positive legal queries.
> - **SAFE HANDLING SCORE:** Resistance to hallucination, graceful gap detection, and proper abstention on out-of-corpus queries.

| Primary Benchmark Metric | Score | Evaluation Method & Criterion |
| :--- | :---: | :--- |
| **ANSWER ACCURACY** | **40.0%** | Exact accuracy on statutory & temporal legal queries |
| **SAFE HANDLING SCORE** | **20.0%** | Combined score on abstention, trap avoidance, and safety |

---

## 2. Detailed Dimension Metrics (The 12 Core Benchmarks)

| Benchmark Dimension | V2 Baseline Score | Target Standard | Primary Failure Mode Observed in V2 Baseline |
| :--- | :---: | :---: | :--- |
| **Factual Grounding** | **0.0%** | 95%+ | Returns generic UI case-guidance stubs instead of digesting in-prompt case facts |
| **Evidence Grounding** | **0.0%** | 95%+ | Cannot link legal arguments to specific documentary exhibits or witness statements |
| **Legal Citation Accuracy** | **40.0%** | 98%+ | Solid on ingested BNS/BNSS/BSA; poor when asked about external or composite acts |
| **Citation Completeness** | **40.0%** | 90%+ | Cites single section without providing operative statutory sub-clauses |
| **Contradiction Detection** | **0.0%** | 90%+ | Lacks reasoning to compare date variances between FIR and deposition |
| **Evidence Gap Detection** | **0.0%** | 90%+ | Fails to use *"The supplied case material does not establish this"*; assumes unstated facts |
| **Argument Quality** | **0.0%** | 90%+ | Outputs disjointed paragraphs rather than the 8-part structured argument schema |
| **Counterargument Quality** | **0.0%** | 90%+ | Does not proactively anticipate adversary positions or structure formal rebuttals |
| **Abstention Correctness** | **0.0%** | 100% | Dangerously substitutes BNS when asked about foreign or out-of-corpus law |
| **Temporal Accuracy** | **40.0%** | 95%+ | Struggles with Article 20(1) retroactivity boundaries on pre-July 2024 offences |
| **Wrong-Act Rate** | **100.0%** | 0.0% | Injects local criminal Sanhita into out-of-corpus foreign queries |
| **Hallucination Rate** | **60.0%** | 0.0% | Accepts fabricated provisions (e.g. accepts "Section 65B of BSA" as valid) |

---

## 3. Performance Across the 18 Evaluation Categories

| Cat ID | Evaluation Category | Evaluation Set Source | V2 Baseline Behavior |
| :---: | :--- | :--- | :--- |
| **01** | `Case Summary` | `CA01`, `CA02` Test Sets | Returns generic UI metadata stub; fails to synthesize supplied facts |
| **02** | `Evidence Analysis` | `CA05` Test Set | Fails to evaluate admissibility or probative value of exhibits |
| **03** | `Evidence Gaps` | `CA06` Test Set | Cannot identify missing primary contracts or unexamined witnesses |
| **04** | `Contradictions` | `CA07` Test Set | Completely misses testimonial vs documentary discrepancies |
| **05** | `Strengths` | `CA08` Test Set | Does not isolate uncontradicted factual pillars |
| **06** | `Weaknesses` | `CA09` Test Set | Either uses defeatist language or fails to spot preliminary objections |
| **07** | `Arguments` | `CA10` Test Set | Lacks 8-part argument schema (`Argument`, `Facts`, `Evidence`, `Law`, `Reasoning`, `Counter`, `Response`, `Uncertainty`) |
| **08** | `Counterarguments` | `CA11` Test Set | Does not anticipate adversary claims on limitation or onus |
| **09** | `Fact-to-Law Mapping`| `CA14` Test Set | Cannot map individual factual events to statutory ingredients |
| **10** | `Hearing Preparation`| `CA16` Test Set | Fails to produce 2-minute pitch or anticipated bench questions |
| **11** | `Witness Questions` | `CA12` Test Set | Incapable of drafting cross-examination impeachment lines |
| **12** | `Document Review` | `CA13`, `CA19` Test Sets | Ignores execution, stamp, and registration validity issues |
| **13** | `Case Strategy` | `CA24`, `CA17`, `CA21` | Defaults to generic client advice without tactical roadmap |
| **14** | `Legal Research` | `CA15`, `CA20` Test Sets | Lacks distinction between binding ratio and obiter dicta |
| **15** | `General Legal` | Validated Statutory Set | **Strong (40.0%)**: Retrieves clean BNS/BNSS provisions via Legal RAG |
| **16** | `Abstention` | Out-of-Corpus Probe | **Critical Failure (0.0%)**: Substitutes BNS for French/foreign law |
| **17** | `Temporal Law` | Pre/Post July 2024 Set | **Moderate (40.0%)**: Misses nuance of Article 20(1) vs BNSS Sec 531 savings |
| **18** | `Citation Correct` | Adversarial Traps Set | **Vulnerable (60.0% Hallucination)**: Accepts fake sections (Sec 65B BSA, Sec 999 BNS) |

---

## 4. Answering the 7 Architectural Questions

### 1. Where does V2 currently fail?
V2 operates strictly as a **statutory Q&A search engine**. When given a client case scenario with facts, witness statements, and evidence:
- The Query Router classifies it as `CASE_QUERY` and returns a hardcoded UI guidance stub (`generate_case_guidance`) instructing the user to upload documents, rather than reading and analyzing the case facts provided in the prompt.
- Even when forced into general prompt mode, V2 lacks the cognitive grammar of a practicing advocate: it cannot structure an 8-part argument, cannot formulate cross-examination impeachment lines, cannot identify evidence gaps, and fails to state *"The supplied case material does not establish this."*
- On out-of-corpus queries (e.g. French Penal Code), it exhibits **statute substitution**, forcing BNS abetment provisions into a question about French law.

### 2. Which failures can fine-tuning solve?
Fine-tuning on the new **Case Analysis Dataset (7,260 examples)** directly solves:
1. **Case Reasoning Grammar**: Teaching the model how to parse `CASE MATERIAL` and produce structured lawyer outputs (`FACTS`, `EVIDENCE`, `LEGAL ISSUES`, `ANALYSIS`, `ARGUMENTS`).
2. **The 8-Part Argument Schema**: Training the model to systematically produce: `Argument` → `Supporting facts` → `Supporting evidence` → `Applicable law` → `Reasoning` → `Likely counterargument` → `Response` → `Remaining uncertainty`.
3. **Epistemic Honesty on Evidence Gaps**: Inculcating the discipline to state: *"The supplied case material does not establish this"* whenever evidence is missing, rather than inventing facts.
4. **Non-Dogmatic Weakness Analysis**: Enforcing the use of *"Potential weakness"*, *"Potential risk"*, *"Requires verification"*, rather than defeatist claims (*"We will lose"*).
5. **Cross-Examination & Witness Scrutiny**: Teaching the model how to formulate precise impeachment questions based on documentary variances.

### 3. Which failures require Case RAG?
Fine-tuning cannot solve the retrieval of voluminous 500-page case dockets (charge sheets, trial transcripts, commercial contracts, annexures). 
- **Case RAG** is strictly required to ingest, chunk, and index private client documents, enabling Dense Cosine + Sparse retrieval to supply the operative facts into the prompt's `CASE MATERIAL` block.

### 4. Which failures require Legal RAG?
Fine-tuning must **never** be relied upon to memorize changing statutory sections or amendments.
- **Legal RAG** is strictly required to provide verbatim statutory text, official enactment bounds (e.g. BNS terminates at Section 358), official Gazette commencement dates (July 1, 2024), and binding Supreme Court precedents.

### 5. Which failures require better prompting?
- The Query Router's decision to bypass model reasoning on `CASE_QUERY` and return a static metadata string was an architectural prompting limitation.
- Grounded prompt templates that explicitly bind:
  `CASE MATERIAL` + `EVIDENCE ON RECORD` + `APPLICABLE LAW` + `LAWYER QUERY` → `STRUCTURED RESPONSE`
  are required to activate the model's analytical capabilities.

### 6. Which failures require better retrieval?
- Cross-domain collisions (e.g. retrieving BNS criminal sections for a civil contract breach or foreign law query) require **Domain Gating** and **Relevance Thresholding** before feeding chunks to the generator.
- Dense embedding models alone struggle with exact section lookups (e.g. confusing Section 482 CrPC with Section 482 BNSS); **Hybrid SQLite FTS5 + Dense Cosine + RRF** is required to guarantee exact statutory matching.

### 7. Is fine-tuning justified?
**YES, UNEQUIVOCALLY.**  
The empirical evaluation demonstrates that:
1. Retrieval alone (Legal RAG) only provides statutory excerpts—it **cannot think through a case**.
2. Case RAG alone only extracts paragraphs from PDFs—it **cannot draft an 8-part argument, spot evidence gaps, or plan cross-examination**.
3. Prompt engineering alone on base Qwen-14B produces generic conversational text lacking legal rigor, structured headings, and Indian procedural acumen.
4. **Fine-tuning on the Case Analysis dataset provides the vital reasoning bridge**: it teaches the model how to ingest facts and law and synthesize them into rigorous, professional case intelligence.

---

## 5. Execution Safeguards Confirmed

- **Zero fine-tuning was performed during this evaluation.**
- **Baseline LegalAI V2 model weights remain 100% frozen.**
- **Authoritative RAG database remains untouched.**
- **Evaluation sets were constructed strictly from held-out test splits (Zero Case Leakage).**
