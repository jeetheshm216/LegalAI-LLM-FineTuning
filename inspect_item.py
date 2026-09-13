import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# Inspect BNS item bundles/bitstreams
url = "https://indiacode.gov.in/server/api/core/items/be4ea071-a263-41cb-bc32-754bb9c30eab"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    item = json.loads(resp.read().decode())
    print("BNS Name:", item.get("name"))
    print("Metadata keys:", list(item.get("metadata", {}).keys()))
    for k in ["dc.title", "dc.identifier.actno", "dc.identifier.actyear", "dc.date.issued"]:
        print(f"  {k}: {item.get('metadata', {}).get(k)}")

# Check bundles (where the PDFs or attachments live)
bundles_url = item.get("_links", {}).get("bundles", {}).get("href")
if bundles_url:
    req_b = urllib.request.Request(bundles_url, headers=headers)
    with urllib.request.urlopen(req_b, timeout=10) as resp_b:
        b_data = json.loads(resp_b.read().decode())
        bundles = b_data.get("_embedded", {}).get("bundles", [])
        print(f"Bundles count: {len(bundles)}")
        for b in bundles:
            print("  Bundle:", b.get("name"))
            bs_url = b.get("_links", {}).get("bitstreams", {}).get("href")
            if bs_url:
                req_bs = urllib.request.Request(bs_url, headers=headers)
                with urllib.request.urlopen(req_bs, timeout=10) as resp_bs:
                    bs_data = json.loads(resp_bs.read().decode())
                    bitstreams = bs_data.get("_embedded", {}).get("bitstreams", [])
                    print(f"    Bitstreams count: {len(bitstreams)}")
                    for bs in bitstreams:
                        name = bs.get("name")
                        size = bs.get("sizeBytes")
                        content_url = bs.get("_links", {}).get("content", {}).get("href")
                        print(f"      File: {name} ({size} bytes) -> {content_url}")
