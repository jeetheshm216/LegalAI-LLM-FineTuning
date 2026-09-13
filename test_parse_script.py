import pymupdf
import re
import unicodedata

def test_parse(pdf_path, start_page, total_sections, act_prefix):
    doc = pymupdf.open(pdf_path)
    pages = [doc[p].get_text() for p in range(start_page - 1, len(doc))]
    raw = "\n".join(pages)
    raw = unicodedata.normalize("NFKC", raw)
    
    found_sections = {}
    pos = 0
    missing = []
    
    for s in range(1, total_sections + 1):
        pat = re.compile(rf'(?:^|\n)\s*{s}\.\s*([^\n]+)', re.MULTILINE)
        m = pat.search(raw, pos)
        if m:
            header = m.group(1).strip()
            found_sections[s] = {"start": m.start(), "header": header}
            pos = m.start() + len(str(s)) + 2
        else:
            pat2 = re.compile(rf'(?:^|\n)\s*{s}\.([^\n]+)', re.MULTILINE)
            m2 = pat2.search(raw, pos)
            if m2:
                header = m2.group(1).strip()
                found_sections[s] = {"start": m2.start(), "header": header}
                pos = m2.start() + len(str(s)) + 1
            else:
                missing.append(s)
                
    print(f"{act_prefix}: Found {len(found_sections)}/{total_sections}. Missing: {missing}")
    return found_sections, missing

print("Testing BSA...")
test_parse('data/raw/BSA_2023_Act_47.pdf', 10, 170, 'BSA')

print("Testing BNS...")
test_parse('data/raw/BNS_2023_Act_45.pdf', 16, 358, 'BNS')

print("Testing BNSS...")
test_parse('data/raw/BNSS_2023_Act_46.pdf', 18, 531, 'BNSS')
