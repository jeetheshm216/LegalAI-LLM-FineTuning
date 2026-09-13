import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

handles = [
    ("BNS", "123456789/568022"),
    ("BNSS_1", "123456789/568091"),
    ("BNSS_2", "123456789/601739"),
    ("BNSS_3", "123456789/588182"),
    ("BSA", "123456789/496549"),
]

for name, h in handles:
    url = f"https://indiacode.gov.in/server/api/pid/find?id={h}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            item = json.loads(resp.read().decode())
            print(f"\n=== {name} ({h}) ===")
            print(f"Name: {item.get('name')}")
            b_url = item.get('_links', {}).get('bundles', {}).get('href')
            if b_url:
                with urllib.request.urlopen(urllib.request.Request(b_url, headers=headers), timeout=10) as r_b:
                    bundles = json.loads(r_b.read().decode()).get('_embedded', {}).get('bundles', [])
                    for b in bundles:
                        bs_url = b.get('_links', {}).get('bitstreams', {}).get('href')
                        if bs_url:
                            with urllib.request.urlopen(urllib.request.Request(bs_url, headers=headers), timeout=10) as r_bs:
                                bss = json.loads(r_bs.read().decode()).get('_embedded', {}).get('bitstreams', [])
                                for bs in bss:
                                    print(f"  File: {bs.get('name')} ({bs.get('sizeBytes')} bytes) -> {bs.get('_links', {}).get('content', {}).get('href')}")
    except Exception as e:
        print(f"Error {name}: {e}")
