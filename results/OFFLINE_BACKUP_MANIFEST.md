# LegalAI Offline Backup Manifest

**Location on Windows Host**: `C:\Users\Jeethesh M\Documents\Projects\LegalAI_Offline_Backup`  
**Purpose**: Secure offline preservation of fine-tuned model weights, pre-compiled vector databases, raw legal sources, and case analysis datasets that are excluded from GitHub.  
**Last Verified Date**: 2026-09-14  

---

## Recommended Directory Structure

```text
C:\Users\Jeethesh M\Documents\Projects\LegalAI_Offline_Backup\
├── Case_Analysis_V1_LoRA_Adapter/
│   ├── README.md
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   ├── chat_template.jinja
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── training_args.bin
├── Case_Documents/
│   └── case-01/
│       └── test_charterparty_contract.pdf
├── Evaluation_Artifacts/
│   ├── baseline_v2_case_analysis_report.md
│   ├── case_analysis_generation_report.md
│   ├── case_analysis_v1_experiment_report.md
│   ├── case_analysis_v1_metrics.json
│   ├── case_analysis_v1_regression_benchmark_report.md
│   ├── case_analysis_v1_regression_human_review.md
│   └── case_analysis_v1_regression_results.csv
├── Important_Datasets/
│   ├── case_analysis_master.jsonl
│   ├── case_analysis_test.jsonl
│   ├── case_analysis_train.jsonl
│   ├── case_analysis_validation.jsonl
│   └── eval_sets/
│       ├── eval_set_01_bail_cancellation_procedural_irregularity.jsonl
│       ├── eval_set_02_quashing_482_commercial_civil_dispute.jsonl
│       ├── eval_set_03_default_bail_167_incomplete_chargesheet.jsonl
│       ├── eval_set_04_cheque_bounce_138_statutory_notice_delay.jsonl
│       ├── eval_set_05_anticipatory_bail_economic_offence_pmla.jsonl
│       ├── eval_set_06_cross_examination_electronic_evidence_65b.jsonl
│       ├── eval_set_07_recovery_memo_section_27_police_custody.jsonl
│       ├── eval_set_08_circumstantial_evidence_last_seen_theory.jsonl
│       ├── eval_set_09_medical_negligence_expert_opinion_standard.jsonl
│       ├── eval_set_10_arbitration_section_9_interim_relief.jsonl
│       ├── eval_set_11_specific_performance_readiness_willingness.jsonl
│       ├── eval_set_12_consumer_deficiency_service_limitation.jsonl
│       ├── eval_set_13_domestic_violence_shared_household_residence.jsonl
│       ├── eval_set_14_motor_accident_compensation_income_proof.jsonl
│       ├── eval_set_15_contempt_court_willful_disobedience_orders.jsonl
│       ├── eval_set_16_trademark_infringement_deceptive_similarity.jsonl
│       ├── eval_set_17_insolvency_section_7_financial_debt_default.jsonl
│       └── eval_set_18_juvenile_justice_age_determination_claim.jsonl
├── Legal_Source_PDFs/
│   ├── BNSS_2023_Act_46.pdf
│   ├── BNSS_2023_Act_46.pdf.meta.json
│   ├── BNS_2023_Act_45.pdf
│   ├── BNS_2023_Act_45.pdf.meta.json
│   ├── BSA_2023_Act_47.pdf
│   └── BSA_2023_Act_47.pdf.meta.json
├── RAG_Database/
│   ├── legalai_rag_mvp.db
│   ├── legalai_rag_mvp.db-shm
│   └── legalai_rag_mvp.db-wal
├── Recovery_Documentation/
│   ├── OFFLINE_BACKUP_MANIFEST.md
│   ├── PROJECT_RECOVERY_MANIFEST.md
│   ├── RAG_ARCHITECTURE.md
│   ├── RAG_DATA_SCHEMA.md
│   ├── legal_sources_manifest.json
│   ├── sft_case_analysis_v1.yaml
│   └── sft_legalai_v2.yaml
├── V1_LoRA_Optional/
│   ├── README.md
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   ├── chat_template.jinja
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── training_args.bin
├── V2_LoRA_Adapter/
│   ├── README.md
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   ├── chat_template.jinja
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── training_args.bin
├── README.txt
└── SHA256SUMS.txt
```

---

## Existing vs New/Changed Backup Components

| Directory | Status | Notes |
| :--- | :--- | :--- |
| `V2_LoRA_Adapter/` | **EXISTING & VERIFIED** | SHA256 hash verified identical to server |
| `RAG_Database/` | **EXISTING & VERIFIED** | SQLite database hash verified identical |
| `Legal_Source_PDFs/` | **EXISTING & VERIFIED** | Gazette PDFs and metadata verified |
| `V1_LoRA_Optional/` | **EXISTING & VERIFIED** | Initial baseline adapter preserved |
| `Case_Analysis_V1_LoRA_Adapter/` | **NEW TO ADD** | Fine-tuned adapter for procedural case analysis (~274 MB) |
| `Important_Datasets/` | **NEW TO ADD** | Case analysis train/val/test splits + 18 probe sets |
| `Evaluation_Artifacts/` | **NEW TO ADD** | Comprehensive benchmark reports and metrics |
| `Case_Documents/` | **NEW TO ADD** | Case document storage template |
| `Recovery_Documentation/` | **UPDATED** | Enhanced with Case Analysis architecture & recovery steps |
| `SHA256SUMS.txt` | **UPDATED** | Appended with hashes of all newly added artifacts |

---

## Verified SHA256 Checksums for Critical Artifacts

```text
# V2 Statutory LoRA Adapter
cbc87e7778f9cc09afe166f548dfe1733a95067ee3c4910a3d8376a9e82f9375  V2_LoRA_Adapter/adapter_model.safetensors
fd125ec5ce4554da4fe271fc50a38f2948d681a06e4f193d934ff419ec99e2e4  V2_LoRA_Adapter/adapter_config.json
cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f  V2_LoRA_Adapter/chat_template.jinja
3fd169731d2cbde95e10bf356d66d5997fd885dd8dbb6fb4684da3f23b2585d8  V2_LoRA_Adapter/tokenizer.json
04b1682c59acbd057f4c9072297faa73d56fc9de053094c659cdb4c464f58f86  V2_LoRA_Adapter/tokenizer_config.json

# Case Analysis V1 LoRA Adapter (NEW)
86871760b951c1cfd7d087b1f1a816fbe622f700d7682e3b321f5f980f04ef2d  Case_Analysis_V1_LoRA_Adapter/adapter_model.safetensors
b66f7c6b320c73e0170a0c26e0498e0d9794d1376f778d07d86127eb2094a23e  Case_Analysis_V1_LoRA_Adapter/adapter_config.json
cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f  Case_Analysis_V1_LoRA_Adapter/chat_template.jinja
3fd169731d2cbde95e10bf356d66d5997fd885dd8dbb6fb4684da3f23b2585d8  Case_Analysis_V1_LoRA_Adapter/tokenizer.json
04b1682c59acbd057f4c9072297faa73d56fc9de053094c659cdb4c464f58f86  Case_Analysis_V1_LoRA_Adapter/tokenizer_config.json

# Production RAG Vector Database
f7bdf27ee5fe32cc09b851693066e9d4fa0d27b40e82b9beb11697b6fd786aff  RAG_Database/legalai_rag_mvp.db

# Official Gazette Source PDFs
d4449e9995b21fd52627811d08f9d21feda6a3678b7e5355b651242d152167f5  Legal_Source_PDFs/BNS_2023_Act_45.pdf
572c79880b9f8effc8fa6e39b864101835a0fb5d85b194b90a99d170121a0562  Legal_Source_PDFs/BNSS_2023_Act_46.pdf
554b2b4ae3d9f09bf31e6e1ba2b2cb8a4e7f4f5ffd6f3156736752cbbce116d5  Legal_Source_PDFs/BSA_2023_Act_47.pdf
```
