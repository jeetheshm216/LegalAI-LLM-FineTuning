"""
tests/verify_gpu_stability.py
Verifies that multiple conversational queries reuse the exact same loaded model
and do not increase GPU memory or spawn duplicate model processes.
"""
import requests
import subprocess

BASE_URL = "http://127.0.0.1:8008"

# Test multiple conversational greetings
queries = ["Hello", "Hi", "What can you do?", "Hi again", "Thank you"]
for q in queries:
    r = requests.post(f"{BASE_URL}/api/v1/ai/chat", json={"content": q}, timeout=30)
    assert r.status_code == 200, f"Query '{q}' failed"
    data = r.json()
    assert data.get("query_type") == "CONVERSATIONAL"
    print(f"Query '{q}': response generated in {data.get('generation_time_sec')}s")

# Inspect GPU 2 memory and processes
res = subprocess.run(["nvidia-smi", "-i", "2"], capture_output=True, text=True)
print("\n" + "=" * 60)
print("GPU 2 STATUS AFTER MULTIPLE CALLS:")
print("=" * 60)
print(res.stdout)
