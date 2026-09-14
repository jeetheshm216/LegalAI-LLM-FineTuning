# LegalAI Project Recovery Manifest & Comprehensive Preservation Guide

**Project Name**: LegalAI (Intelligent Legal Reasoning & Retrieval Platform)  
**GitHub Repository**: [https://github.com/jeetheshm216/LegalAI-LLM-FineTuning.git](https://github.com/jeetheshm216/LegalAI-LLM-FineTuning.git)  
**Main Branch**: `main`  
**Current Project Commit**: `587bb8284e817516bc9f21926e8e3d5b2524bd9b` (prior to synchronization commit)  
**Primary Environment**: Linux x86_64, 8x NVIDIA B200 178GB GPU (`sece2026-student07@NvidiaComputing`)  
**Offline Preservation Storage**: `C:\Users\Jeethesh M\Documents\Projects\LegalAI_Offline_Backup`  

---

## 1. Executive Summary & Architecture Overview

LegalAI is an enterprise-grade legal reasoning and document management system built specifically for the new Indian Criminal Code and procedural reforms:
- **Statutory Framework**: Bharatiya Nyaya Sanhita 2023 (BNS), Bharatiya Nagarik Suraksha Sanhita 2023 (BNSS), and Bharatiya Sakshya Adhiniyam 2023 (BSA).
- **Core Intelligence Engine**:
  1. **Base Model**: `Qwen/Qwen2.5-14B-Instruct` (14.7B parameters, 128k context window).
  2. **Statutory Reasoning Adapter (V2 LoRA)**: `outputs/qwen14b-legalai-v2/` trained on 1,152 curated legal examples across IPC-BNS concordance, criminal procedures, and evidence rules.
  3. **Case Analysis & Advisory Adapter (V1 LoRA)**: `outputs/qwen14b-case-analysis-v1/` trained on 1,448 procedural case analysis records across 20 distinct legal domains.
  4. **Query Router**: Dynamic intent classification and context builder (`src/api/query_router.py`) directing queries between Conversational, Statutory RAG, Case Analysis, and Hybrid pipelines.
  5. **Deterministic & Semantic Legal RAG**: SQLite + FTS5 full-text search + `BAAI/bge-large-en-v1.5` dense embeddings (1,089 chunks) with strict concordance verification and temporal guardrails (`src/rag/`).
  6. **Chambers Management Workspace**: Modern React 18 / Vite frontend (`frontend/`) featuring Document Drafting Studio, Case Manager, Client CRM, and Chambers Billing & Ledger.

---

## 2. Model & Artifact Locations

| Component | In-Project / Server Path | Offline Backup Directory | GitHub Status |
| :--- | :--- | :--- | :--- |
| **Base Foundation Model** | `Qwen/Qwen2.5-14B-Instruct` | Downloadable from Hugging Face | Excluded (Hugging Face) |
| **Statutory V2 LoRA Adapter** | `outputs/qwen14b-legalai-v2/` | `LegalAI_Offline_Backup/V2_LoRA_Adapter/` | Excluded (`*.safetensors`) |
| **Case Analysis V1 LoRA Adapter** | `outputs/qwen14b-case-analysis-v1/` | `LegalAI_Offline_Backup/Case_Analysis_V1_LoRA_Adapter/` | Excluded (`*.safetensors`) |
| **Production RAG Database** | `data/legalai_rag_mvp.db` | `LegalAI_Offline_Backup/RAG_Database/` | Excluded (`*.db`) |
| **Raw Legal Source PDFs** | `data/raw/` | `LegalAI_Offline_Backup/Legal_Source_PDFs/` | Excluded (`data/raw/`) |
| **Case Dossiers & Documents** | `data/case_documents/` | `LegalAI_Offline_Backup/Case_Documents/` | Excluded (`data/case_documents/`) |
| **Case Analysis Datasets** | `data/case_analysis/` | `LegalAI_Offline_Backup/Important_Datasets/` | Excluded (`data/case_analysis/`) |
| **125-Question Benchmark Suite** | `data/legal_eval_125.jsonl` | Committed to GitHub & Offline Backup | **Committed to GitHub** |
| **V2 Fine-Tuning Dataset** | `data/legal_train_v2.jsonl` | Committed to GitHub & Offline Backup | **Committed to GitHub** |
| **Statutory Knowledge Reference** | `data/legal_knowledge.json` | Committed to GitHub | **Committed to GitHub** |
| **Processed Normalized Text** | `data/processed/*.txt` | Committed to GitHub | **Committed to GitHub** |
| **Source Provenance Manifest** | `data/sources/legal_sources_manifest.json` | Committed to GitHub | **Committed to GitHub** |
| **Evaluation Reports & CSVs** | `results/` & `results/case_analysis/` | Committed to GitHub & Offline Backup | **Committed to GitHub** |
| **All Source Code & Tests** | `src/`, `frontend/`, `scripts/`, `tests/` | Committed to GitHub | **Committed to GitHub** |
| **Configuration Files** | `configs/*.yaml`, `frontend/vite.config.js` | Committed to GitHub | **Committed to GitHub** |

---

## 3. Preservation & Boundary Rules

### What is Preserved in GitHub:
- All application source code (FastAPI backend, React frontend, RAG pipeline, Query Router).
- All evaluation, training, data processing, and validation scripts.
- All test suites (unit, integration, regression, stability).
- All configuration YAML files and build definitions.
- Comprehensive evaluation reports, CSV summaries, metrics JSON files, and architecture documentation.
- Non-sensitive, public statutory reference datasets (`legal_train_v2.jsonl`, `legal_eval_125.jsonl`).

### What is Excluded from GitHub (Preserved in Offline Backup):
1. **LoRA Model Weights**: `adapter_model.safetensors` (~263 MB per adapter) and training checkpoints.
2. **Pre-compiled Databases**: `legalai_rag_mvp.db` (~14.3 MB) and temporary SQLite write-ahead logs (`*.db-wal`, `*.db-shm`).
3. **Official Gazette PDFs**: `BNS_2023_Act_45.pdf`, `BNSS_2023_Act_46.pdf`, `BSA_2023_Act_47.pdf` (~4.6 MB total).
4. **Client & Case Documents**: Uploaded user briefs and case materials in `data/case_documents/`.
5. **Heavy Generated Datasets**: `data/case_analysis/` (~387 MB total) containing master query corpora, intermediate validation dumps, and large JSONLs.
6. **Execution Environments**: `.venv/` (~18.2 GB), `node_modules/` (~120 MB), and Hugging Face model caches.

---

## 4. Step-by-Step Restoration Guide

### Prerequisites
- **Git**: Installed and authenticated.
- **Python**: Version `3.10` to `3.12` with `pip` and `venv`.
- **Node.js**: Version `18.x` or `20.x` with `npm`.
- **Hardware Options**:
  - **Full Local GPU Inference**: NVIDIA GPU with >= 16 GB VRAM (for 4-bit/8-bit LoRA inference) or >= 32 GB VRAM (bfloat16).
  - **CPU-Only / Hybrid RAG**: Standard laptop CPU runs the RAG retrieval pipeline (< 15 ms latency) paired with an external LLM API (e.g., Groq API).

### Step 1: Clone Repository
```bash
git clone https://github.com/jeetheshm216/LegalAI-LLM-FineTuning.git
cd LegalAI-LLM-FineTuning
```

### Step 2: Restore Offline Assets from Local Windows Backup
Copy the preserved offline assets into their respective locations in the repository:
```powershell
# In Windows PowerShell:
$BACKUP_DIR = "C:\Users\Jeethesh M\Documents\Projects\LegalAI_Offline_Backup"
$REPO_DIR = Get-Location

# 1. Restore V2 Adapter
New-Item -ItemType Directory -Force -Path "$REPO_DIR\outputs\qwen14b-legalai-v2"
Copy-Item -Path "$BACKUP_DIR\V2_LoRA_Adapter\*" -Destination "$REPO_DIR\outputs\qwen14b-legalai-v2\" -Recurse

# 2. Restore Case Analysis V1 Adapter
New-Item -ItemType Directory -Force -Path "$REPO_DIR\outputs\qwen14b-case-analysis-v1"
Copy-Item -Path "$BACKUP_DIR\Case_Analysis_V1_LoRA_Adapter\*" -Destination "$REPO_DIR\outputs\qwen14b-case-analysis-v1\" -Recurse

# 3. Restore RAG Vector Database
New-Item -ItemType Directory -Force -Path "$REPO_DIR\data"
Copy-Item -Path "$BACKUP_DIR\RAG_Database\legalai_rag_mvp.db" -Destination "$REPO_DIR\data\"

# 4. Restore Raw Gazette PDFs
New-Item -ItemType Directory -Force -Path "$REPO_DIR\data\raw"
Copy-Item -Path "$BACKUP_DIR\Legal_Source_PDFs\*" -Destination "$REPO_DIR\data\raw\" -Recurse

# 5. Restore Case Datasets
New-Item -ItemType Directory -Force -Path "$REPO_DIR\data\case_analysis"
Copy-Item -Path "$BACKUP_DIR\Important_Datasets\*" -Destination "$REPO_DIR\data\case_analysis\" -Recurse
```

### Step 3: Verify Checksums
Verify that all restored binary assets match the verified SHA256 checksums:
```powershell
Get-FileHash -Algorithm SHA256 "$REPO_DIR\outputs\qwen14b-legalai-v2\adapter_model.safetensors"
# Expected: cbc87e7778f9cc09afe166f548dfe1733a95067ee3c4910a3d8376a9e82f9375

Get-FileHash -Algorithm SHA256 "$REPO_DIR\outputs\qwen14b-case-analysis-v1\adapter_model.safetensors"
# Expected: 86871760b951c1cfd7d087b1f1a816fbe622f700d7682e3b321f5f980f04ef2d

Get-FileHash -Algorithm SHA256 "$REPO_DIR\data\legalai_rag_mvp.db"
# Expected: f7bdf27ee5fe32cc09b851693066e9d4fa0d27b40e82b9beb11697b6fd786aff
```

### Step 4: Python Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\Activate.ps1 on Windows
pip install --upgrade pip
pip install torch transformers peft accelerate sentence-transformers bitsandbytes pypdf fastapi uvicorn pydantic
```

### Step 5: Frontend Setup
```bash
cd frontend
npm install
npm run build   # Or npm run dev for local development
```

### Step 6: Running the Application
```bash
# Launch FastAPI Backend
uvicorn src.api.server:app --host 0.0.0.0 --port 8008

# Launch Frontend (in another terminal)
cd frontend
npm run dev
```

---

## 5. Software & Hardware Specifications

- **Python Version**: `3.12.3` (tested compatible with 3.10-3.12)
- **Node.js**: `>= 18.19.0` | **npm**: `>= 9.2.0`
- **Key Python Dependencies**:
  - `torch==2.11.0`
  - `transformers==5.16.1`
  - `peft==0.20.0`
  - `sentence-transformers==6.0.1`
  - `fastapi==0.115.0`
  - `uvicorn==0.34.0`
- **GPU Inference Memory Footprint**:
  - `Qwen/Qwen2.5-14B-Instruct` + LoRA Adapter:
    - In `bfloat16`: ~31 GB VRAM
    - In `8-bit` (bitsandbytes): ~17 GB VRAM
    - In `4-bit` (bitsandbytes NF4): ~10.5 GB VRAM
