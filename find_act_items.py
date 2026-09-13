import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'Mozilla/5.0'}

queries = [
    ("BNS", "Bharatiya Nyaya Sanhita, 2023"),
    ("BNSS", "Bharatiya Nagarik Suraksha Sanhita, 2023"),
    ("BSA", "Bharatiya Sakshya Adhiniyam, 2023"),
]

base_url = "https://indiacode.gov.in/server/api/discover/search/objects"

for code, q in queries:
    params = urllib.parse.urlencode({'query': f'"{q}"', 'size': 10})
    req = urllib.request.Request(f"{base_url}?{params}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            objects = data.get('_embedded', {}).get('searchResult', {}).get('_embedded', {}).get('objects', [])
            print(f"\n=== Query: {q} ({len(objects)} results) ===")
            for obj in objects:
                item = obj.get('_embedded', {}).get('indexableObject', {})
                name = item.get('name')
                handle = item.get('handle')
                uuid = item.get('uuid')
                meta = item.get('metadata', {})
                act_no = meta.get('dc.identifier.actno', [{'value': 'N/A'}])[0].get('value')
                act_yr = meta.get('dc.identifier.actyear', [{'value': 'N/A'}])[0].get('value')
                print(f"  Name: {name}")
                print(f"  Handle: {handle} | UUID: {uuid} | Act No: {act_no} | Year: {act_yr}")
    except Exception as e:
        print(f"Error querying {q}: {e}")
