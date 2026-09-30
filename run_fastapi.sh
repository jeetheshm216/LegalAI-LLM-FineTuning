#!/bin/bash
set -e
cd /home/sece2026-student07/legalai-finetuning
export CUDA_VISIBLE_DEVICES=2
export PYTHONUNBUFFERED=1
source .venv/bin/activate
exec python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port 8008 --log-level info
