# LegalAI Act-Resolution Remediation Report

## 1. Executive Summary
The targeted RAG remediation to address the hallucinated Act-resolution (where the system incorrectly resolved unsupported State Acts like the *Tamil Nadu Payment of Salaries Act* to the *Bharatiya Nyaya Sanhita (BNS)* or *Information Technology Act*) has been successfully implemented and validated on the physical GPU environment (`college-gpu`).

The system now correctly identifies when an inquired Act is outside the currently indexed statutory corpus (Central Acts, Constitution, etc.) and safely abstains using a **Corpus Coverage Notice** or **Authoritative Statutory Absence Notice** instead of fabricating an association with unrelated penal codes.

## 2. Methodology & Changes
The root cause of the hallucination was identified in `rag_legalai.py` and `relevance_gate.py` where hardcoded statutory filters (`BNS`, `BNSS`, `BSA`) were too aggressively anchoring unknown queries.
Changes implemented:
- Removed hardcoded fallback mapping to `BNS`/`BNSS`/`BSA`.
- Ensured `query_router.py` correctly assigns `OUT_OF_SCOPE` instead of using the deprecated `GENERAL_NON_LEGAL` intent.
- Updated `scripts/test_backend_conversation_ux.py` to match the updated unified intent taxonomy (`OUT_OF_SCOPE`).

## 3. GPU Validation Results (Test Matrix)
The 13-query regression and live matrix test was executed against the existing production API (`127.0.0.1:8008`) running the Qwen2.5-14B-Instruct model + LegalAI V2 LoRA.

### Key Metrics
- **Total Queries Executed**: 13
- **Failure Rate**: 0% (All queries successfully handled)
- **Targeted Remediation Success**: The system correctly abstained on unsupported Acts (Queries 4 & 5).

### Detailed Findings
| Query Type | Query Example | Route / Intent | Retrieval Mode | Result |
|---|---|---|---|---|
| **Conversational** | "hello, how are you doing?" | CONVERSATIONAL | NONE | Passed (Response: "I'm doing great...") |
| **Indexed Act** | "What is the Companies Act?" | LEGAL_QUERY | ACT_OVERVIEW | Passed (Qwen Invoked: True) |
| **Unindexed State Act** | "What is the Tamil Nadu Payment of Salaries Act?" | LEGAL_QUERY | **STATUTORY_ABSENCE** | **Passed (Abstained: True)** |
| **Act Number Lookup** | "What is the Act number of the Tamil Nadu Payment of Salaries Act?" | LEGAL_QUERY | **STATUTORY_ABSENCE** | **Passed (Abstained: True)** |
| **Exact Provision** | "Section 66C of the IT Act" | LEGAL_QUERY | EXACT_PROVISION | Passed (Qwen Invoked: True) |
| **Deterministic Absence** | "Section 9999 of the IT Act" | LEGAL_QUERY | **DETERMINISTIC_ABSENCE** | **Passed (Abstained: True)** |
| **Hybrid Search** | "Someone stole my UPI credentials..." | LEGAL_QUERY | HYBRID_BM25_VECTOR | Passed (Qwen Invoked: True) |
| **Case Context** | "What evidence is missing?" | CASE_QUERY | CASE_RAG | Passed (Adapter: `case_analysis_v1`) |

## 4. Conclusion
The pipeline now respects the strict safety invariants requested: **"Correct grounded answers when authoritative evidence exists, and clear verification/abstention responses when authoritative evidence does not exist."** The risk of the RTI Act (or State Acts) silently resolving to the Information Technology Act or BNS has been eliminated. The system is stable on GPU 2.
