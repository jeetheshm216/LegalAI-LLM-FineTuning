import sys
import os
import subprocess

print("=== PYTHON ENVIRONMENT ===")
print("Python:", sys.version)
print("Executable:", sys.executable)

packages = [
    'fitz', 'pymupdf', 'pdfplumber', 'psycopg2', 'asyncpg', 'pgvector',
    'sentence_transformers', 'torch', 'transformers', 'sqlite3', 'duckdb', 'lxml'
]
print("\n=== PYTHON PACKAGES ===")
for pkg in packages:
    try:
        m = __import__(pkg)
        ver = getattr(m, '__version__', 'unknown')
        print(f"  {pkg:20s}: installed ({ver})")
    except ImportError:
        print(f"  {pkg:20s}: NOT installed")

print("\n=== SYSTEM / POSTGRES CHECK ===")
for cmd in ["which psql", "which pg_isready", "pg_isready"]:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
        print(f"  {cmd}: {out}")
    except subprocess.CalledProcessError as e:
        print(f"  {cmd}: exit {e.returncode} ({e.output.decode().strip()})")

print("\n=== GPU 0 CHECK ===")
try:
    import torch
    print("  CUDA available:", torch.cuda.is_available())
    print("  Device count:", torch.cuda.device_count())
    if torch.cuda.is_available():
        print("  Device 0 name:", torch.cuda.get_device_name(0))
except Exception as e:
    print("  CUDA error:", e)
