import requests, time

t0 = time.time()
payload = {
    'content': 'What are the key facts in my case?',
    'mode': 'SINGLE_CASE',
    'caseId': 'case-01',
    'history': []
}
r = requests.post('http://127.0.0.1:8008/api/v1/ai/chat', json=payload, timeout=120)
print('Status:', r.status_code)
data = r.json()
print('Query type:', data.get('query_type'))
print('Content len:', len(data.get('content', '')))
print('Generation time:', data.get('generation_time_sec'), 'Elapsed:', round(time.time() - t0, 3))
print('Content snippet:', data.get('content', '')[:200])
