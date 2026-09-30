import os
import sys
import time

os.environ["HF_HOME"] = "/data/user/sece2026-student07/.cache/huggingface"

from huggingface_hub import snapshot_download

def main():
    repo_id = "Qwen/Qwen2.5-32B-Instruct"
    print(f"Starting download of {repo_id} to {os.environ['HF_HOME']}...")
    t0 = time.time()
    path = snapshot_download(
        repo_id=repo_id,
        resume_download=True,
        max_workers=8
    )
    elapsed = time.time() - t0
    print(f"Download complete in {elapsed:.1f}s! Path: {path}")

if __name__ == "__main__":
    main()
