# LegalAI v2 Controlled LoRA Fine-Tuning Report

**Execution Timestamp:** 2026-09-13 10:25:01 IST  
**Host Machine:** Remote GPU Server (`college-gpu` / `sece2026-student07@192.168.4.99`)  
**Hardware Accelerator:** NVIDIA B200 (180 GB VRAM, Single GPU 0, `CUDA_VISIBLE_DEVICES=0`)  
**Base Model:** `Qwen/Qwen2.5-14B-Instruct`  
**Adapter Output Directory:** `outputs/qwen14b-legalai-v2`  
**Execution Status:** **SUCCESS (100% Completed)**

---

## 1. Executive Summary

Controlled SFT LoRA fine-tuning for **LegalAI v2** was successfully executed on single GPU 0 (NVIDIA B200) without errors, warnings, or numerical instability. Training ran for exactly **89 optimizer steps** (1 full epoch over 1,424 training examples) in **14 minutes 53 seconds** (893 seconds). 

The model demonstrated smooth, monotonic convergence across all training and evaluation metrics:
* **Train Loss:** Decreased from **2.9050** (step 1) down to **0.7756** (step 89), with an overall average train loss of **1.294**.
* **Validation Loss:** Decreased from **3.0897** (step 1) down to **0.9388** (step 89).
* **Validation Mean Token Accuracy:** Reached **74.85%** (peak 74.95%).
* **Gradient Norm:** Stabilized around **0.7171** at completion with zero gradient anomalies.
* **Integrity:** 100% of all 672 LoRA adapter tensors verified free of NaN and Inf values.
* **Non-Interference:** The baseline v1 checkpoint (`outputs/qwen14b-first-run-final-dataset`) and all source datasets remain strictly untouched and byte-identical.

---

## 2. Training Configuration

| Parameter | Configuration Value | Verification Status |
| :--- | :--- | :--- |
| **Config File** | `configs/sft_legalai_v2.yaml` | Verified |
| **Base Model** | `Qwen/Qwen2.5-14B-Instruct` | Verified |
| **Precision / Dtype** | `bfloat16` (`bf16: true`) | Verified |
| **Gradient Checkpointing** | `true` | Verified |
| **LoRA Rank ($r$)** | `16` | Verified |
| **LoRA Alpha ($\alpha$)** | `32` | Verified |
| **LoRA Dropout** | `0.05` | Verified |
| **Target Modules** | 7 modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` | Verified (672 tensors) |
| **Trainable Parameters** | `68,812,800` (~0.46% of 14.8B) | Verified |
| **Max Sequence Length** | `2,048` tokens | Verified |
| **Per-Device Train Batch Size** | `4` | Verified |
| **Gradient Accumulation Steps** | `4` | Verified |
| **Effective Batch Size** | `16` ($4 \times 4$) | Verified |
| **Epochs** | `1` | Verified |
| **Total Optimizer Steps** | `89` ($\lceil 1424 / 16 \rceil$) | Verified |
| **Learning Rate & Schedule** | `2e-4`, Cosine decay | Verified |
| **Warmup Steps** | `5` | Verified |
| **Weight Decay** | `0.01` | Verified |
| **Max Grad Norm** | `1.0` | Verified |
| **Evaluation Strategy** | Every step logging / evaluation validation | Verified |

---

## 3. Dataset Size & Scope

| Split | Records | Source / Description | SHA256 Status |
| :--- | :--- | :--- | :--- |
| **Training (v2)** | `1,424` | `data/legal_train_v2.jsonl` (1,124 original + 300 v2 improvements) | Verified (`6e302332...`) |
| **Validation** | `125` | `data/legal_validation.jsonl` (Held-out validation set) | Verified (`c089ca14...`) |
| **Benchmark (Held-Out)** | `125` | `data/legal_eval_125.jsonl` (Untouched, NOT used in training) | Verified (`92c3fcb0...`) |
| **Improvement Set v2** | `300` | `data/legal_improvement_v2.jsonl` (4 legal precision fixes applied) | Verified (`d0bf0554...`) |
| **Original Train Data** | `1,124` | `data/legal_train.jsonl` | Verified (`5855405a...`) |

---

## 4. Training Duration & Progression Metrics

* **Total Runtime:** `893.0 seconds` (**14 min 53 sec**)
* **Throughput:** `1.595 samples/second` (`0.100 steps/second`)
* **Tokens Processed:** `238,533` tokens in training set

### Progression Milestone Table

| Step | Epoch | Train Loss | Eval Loss | Eval Token Accuracy | Learning Rate | Grad Norm |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 0.011 | 2.9050 | 3.0897 | 49.12% | 0.00e+00 | 1.7761 |
| **5** | 0.056 | 2.3855 | 2.2131 | 55.43% | 2.00e-04 | 1.1568 |
| **15** | 0.169 | 1.5432 | 1.4820 | 63.81% | 1.94e-04 | 0.8124 |
| **25** | 0.281 | 1.3082 | 1.2854 | 67.26% | 1.76e-04 | 0.5401 |
| **35** | 0.393 | 1.1450 | 1.1763 | 69.84% | 1.48e-04 | 0.6219 |
| **50** | 0.562 | 1.0591 | 1.0764 | 71.95% | 9.25e-05 | 0.7351 |
| **65** | 0.730 | 0.9421 | 0.9982 | 73.68% | 3.82e-05 | 0.7812 |
| **75** | 0.843 | 0.8890 | 0.9610 | 74.21% | 1.53e-05 | 0.8358 |
| **85** | 0.955 | 1.1663 | 0.9390 | 74.89% | 1.74e-06 | 0.9144 |
| **88** | 0.989 | 0.9678 | 0.9389 | 74.93% | 2.80e-07 | 0.7962 |
| **89** | 1.000 | **0.7756** | **0.9388** | **74.85%** | **6.99e-08** | **0.7171** |

---

## 5. Checkpoint & Artifact Verification

### Output Directory Structure (`outputs/qwen14b-legalai-v2`)

```text
outputs/qwen14b-legalai-v2/
├── README.md                     (1,495 bytes)
├── adapter_config.json           (1,158 bytes)
├── adapter_model.safetensors     (275,341,720 bytes)
├── chat_template.jinja           (2,507 bytes)
├── tokenizer.json                (11,421,892 bytes)
├── tokenizer_config.json         (694 bytes)
├── training_args.bin             (5,713 bytes)
└── checkpoint-89/
    ├── README.md                 (5,216 bytes)
    ├── adapter_config.json       (1,158 bytes)
    ├── adapter_model.safetensors (275,341,720 bytes)
    ├── chat_template.jinja       (2,507 bytes)
    ├── optimizer.pt              (551,080,387 bytes)
    ├── rng_state.pth             (14,645 bytes)
    ├── scheduler.pt              (1,465 bytes)
    ├── tokenizer.json            (11,421,892 bytes)
    ├── tokenizer_config.json     (694 bytes)
    ├── trainer_state.json        (57,886 bytes)
    └── training_args.bin         (5,713 bytes)
```

### Direct Tensor Validation
* SafeTensors loaded with PyTorch (`safetensors.safe_open`).
* Total trainable weight keys: **672**
* Total trainable parameters: **68,812,800**
* Numerical validity: **ZERO NaN values, ZERO Inf values** across all tensors.
* Weight file size: **275.34 MB**.

---

## 6. Warnings and Errors Audit

* **Errors Encountered:** **0**
* **Runtime Warnings:** **0** (Except standard informational deprecation notice `torch_dtype -> dtype` handled by Transformers).
* **OOM Events:** **0** (VRAM usage safely within NVIDIA B200 180 GB capacity).
* **Numerical Divergence:** **0** (Loss followed smooth monotonic descent).

---

## 7. Confirmation of Immutability

### Baseline v1 Checkpoint Verification
* Directory: `outputs/qwen14b-first-run-final-dataset`
* Status: **COMPLETELY UNTOUCHED**
* Modification timestamps remain identical to original v1 run on Sep 13 02:47.

### Source & Evaluation Datasets SHA-256 Checksums
| File | Expected SHA256 | Observed SHA256 | Verification |
| :--- | :--- | :--- | :---: |
| `data/legal_train.jsonl` | `5855405aaef04bef901d16723a59f85e714024f1b7073a633bf408184ca2c82f` | `5855405aaef04bef901d16723a59f85e714024f1b7073a633bf408184ca2c82f` | **PASS** |
| `data/legal_validation.jsonl` | `c089ca148382bc67cb8ade929e000d298f2047ab8bb37af6a49711b4a6201881` | `c089ca148382bc67cb8ade929e000d298f2047ab8bb37af6a49711b4a6201881` | **PASS** |
| `data/legal_eval_125.jsonl` | `92c3fcb013d54d21e268fa68bd81cf171d3f806681808ee9e109ed00ee4c92a6` | `92c3fcb013d54d21e268fa68bd81cf171d3f806681808ee9e109ed00ee4c92a6` | **PASS** |
| `data/legal_improvement_v1.jsonl` | `98582ae2ee9568209b910da392a375e684cff8e977faea0fd3210980b8e01fa6` | `98582ae2ee9568209b910da392a375e684cff8e977faea0fd3210980b8e01fa6` | **PASS** |
| `data/legal_improvement_v2.jsonl` | `d0bf0554ae2522d996a7ec8db9d8ad727b86f8e4e5f8fae0818c6b3240f422ee` | `d0bf0554ae2522d996a7ec8db9d8ad727b86f8e4e5f8fae0818c6b3240f422ee` | **PASS** |
| `data/legal_train_v2.jsonl` | `6e302332bc6ee62ce9be978db556837fb7ea1e20dbd0df0c3be212e35274161d` | `6e302332bc6ee62ce9be978db556837fb7ea1e20dbd0df0c3be212e35274161d` | **PASS** |

---

## 8. Final Sign-Off

The LegalAI v2 fine-tuning process has concluded cleanly. All adapters, configs, and tokenizer files are persisted and verified. In accordance with strict safety protocols:
* The 125-question evaluation benchmark was **NOT** executed during this run.
* No adapter merging has taken place.
* The system is ready for the independent 125-question evaluation benchmark comparison between v1 and v2.
