import requests, json

BASE_URL = 'http://127.0.0.1:8008'

test_queries = [
    ('what i syour name', 'case-01'),
    ('what is your name', 'case-01'),
    ('what is the matter', 'case-01'),
    ('waht is the matter', 'case-01'),
    ('what is the kay points in this case', 'case-01'),
    ('what is the priority of this case', 'case-01'),
    ('how important is this case', 'case-01'),
    ('what should i focus on', 'case-01'),
    ('what should i focus on', None),
    ('what is qwen', 'case-01'),
    ('what is rag', 'case-01'),
    ('what is section 66c', 'case-01'),
    ('what evidence do we have', 'case-01'),
    ('what evidence are we missing', 'case-01'),
    ('what should i prepare for the next hearing', 'case-01'),
    ('what are our arguments', 'case-01'),
    ('what could the other side argue', 'case-01'),
    ('what happened so far', 'case-01')
]

for q, cid in test_queries:
    payload = {
        'content': q,
        'mode': 'SINGLE_CASE' if cid else 'GENERAL',
        'caseId': cid,
        'selectedCases': [cid] if cid else [],
        'history': []
    }
    resp = requests.post(f'{BASE_URL}/api/v1/ai/chat', json=payload, timeout=60)
    data = resp.json()
    q_type = data.get('query_type')
    route = data.get('route')
    sub_intent = data.get('sub_intent')
    preview = data.get('content', '').replace('\n', ' ')[:90]
    print(f'[{q}] (case={cid}) -> type={q_type} | route={route} | sub={sub_intent}')
    print(f'   Content: {preview}...\n')
