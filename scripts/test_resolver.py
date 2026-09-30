import re
import sqlite3

class ActResolver:
    def __init__(self, db_path='data/legalai_indian_legal_knowledge.db'):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        rows = c.execute('SELECT act_prefix, title, legal_domain FROM indian_legal_documents').fetchall()
        conn.close()

        self.indexed_acts = []
        for prefix, title, domain in rows:
            self.indexed_acts.append({
                'prefix': prefix,
                'title': title,
                'domain': domain
            })

        # Curated canonical alias triggers derived from official Acts
        self.aliases = {
            'COMPANIES_ACT_2013': [r'\bcompanies\s+act(?:\s*,?\s*2013)?\b', r'\bthe\s+companies\s+act\b'],
            'IBC_2016': [r'\bibc(?:\s*,?\s*2016)?\b', r'\binsolvency\s+and\s+bankruptcy\s+code(?:\s*,?\s*2016)?\b'],
            'ARBITRATION_ACT_1996': [r'\barbitration\s+(?:and\s+conciliation\s+)?act(?:\s*,?\s*1996)?\b', r'\barbitration\s+act\b'],
            'POCSO_ACT_2012': [r'\bpocso(?:\s+act)?(?:\s*,?\s*2012)?\b', r'\bprotection\s+of\s+children\s+from\s+sexual\s+offences(?:\s+act)?\b'],
            'PMLA_2002': [r'\bpmla(?:\s*,?\s*2002)?\b', r'\bprevention\s+of\s+money[\s\-]+laundering\s+act(?:\s*,?\s*2002)?\b'],
            'NDPS_ACT_1985': [r'\bndps(?:\s+act)?(?:\s*,?\s*1985)?\b', r'\bnarcotic\s+drugs(?:\s+and\s+psychotropic\s+substances)?(?:\s+act)?\b'],
            'CPC_1908': [r'\bcpc(?:\s*,?\s*1908)?\b', r'\bcode\s+of\s+civil\s+procedure(?:\s*,?\s*1908)?\b', r'\bcivil\s+procedure\s+code\b'],
            'SPECIFIC_RELIEF_ACT_1963': [r'\bspecific\s+relief\s+act(?:\s*,?\s*1963)?\b', r'\bspecific\s+relief\b'],
            'BNS': [r'\bbns(?:\s*,?\s*2023)?\b', r'\bbharatiya\s+nyaya\s+sanhita(?:\s*,?\s*2023)?\b'],
            'BNSS': [r'\bbnss(?:\s*,?\s*2023)?\b', r'\bbharatiya\s+nagarik\s+suraksha\s+sanhita(?:\s*,?\s*2023)?\b'],
            'BSA': [r'\bbsa(?:\s*,?\s*2023)?\b', r'\bbharatiya\s+sakshya\s+adhiniyam(?:\s*,?\s*2023)?\b'],
            'COI': [r'\bconstitution\s+of\s+india\b', r'\bthe\s+constitution\b', r'\bindian\s+constitution\b'],
            'NI_ACT': [r'\bni\s+act(?:\s*,?\s*1881)?\b', r'\bnegotiable\s+instruments\s+act(?:\s*,?\s*1881)?\b'],
            'IT_ACT': [r'\bit\s+act(?:\s*,?\s*2000)?\b', r'\binformation\s+technology\s+act(?:\s*,?\s*2000)?\b'],
            'CONTRACT_ACT': [r'\bcontract\s+act(?:\s*,?\s*1872)?\b', r'\bindian\s+contract\s+act\b'],
            'MOTOR_VEHICLES_ACT_1988': [r'\bmotor\s+vehicles?\s+act(?:\s*,?\s*1988)?\b', r'\bmva\b'],
            'CONSUMER_PROTECTION_ACT_2019': [r'\bconsumer\s+protection\s+act(?:\s*,?\s*2019)?\b', r'\bcpa\s+2019\b'],
            'TRANSFER_OF_PROPERTY_ACT_1882': [r'\btransfer\s+of\s+property\s+act(?:\s*,?\s*1882)?\b', r'\btpa\s+1882\b'],
            'SC_ST_POA_ACT_1989': [r'\bsc[\s\/]+st\s+act\b', r'\bprevention\s+of\s+atrocities\s+act\b']
        }

    def resolve(self, query: str):
        # 1. Extract provision number (Section X, Article Y, §Z)
        provision_match = re.search(r'\b(?:section|sec\.?|s\.?|u\/s|article|art\.?|§)\s*([0-9]+[A-Za-z]*)', query, re.I)
        provision_number = provision_match.group(1) if provision_match else None

        # 2. Match against indexed Acts
        matched_prefix = None
        matched_title = None
        for prefix, patterns in self.aliases.items():
            for pat in patterns:
                if re.search(pat, query, re.I):
                    matched_prefix = prefix
                    for act in self.indexed_acts:
                        if act['prefix'] == prefix:
                            matched_title = act['title']
                            break
                    break
            if matched_prefix:
                break

        if matched_prefix:
            return {
                'act_prefix': matched_prefix,
                'act_title': matched_title,
                'provision_number': provision_number,
                'is_unindexed_act': False,
                'unindexed_act_name': None
            }

        # 3. Detect unindexed Act requests (e.g., "XYZ Act", "Marine Insurance Act", "Factories Act")
        act_pattern = re.search(
            r'\b([A-Z0-9][A-Za-z0-9\s,\-\'\&]+?\s+(?:Act|Code|Sanhita|Adhiniyam|Ordinance|Rules|Regulations))(?:\s*,?\s*(\d{4}))?\b',
            query
        )
        if act_pattern:
            candidate_act = act_pattern.group(1).strip()
            if candidate_act.lower() not in ("legal authorities", "authoritative act", "an act", "the act"):
                return {
                    'act_prefix': None,
                    'act_title': None,
                    'provision_number': provision_number,
                    'is_unindexed_act': True,
                    'unindexed_act_name': candidate_act
                }

        return {
            'act_prefix': None,
            'act_title': None,
            'provision_number': provision_number,
            'is_unindexed_act': False,
            'unindexed_act_name': None
        }

if __name__ == '__main__':
    resolver = ActResolver()
    test_queries = [
        "What does Section 19 of the POCSO Act require when an offence is known or suspected?",
        "What are the requirements for incorporation of a company under Section 7 of the Companies Act, 2013?",
        "What are the requirements for initiating the corporate insolvency resolution process by an operational creditor under Section 9 of the IBC?",
        "What remedies are available under Section 34 of the Arbitration and Conciliation Act, 1996 to challenge an arbitral award?",
        "What are the twin bail conditions under Section 45 of the Prevention of Money-Laundering Act?",
        "What safeguards apply to a personal search under Section 50 of the NDPS Act?",
        "What is the scope of a first appeal under Section 96 of the Code of Civil Procedure?",
        "When can specific performance be granted under the Specific Relief Act, 1963?",
        "What does Section 10 of the XYZ Act provide?",
        "What is Section 4 of the Marine Insurance Act, 1963?",
        "Section 19 BNS",
        "Section 19 POCSO",
        "Section 45 PMLA",
        "Section 45 BNS",
        "Section 50 NDPS",
        "Section 50 BNS",
        "Section 96 CPC",
        "Section 96 Companies Act",
        "Section 9 IBC",
        "Section 9 Arbitration Act",
        "Can police arrest without warrant?"
    ]

    for q in test_queries:
        res = resolver.resolve(q)
        print(f"{q[:45]:<45} => act={str(res['act_prefix']):<22} sec={str(res['provision_number']):<4} unindexed={res['is_unindexed_act']}")
