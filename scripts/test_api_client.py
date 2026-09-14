#!/usr/bin/env python3
import urllib.request
import json

def test_query(content):
    url = "http://127.0.0.1:8008/api/v1/ai/chat"
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print("Status:", resp.status)
            print("Query Type:", res.get("query_type"))
            print("Reliability:", res.get("reliabilityLabel"))
            print("Answer:", res.get("content")[:200])
            return res
    except Exception as e:
        print("Error:", e)
        return None

print("=== 1. Conversational ===")
test_query("Hi")

print("\n=== 2. General Statutory ===")
test_query("What are the grounds for bail under BNSS?")

print("\n=== 3. Case Analysis Query without Case Dossier ===")
test_query("Here are the facts: A contractor failed to deliver construction material on time. What are our strongest arguments?")

print("\n=== 4. Out-of-Corpus Query ===")
test_query("What does Section 45 of the French Penal Code say?")
