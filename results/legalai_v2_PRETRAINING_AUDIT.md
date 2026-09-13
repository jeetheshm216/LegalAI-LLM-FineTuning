# LegalAI v2 — Pre-Training Preparation & Dataset Audit Report

**Date:** 13 September 2026  
**Project:** `/home/sece2026-student07/legalai-finetuning`  
**Target Output Checkpoint:** `outputs/qwen14b-legalai-v2`  
**Audit Status:** COMPLETE — PRE-CONDITIONS MET FOR CONTROLLED V2 TRAINING  

---

## 1. Executive Summary

The preparation of the **LegalAI v2** training dataset and configuration has been completed in strict accordance with the project safety rules. 

The v2 training dataset merges the clean original training dataset (`data/legal_train.jsonl`, 1,124 records) with the newly refined targeted improvement dataset (`data/legal_improvement_v2.jsonl`, 300 records) to form `data/legal_train_v2.jsonl` (**1,424 records**). 

Only the **four documented advocate-oriented precision corrections** identified in `results/legal_improvement_v1_CONTENT_AUDIT.md` were applied. Zero original datasets or checkpoints were modified, zero records leaked into or from the evaluation benchmark (`data/legal_eval_125.jsonl`), and a complete pre-flight dry-run on NVIDIA B200 (GPU 0) confirmed 100% readiness without executing training.

---

## 2. Dataset Composition & Record Counts

| Dataset File | Role | Records | Format / Schema | Status |
| :--- | :--- | :---: | :--- | :---: |
| `data/legal_train.jsonl` | Original SFT Training Base | 1,124 | `messages: [user, assistant]` | **UNMODIFIED** |
| `data/legal_improvement_v1.jsonl` | Baseline Improvement Set | 300 | `messages: [user, assistant]` | **UNMODIFIED** |
| `data/legal_improvement_v2.jsonl` | Corrected Improvement Set | 300 | `messages: [user, assistant]` | **NEW (4 Minor Fixes Applied)** |
| `data/legal_train_v2.jsonl` | Combined v2 Training Dataset | **1,424** | `messages: [user, assistant]` | **NEW (1,124 + 300)** |
| `data/legal_validation.jsonl` | Validation Dataset | 125 | `messages: [user, assistant]` | **UNMODIFIED / HELD OUT** |
| `data/legal_eval_125.jsonl` | Independent Benchmark | 125 | Benchmark JSONL | **UNMODIFIED / HELD OUT** |

### Group Breakdown of Improvement Records (300 total):
- **Group A (BNS / BNSS / BSA Distinction):** 60 records (20.0%)
- **Group B (1 July 2024 Legal Transition):** 60 records (20.0%)
- **Group C (Hallucination Resistance & Verification):** 50 records (16.7%)
- **Group D (False-Premise Detection & Rectification):** 40 records (13.3%)
- **Group E (Correct Act / Specialized Provision Selection):** 50 records (16.7%)
- **Group F (Evidence Law Transition - BSA vs IEA):** 20 records (6.7%)
- **Group G (Cyber-Law Distinction - IT Act Differentiation):** 20 records (6.7%)

---

## 3. Four Documented Precision Corrections Applied

In `data/legal_improvement_v2.jsonl`, all 296 PASS records from v1 were preserved exactly without modification. Only the four MINOR_FIX records documented in the content audit were updated with advocate-oriented precision enhancements:

1. **Record 17 (Group A — 24-Hour Magistrate Production):**
   - *Question:* Which enactment requires that an arrested individual be produced before a judicial magistrate within 24 hours?
   - *Enhancement:* Explicitly cited **Section 58 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)** (replacing Section 57 CrPC) alongside Article 22(2) of the Constitution.
2. **Record 48 (Group A — Maintenance Provisions):**
   - *Question:* Which code provides the summary procedure for claiming maintenance by wives, children, and parents under general procedural law?
   - *Enhancement:* Explicitly cited **Section 144 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)** (replacing Section 125 CrPC).
3. **Record 96 (Group B — Anticipatory Bail in Transition):**
   - *Question:* An anticipatory bail application is filed on 10 July 2024 in relation to an FIR lodged in June 2024 under the IPC. Which procedural provision is invoked?
   - *Enhancement:* Added clear parenthetical warning clarifying that **Section 482 BNSS** corresponds to old Section 438 CrPC (anticipatory bail) and must not be confused with old Section 482 CrPC (inherent powers, now Section 528 BNSS).
4. **Record 236 (Group E — Setting Aside Arbitral Awards):**
   - *Question:* An aggrieved party claims that an arbitral tribunal exceeded its jurisdiction and made an order without hearing them. Which statute and section provide for setting aside the award?
   - *Enhancement:* Added **Section 34(2A)** of the Arbitration and Conciliation Act, 1996 to reflect the 'patent illegality' ground available for domestic arbitrations.

---

## 4. Integrity, Overlap, and Collision Verification

Rigorous automated checks were conducted across all 1,424 records of `data/legal_train_v2.jsonl`:

- **Internal Duplicate Questions:** **0** (All 1,424 questions are unique).
- **Exact Duplicate Records:** **0**.
- **Overlap with Validation Set (`data/legal_validation.jsonl`):** **0** (Zero leakage).
- **Overlap with Benchmark (`data/legal_eval_125.jsonl`):** **0** (Zero leakage).
- **Overlap between Train v1 and Improvement v2:** **0**.
- **Text Length Statistics:**
  - Question Length: Min = 7 words, Max = 50 words, Average = **21.7 words**.
  - Answer Length: Min = 14 words, Max = 235 words, Average = **81.4 words**.

---

## 5. Cryptographic Verification of Hashes

All file hashes were verified using SHA256 before and after dataset creation:

```text
====================================================================================================
FILE INTEGRITY CHECKSUM REGISTER (SHA256)
====================================================================================================
data/legal_train.jsonl          5855405aaef04bef901d16723a59f85e714024f1b7073a633bf408184ca2c82f  [PASS - UNMODIFIED]
data/legal_validation.jsonl     c089ca148382bc67cb8ade929e000d298f2047ab8bb37af6a49711b4a6201881  [PASS - UNMODIFIED]
data/legal_eval_125.jsonl       92c3fcb013d54d21e268fa68bd81cf171d3f806681808ee9e109ed00ee4c92a6  [PASS - UNMODIFIED]
data/legal_improvement_v1.jsonl 98582ae2ee9568209b910da392a375e684cff8e977faea0fd3210980b8e01fa6  [PASS - UNMODIFIED]
data/legal_improvement_v2.jsonl d0bf0554ae2522d996a7ec8db9d8ad727b86f8e4e5f8fae0818c6b3240f422ee  [PASS - VERIFIED]
data/legal_train_v2.jsonl       6e302332bc6ee62ce9be978db556837fb7ea1e20dbd0df0c3be212e35274161d  [PASS - VERIFIED]
====================================================================================================
```

---

## 6. Training Configuration (`configs/sft_legalai_v2.yaml`)

The training configuration adheres strictly to the controlled single-epoch philosophy of the successful v1 run:

```yaml
model:
  model_name_or_path: "Qwen/Qwen2.5-14B-Instruct"
  trust_remote_code: false
  torch_dtype: "bfloat16"
  use_cache: false

data:
  train_file: "data/legal_train_v2.jsonl"
  validation_file: "data/legal_validation.jsonl"
  max_seq_length: 2048

lora:
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  target_modules:
    - "q_proj"
    - "k_proj"
    - "v_proj"
    - "o_proj"
    - "gate_proj"
    - "up_proj"
    - "down_proj"
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  output_dir: "outputs/qwen14b-legalai-v2"
  num_train_epochs: 1
  per_device_train_batch_size: 4
  per_device_eval_batch_size: 4
  gradient_accumulation_steps: 4
  learning_rate: 0.0002
  lr_scheduler_type: "cosine"
  warmup_steps: 5
  weight_decay: 0.01
  max_grad_norm: 1.0
  logging_steps: 1
  save_strategy: "steps"
  save_steps: 50
  save_total_limit: 1
  eval_strategy: "steps"
  eval_steps: 50
  load_best_model_at_end: false
  seed: 42

hardware:
  bf16: true
  fp16: false
  gradient_checkpointing: true
  dataloader_num_workers: 2

logging:
  logging_steps: 1
  report_to: "none"
```

---

## 7. Expected Training Progression & Optimizer Steps

- **Total Training Examples:** 1,424
- **Per-Device Train Batch Size:** 4
- **Gradient Accumulation Steps:** 4
- **Effective Batch Size:** 16 (4 × 4 × 1 GPU)
- **Epochs:** 1.0
- **Total Optimizer Update Steps:**  
  $$	ext{Steps} = rac{1,424}{16} = 89 	ext{ update steps}$$
- **Evaluation Points:** Evaluated on 125 validation examples at Step 50 and at completion (Step 89).
- **Checkpoints:** Intermediate checkpoint at Step 50; final checkpoint saved at Step 89 in `outputs/qwen14b-legalai-v2`.
- **Existing Checkpoint Protection:** `outputs/qwen14b-first-run-final-dataset` remains completely untouched and isolated.

---

## 8. Dry-Run Verification Result

The training harness was executed in dry-run mode (`python scripts/train.py --config configs/sft_legalai_v2.yaml --dry-run` on GPU 0):

```text
[INFO] STARTING LEGALAI SFT PRE-FLIGHT DRY-RUN VERIFICATION
[INFO] [1/7] Hardware: NVIDIA B200 (BF16 enabled) on CUDA_VISIBLE_DEVICES=0
[INFO] [2/7] Configuration: Qwen/Qwen2.5-14B-Instruct, context=2048, output=outputs/qwen14b-legalai-v2
[INFO] [3/7] Tokenizer: Qwen2Tokenizer, EOS=<|im_end|>, PAD=<|endoftext|>, chat template confirmed
[INFO] [4/7] Datasets: Train=1424 records, Validation=125 records, formatting verified
[INFO] [5/7] LoRA: r=16, alpha=32, 7 target modules verified (68,812,800 trainable parameters)
[INFO] [6/7] TRL SFTConfig built successfully
[INFO] [7/7] Pipeline purity verified (confirmed Qwen2.5 architecture)
[INFO] DRY-RUN VERIFICATION SUCCESSFUL — ALL PRE-CONDITIONS MET
[INFO] No base model weights were downloaded and no training was executed.
```

---

## 9. Final Checklist Confirmation

- [x] `outputs/qwen14b-first-run-final-dataset` is UNTOUCHED.
- [x] `data/legal_eval_125.jsonl` benchmark is UNTOUCHED.
- [x] `data/legal_train.jsonl` and `data/legal_validation.jsonl` are UNTOUCHED.
- [x] Zero training was performed during this preparation phase.
- [x] All pre-conditions are met for launching the controlled v2 fine-tuning run whenever authorized.
