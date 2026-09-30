import requests
import json

test_suite = [
    # 1. Greetings / conversational
    ('hi', 'GENERAL', None),
    ('how are you', 'GENERAL', None),
    ('are you doing good', 'GENERAL', None),
    ('what can you do', 'GENERAL', None),
    ("why aren't you working as a normal chatbot", 'GENERAL', None),
    ('who made you', 'GENERAL', None),
    
    # 2. Case in Single Case Mode
    ('what is this case is about', 'SINGLE_CASE', '2024-CR-0442'),
    ('what is this case about', 'SINGLE_CASE', '2024-CR-0442'),
    ('tell me about this case', 'SINGLE_CASE', '2024-CR-0442'),
    ('summary of the case', 'SINGLE_CASE', '2024-CR-0442'),
    ('who are the parties involved', 'SINGLE_CASE', '2024-CR-0442'),
    ('key facts', 'SINGLE_CASE', '2024-CR-0442'),
    
    # 3. Case by name / typo in General Mode
    ('what is the case about the martienx', 'GENERAL', None),
    ('what is the martinez case about', 'GENERAL', None),
    ('tell me about state v whitfield', 'GENERAL', None),
    
    # 4. Out of domain (non-legal)
    ('how to make pasta', 'GENERAL', None),
    ('write python code for merge sort', 'GENERAL', None),
    ('who won the world cup in 2022', 'GENERAL', None),
    
    # 5. Pure legal statutory
    ('what is section 420 of IPC', 'GENERAL', None),
    ('explain order 39 rule 1 of CPC', 'GENERAL', None)
]

for content, mode, case_id in test_suite:
    payload = {'content': content, 'mode': mode, 'conversationId': 'diag_1'}
    if case_id:
        payload['caseId'] = case_id
    try:
        r = requests.post('http://127.0.0.1:8008/api/v1/ai/chat', json=payload, timeout=60)
        data = r.json() if r.status_code == 200 else {}
        qtype = str(data.get('query_type'))
        resp = str(data.get('content', ''))[:120].replace('\n', ' ')
        print(f'[{mode:11}] [{qtype:15}] Query: "{content}" -> Resp: {resp}')
    except Exception as e:
        print(f'[{mode:11}] [ERROR] Query: "{content}" -> {e}')
