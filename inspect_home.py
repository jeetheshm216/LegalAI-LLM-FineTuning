import urllib.request
import re

url = "https://www.indiacode.nic.in/"
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

print("Title:", re.findall(r'<title>(.*?)</title>', html, re.I))
# Find form actions and links
links = re.findall(r'href=[\'"]([^\'"]*?)[\'"]', html)
print("Total links:", len(links))
for l in links:
    if any(k in l.lower() for k in ['act', 'search', 'handle', 'central']):
        print(" ", l)
