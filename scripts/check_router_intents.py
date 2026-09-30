from src.api.query_router import get_query_router

router = get_query_router()
queries = [
    'What does Section 19 of the POCSO Act require when an offence is known or suspected?',
    'What are the requirements for incorporation of a company under Section 7 of the Companies Act, 2013?',
    'What are the requirements for initiating the corporate insolvency resolution process by an operational creditor under Section 9 of the IBC?',
    'What remedies are available under Section 34 of the Arbitration and Conciliation Act, 1996 to challenge an arbitral award?',
    'What are the twin bail conditions under Section 45 of the Prevention of Money-Laundering Act?',
    'What safeguards apply to a personal search under Section 50 of the NDPS Act?',
    'What is the scope of a first appeal under Section 96 of the Code of Civil Procedure?',
    'When can specific performance be granted under the Specific Relief Act, 1963?',
    'What does Section 10 of the XYZ Act provide?'
]

for q in queries:
    res = router.classify(q)
    print(f'{res.intent.value:<15} | {q[:70]}')
