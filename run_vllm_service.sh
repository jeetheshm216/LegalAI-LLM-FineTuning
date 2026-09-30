#!/bin/bash
export PATH="/home/sece2026-student07/legalai-finetuning/.venv/bin:/opt/llm-training/bin:$PATH"
export CUDA_VISIBLE_DEVICES=2
export HF_HOME="/data/user/sece2026-student07/.cache/huggingface"

cd /home/sece2026-student07/legalai-finetuning

exec .venv/bin/python3 -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-32B-Instruct \
    --served-model-name Qwen/Qwen2.5-32B-Instruct legalai case_analysis \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.55 \
    --tensor-parallel-size 1 \
    --dtype bfloat16 \
    --trust-remote-code \
    --host 127.0.0.1 \
    --port 8009 \
    --disable-log-stats
