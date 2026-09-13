import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}

# Check MHA new criminal laws page
urls = [
    "https://www.mha.gov.in/",
    "https://lddashboard.nic.in/",
    "https://egazette.gov.in/"
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"URL: {u} -> Status: {resp.status}")
    except Exception as e:
        print(f"URL: {u} -> Error: {e}")
