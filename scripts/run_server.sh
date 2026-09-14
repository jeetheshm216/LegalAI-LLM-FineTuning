#!/usr/bin/env bash
# scripts/run_server.sh
# Launches LegalAI FastAPI backend on DGX server using Physical GPU 2 (B200)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
cd "$REPO_DIR"

export CUDA_VISIBLE_DEVICES=2
export PYTHONUNBUFFERED=1

echo "=========================================================="
echo "Starting LegalAI Backend on Physical GPU 2 (B200)"
echo "Host Port: 8008"
echo "Working Directory: $REPO_DIR"
echo "=========================================================="

exec "$REPO_DIR/.venv/bin/python3" -m uvicorn src.api.server:app --host 0.0.0.0 --port 8008 --log-level info
