import urllib.request
import json
import sys

url = "https://brveublsqvbulxxkgjxu.supabase.co/rest/v1/"
key = "sb_publishable_fo2AZ4LYA90V1N2ghE4JHw_qSTCGfix"

try:
    req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("Connected to Supabase! Status:", resp.status)
except Exception as e:
    print("Supabase connection result:", e)
