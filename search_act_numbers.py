import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'Mozilla/5.0'}
base = "https://indiacode.gov.in/server/api/discover/search/objects"

queries = [
    "Act No. 45 of 2023",
    "Act No. 46 of 2023",
    "Act No. 47 of 2023"
]

for q in queries:
    params = urllib.parse.urlencode({'query': f'"{q}"', 'size': 5})
    url = f"{base}?{params}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            objects = data.get('_embedded', {}).get('searchResult', {}).get('_embedded', {}).get('objects', [])
            print(f"\nQuery '{q}' found {len(objects)} objects:")
            for obj in objects:
                item = obj.get('_embedded', {}).get('indexableObject', {})
                print(f"  Name: {item.get('name')}")
                print(f"  Handle: {item.get('handle')}")
                print(f"  UUID: {item.get('uuid')}")
                # check bundles
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
                                        print(f"    File: {bs.get('name')} ({bs.get('sizeBytes')} bytes) -> {bs.get('_links', {}).get('content', {}).get('href')}")
    except Exception as e:
        print(f"Error {q}: {e}")
