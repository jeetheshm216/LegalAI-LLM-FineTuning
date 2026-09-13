import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    "Bharatiya Nyaya Sanhita",
    "Bharatiya Nagarik Suraksha Sanhita",
    "Bharatiya Sakshya Adhiniyam"
]

for q in queries:
    url = f"https://www.indiacode.nic.in/simple-search?query={urllib.parse.quote(q)}"
    print(f"\nSearching: {url}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"Status: {resp.status}, HTML length: {len(html)}")
            # Find handle links
            matches = re.findall(r'href=[\'"](/handle/123456789/\d+)[\'"][^>]*>(.*?)</a>', html)
            print(f"Found {len(matches)} handle matches:")
            for m in matches[:5]:
                print(f"  {m[0]} -> {re.sub('<[^<]+?>', '', m[1]).strip()[:80]}")
    except Exception as e:
        print(f"Error querying {q}: {e}")
