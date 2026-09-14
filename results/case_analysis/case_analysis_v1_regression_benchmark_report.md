# Case Analysis V1: 125-Question Production Regression Benchmark Report

**Execution Timestamp:** 2026-09-14 18:01:09
**Host / Device:** Single Physical GPU 2 (NVIDIA B200, `CUDA_VISIBLE_DEVICES=2`)
**Base Model:** `Qwen/Qwen2.5-14B-Instruct`
**LoRA Adapter:** `outputs/qwen14b-case-analysis-v1`
**RAG Database:** `data/legalai_rag_mvp.db` (1,059 sections, 1,089 chunks)
**Benchmark Dataset:** `data/legal_eval_125.jsonl` (125 held-out questions)

## 1. Executive Summary & Regression Analysis

| Metric | LegalAI V2 (Baseline) | Case Analysis V1 | Delta | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Effective System Accuracy** | 90.4% | **70.8%** | -19.6% | REGRESSION |
| **In-Corpus Statutory Accuracy** | 88.0% | **67.9%** | -20.1% | REGRESSION |
| **Justified Abstentions** | 50/125 (40.0%) | **44/125 (35.2%)** | -4.8% | STABLE |
| **Wrong-Domain Citations** | 2/125 (1.6%) | **6/125 (4.8%)** | +3.2% | FAIL |
| **Hallucination Rate** | 0.0% | **0.0%** | 0.0% | PASS |
| **Temporal Error Rate** | 0.0% | **0.0%** | 0.0% | PASS |
| **Deliberate Trap Handling** | 100.0% | **100.0%** | 0.0% | PASS |
| **Cases Requiring Human Review** | 24/125 (19.2%) | **20/125 (16.0%)** | -3.2% | ACCEPTABLE |

## 2. Nine-Class Legal Performance Breakdown

| Classification Category | Count | Percentage | Legal Assessment |
| :--- | :---: | :---: | :--- |
| **CORRECT** | 28 | 22.4% | Grounded substantive match with complete statutory precision |
| **PARTIALLY_CORRECT** | 33 | 26.4% | Substantively sound with minor omissions |
| **JUSTIFIED_ABSTENTION** | 44 | 35.2% | High-fidelity refusal due to statute outside 3-Act corpus |
| **INCORRECT** | 14 | 11.2% | Fails substantive legal test without hallucinating |
| **HALLUCINATION** | 0 | 0.0% | Fabricated provisions, fake cases, or invented citations |
| **WRONG_DOMAIN_RETRIEVAL** | 6 | 4.8% | Inappropriately cited BNS/BNSS for non-criminal queries |
| **OUTDATED_LAW** | 0 | 0.0% | Relied on repealed law without noting 2024 transition |
| **TEMPORAL_ERROR** | 0 | 0.0% | Applied BNS retroactively to pre-July 1, 2024 acts |
| **CITATION_ERROR** | 0 | 0.0% | Cited provision unsupported by retrieved context |

