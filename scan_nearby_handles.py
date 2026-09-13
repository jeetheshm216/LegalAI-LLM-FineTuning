import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# Test handles around 496545 - 496555
for h_id in range(496540, 496560):
    h = f"123456789/{h_id}"
    url = f"https://indiacode.gov.in/server/api/pid/find?id={h}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            item = json.loads(resp.read().decode())
            name = item.get("name")
            print(f"Handle {h}: {name}")
            # check files
            b_url = item.get('_links', {}).get('bundles', {}).get('href')
            if b_url:
                with urllib.request.urlopen(urllib.request.Request(b_url, headers=headers), timeout=5) as r_b:
                    bundles = json.loads(r_b.read().decode()).get('_embedded', {}).get('bundles', [])
                    for b in bundles:
                        bs_url = b.get('_links', {}).get('bitstreams', {}).get('href')
                        if bs_url:
                            with urllib.request.urlopen(urllib.request.Request(bs_url, headers=headers), timeout=5) as r_bs:
                                bss = json.loads(r_bs.read().decode()).get('_embedded', {}).get('bitstreams', [])
                                for bs in bss:
                                    print(f"   -> {bs.get('name')} ({bs.get('sizeBytes')} B): {bs.get('_links', {}).get('content', {}).get('href')}")
    except Exception:
        pass
