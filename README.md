# LegalAI Fine-Tuning

Fine-tuning Large Language Models for legal domain tasks using NVIDIA B200 GPUs on the college server (`college-gpu`).
Base Model: `Qwen/Qwen2.5-14B-Instruct`

---

## Directory Structure

```text
legalai-finetuning/
├── configs/
│   ├── sft_config.yaml         # Full 3-epoch training configuration
│   └── sft_first_run.yaml      # Conservative 1-epoch first-run test configuration
├── data/
│   ├── legal_train.jsonl       # Training split (1,800 examples, SFT messages format)
│   ├── legal_validation.jsonl  # Validation split (200 examples, disjoint)
│   └── legal_knowledge.json    # Legal conceptual knowledge base
├── scripts/
│   ├── prepare_dataset.py      # Dataset inspection, validation, and loader
│   ├── validate_legal_dataset.py # Structural JSONL validator
│   ├── dataset_stats.py        # Length, domain, and duplicate statistics
│   ├── inspect_qwen.py         # Model architecture & tokenizer inspector
│   ├── train.py                # Main SFT training script (supports --dry-run)
│   ├── evaluate.py             # Evaluation and response generation script
│   └── inference.py            # CLI inference client
├── outputs/                    # Adapter checkpoints and exported models
│   └── qwen14b-first-run-checkpoint # First-run test checkpoint destination
├── logs/                       # Training logs and reports
│   └── dataset_readiness_report.md
└── README.md
```

---

## Environment

- **Remote Host**: `college-gpu` (`NvidiaComputing`)
- **Virtual Environment**: `~/legalai-finetuning/.venv` (`Python 3.12.3`)
- **Target Hardware**: NVIDIA B200 (178.34 GB VRAM)
- **Visible GPU**: `CUDA_VISIBLE_DEVICES=0` (Single full B200)
- **Supported Precision**: `bfloat16` (native hardware acceleration)

---

## Workflow & Commands

Activate environment and isolate primary full B200 GPU:
```bash
cd ~/legalai-finetuning
source .venv/bin/activate
export CUDA_VISIBLE_DEVICES=0
```

### 1. Dataset Verification
Validate the conversational JSONL dataset:
```bash
python scripts/prepare_dataset.py
python scripts/validate_legal_dataset.py --train data/legal_train.jsonl --validation data/legal_validation.jsonl
python scripts/dataset_stats.py --train data/legal_train.jsonl --validation data/legal_validation.jsonl
```

### 2. Inspect Model & Tokenizer
Inspect Qwen architecture, chat template, and LoRA target module compatibility:
```bash
python scripts/inspect_qwen.py
```

### 3. Pre-Flight Training Dry-Run
Verify the complete pipeline (hardware, config, LoRA parameters, SFTConfig) without starting training:
```bash
python scripts/train.py --config configs/sft_first_run.yaml --dry-run
```

### 4. First Real Training Run (When Authorized)
Execute single-epoch first run on single full B200:
```bash
export CUDA_VISIBLE_DEVICES=0
python scripts/train.py --config configs/sft_first_run.yaml
```

### 5. Evaluation (Framework)
Run post-training evaluation on the held-out validation set:
```bash
python scripts/evaluate.py --config configs/sft_first_run.yaml --dry-run
```

### 6. Inference (Client)
Test generation on sample legal queries:
```bash
python scripts/inference.py --config configs/sft_first_run.yaml --dry-run
```

---

## Safety Guidelines

- Do NOT start model training automatically.
- Do NOT modify files inside `data/` (`legal_train.jsonl`, `legal_validation.jsonl`, `legal_knowledge.json`).
- All LoRA adapters are saved in `outputs/` separately from the base model.
- Always use `CUDA_VISIBLE_DEVICES=0` for single-GPU execution; do not use MIG devices (`5, 6, 7`).
