import glob
for f in glob.glob('/home/sece2026-student07/legalai-finetuning/frontend/src/styles/**/*', recursive=True):
    for line_no, l in enumerate(open(f, errors='ignore'), 1):
        if 'svg' in l.lower():
            print(f'{f}:{line_no}: {l.strip()}')
