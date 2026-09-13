import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'Mozilla/5.0'}
base = "https://indiacode.gov.in/server/api/discover/search/objects"

queries = [
    "a2023-45.pdf",
    "a2023-46.pdf",
    "45 of 2023",
    "46 of 2023"
]

for q in queries:
    params = urllib.parse.urlencode({'query': q, 'size': 5})
    url = f"{base}?{params}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            objects = data.get('_embedded', {}).get('searchResult', {}).get('_embedded', {}).get('objects', [])
            print(f"\nQuery '{q}' found {len(objects)} objects:")
            for obj in objects:
                item = obj.get('_embedded', {}).get('indexableObject', {})
                name = item.get('name')
                handle = item.get('handle')
                uuid = item.get('uuid')
                print(f"  Name: {name} | Handle: {handle} | UUID: {uuid}")
                b_url = item.get('_links', {}).get('bundles', {}).get('href')
                if b_url:
                    req_b = urllib.request.Request(b_url, headers=headers)
                    with urllib.request.urlopen(req_b, timeout=10) as r_b:
                        bundles = json.loads(r_b.read().decode()).get('_embedded', {}).get('bundles', [])
                        for b in bundles:
                            bs_url = b.get('_links', {}).get('bitstreams', {}).get('href')
                            if bs_url:
                                req_bs = urllib.request.Request(bs_url, headers=headers)
                                with urllib.request.urlopen(req_bs, timeout=10) as r_bs:
                                    bitstreams = json.loads(r_bs.read().decode()).get('_embedded', {}).get('bitstreams', [])
                                    for bs in bitstreams:
                                        fname = bs.get('name')
                                        if 'a2023' in fname.lower() or 'bns' in fname.lower() or 'bnss' in fname.lower() or 'pdf' in fname.lower():
                                            print(f"    File: {fname} ({bs.get('sizeBytes')} bytes) -> {bs.get('_links', {}).get('content', {}).get('href')}")
    except Exception as e:
        print(f"Error {q}: {e}")
