import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0'}

req = urllib.request.Request("https://www.mha.gov.in/", headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

links = re.findall(r'href=[\'"]([^\'"]*?)[\'"]', html)
print(f"Total links on MHA: {len(links)}")
criminal_links = []
for l in links:
    if any(k in l.lower() for k in ['criminal', 'sanhita', 'adhiniyam', 'bns', 'bnss', 'bsa', 'acts']):
        criminal_links.append(l)

print(f"Criminal links count: {len(criminal_links)}")
for l in set(criminal_links)[:20]:
    print(" ", l)
