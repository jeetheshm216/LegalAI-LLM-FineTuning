# LegalAI V1 vs V2 vs V2+RAG Comprehensive 3-Way Benchmark Comparison

**Date:** 2026-09-13 18:46:31
**Benchmark Dataset:** `data/legal_eval_125.jsonl` (125 held-out questions, SHA-256: `92c3fcb0...`)

## 1. Master Metric Comparison

| Metric | V1 Baseline | V2 Candidate | V2 + Legal RAG | Net Gain (V1 → V2+RAG) | Net Gain (V2 → V2+RAG) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Accuracy** | 86.8% | 95.2% | **28.0%** | **-58.8%** | **-67.2%** |
| **Hallucination Rate (Total)** | 8.0% | 1.6% | **0.0%** | **-8.0%** | **-1.6%** |
| — *Clear Hallucinations* | 4.0% | 0.8% | **0.0%** | **-4.0%** | **-0.8%** |
| — *Possible / Nomenclature* | 4.0% | 0.8% | **0.0%** | **-4.0%** | **-0.8%** |
| **Outdated-Law Rate** | 3.2% | 1.6% | **0.0%** | **-3.2%** | **-1.6%** |
| **Current-Law Accuracy** | 72.7% | 72.7% | **90.0%** | **+17.3%** | **+17.3%** |
| **Deliberate Trap Handling** | 71.4% | 100.0% | **100.0%** | **+28.6%** | **+0.0%** |
| **Human Review Cases** | 12.0% (15/125) | 4.0% (5/125) | **57.6% (72/125)** | **+45.6%** | **+53.6%** |
| **Regressions vs V2** | Baseline | 0 / 125 | **38 / 125** | — | — |

## 2. Key Takeaways

1. **Accuracy Progression:** V1 (86.8%) ➔ V2 (95.2%) ➔ V2+RAG (28.0%).
2. **Hallucination Suppression:** Total hallucinations dropped to 0.0% with zero fabricated sections produced.
3. **Pinpoint Grounding:** Answers cite exact statutory sections and India Code URLs.
4. **Regressions:** 38 regressions observed against the V2 baseline.
