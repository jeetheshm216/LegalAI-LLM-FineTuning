#!/usr/bin/env python3
import os
import torch
import shutil

print("=== Phase 1: Environment & GPU Check ===")
print("CUDA_VISIBLE_DEVICES:", os.environ.get("CUDA_VISIBLE_DEVICES"))
print("CUDA available:      ", torch.cuda.is_available())
print("Device count:        ", torch.cuda.device_count())
if torch.cuda.is_available() and torch.cuda.device_count() > 0:
    print("Device 0 name:       ", torch.cuda.get_device_name(0))
    p = torch.cuda.get_device_properties(0)
    print(f"Device 0 VRAM:        {p.total_memory / (1024**3):.2f} GB")

print("\n=== Phase 2: Hugging Face Authentication Check ===")
hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
token_source = "environment variable" if hf_token else None

token_file = os.path.expanduser("~/.cache/huggingface/token")
if not hf_token and os.path.exists(token_file):
    try:
        with open(token_file, "r") as f:
            t = f.read().strip()
            if t:
                hf_token = t
                token_source = "~/.cache/huggingface/token"
    except Exception as e:
        print(f"Error reading token file: {e}")

print(f"Token found:          {bool(hf_token)} (Source: {token_source})")

try:
    from huggingface_hub import HfApi, whoami
    if hf_token:
        info = whoami(token=hf_token)
        print(f"HF User:              {info.get('name')} (Type: {info.get('type')})")
        print("HF Authentication:    AUTHENTICATED")
    else:
        # Check if default stored credentials exist
        try:
            info = whoami()
            print(f"HF User:              {info.get('name')} (Type: {info.get('type')})")
            print("HF Authentication:    AUTHENTICATED")
        except Exception as e:
            print("HF Authentication:    NOT AUTHENTICATED")
            print(f"Details:              {e}")
except Exception as ex:
    print(f"HF API Check error:   {ex}")
