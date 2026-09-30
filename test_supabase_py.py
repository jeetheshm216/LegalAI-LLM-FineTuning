import requests
import json

SUPABASE_URL = "https://brveublsqvbulxxkgjxu.supabase.co"
SUPABASE_KEY = "sb_publishable_fo2AZ4LYA90V1N2ghE4JHw_qSTCGfix"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

tables = ['cases', 'documents', 'case_documents', 'conversations', 'messages', 'chat_history', 'case_chat_memory', 'advocates']

print("--- Checking Supabase Tables ---")
for t in tables:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{t}?select=*&limit=2", headers=headers)
    print(f"Table '{t}': HTTP {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Count: {len(data)}, Columns: {list(data[0].keys()) if data else 'Empty'}")
    else:
        print(f"  Error: {r.text}")
