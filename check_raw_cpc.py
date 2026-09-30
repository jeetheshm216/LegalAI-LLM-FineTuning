import re

with open("/home/sece2026-student07/legalai-finetuning/data/raw/central_acts/cpc_1908.txt") as f:
    text = f.read()

idx = text.find("temporary injunction may be granted")
if idx != -1:
    print(text[max(0, idx-200):idx+300])
else:
    print("Not found")

