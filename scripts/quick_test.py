import requests
import json
import time

url = "http://127.0.0.1:8008/api/v1/ai/chat"

print("--- Test 1: SYSTEM_INFO ---")
t0 = time.time()
r = requests.post(url, json={"content": "What model powers LegalAI?", "mode": "SINGLE_CASE", "caseId": "case-01"})
print(f"Status: {r.status_code}, time: {round(time.time()-t0, 2)}s")
print(r.json().get("content")[:120], "...\n")

print("--- Test 2: CASE_MANAGEMENT ---")
t0 = time.time()
r = requests.post(url, json={"content": "Which case should I focus on?", "mode": "SINGLE_CASE", "caseId": "case-01"})
print(f"Status: {r.status_code}, time: {round(time.time()-t0, 2)}s")
print(r.json().get("content")[:120], "...\n")

print("--- Test 3: TECHNICAL_AI ---")
t0 = time.time()
r = requests.post(url, json={"content": "What is Qwen?", "mode": "SINGLE_CASE", "caseId": "case-01"})
print(f"Status: {r.status_code}, time: {round(time.time()-t0, 2)}s")
print(r.json().get("content")[:120], "...\n")
