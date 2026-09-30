"""Act and Domain Resolver for Indian Legal Knowledge Retrieval.

Guarantees strict statutory separation, context inheritance, ambiguity detection,
cybercrime domain routing, and structured legal query generation.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from ..indexing.database import IndianLegalDatabaseManager
from ..models import StructuredLegalQuery, ProvisionType
from ..cybercrime.registry import detect_cybercrime_domains, CybercrimeCategory


class IndianActResolver:
    """Resolves target Indian Acts, canonical prefixes, provision types, and statutory provisions."""

    ACT_PATTERNS: Dict[str, List[str]] = {
        "COMPANIES_ACT_2013": [
            r"\bcompanies\s+act(?:\s*,?\s*2013)?\b",
            r"\bthe\s+companies\s+act\b",
            r"\bunder\s+the\s+companies\s+act\b",
            r"\bca\s*2013\b"
        ],
        "IBC_2016": [
            r"\bibc(?:\s*,?\s*2016)?\b",
            r"\binsolvency\s+and\s+bankruptcy\s+code(?:\s*,?\s*2016)?\b",
            r"\binsolvency\s+code\b"
        ],
        "ARBITRATION_ACT_1996": [
            r"\barbitration\s+(?:and\s+conciliation\s+)?act(?:\s*,?\s*1996)?\b",
            r"\barbitration\s+act\b",
            r"\bconciliation\s+act\b"
        ],
        "POCSO_ACT_2012": [
            r"\bpocso(?:[\s\-]+act)?(?:\s*,?\s*2012)?\b",
            r"\bprotection\s+of\s+children\s+from\s+sexual\s+offences(?:\s+act)?\b"
        ],
        "PMLA_2002": [
            r"\bpmla(?:\s*,?\s*2002)?\b",
            r"\bprevention\s+of\s+money[\s\-]+laundering\s+act(?:\s*,?\s*2002)?\b",
            r"\bmoney\s+laundering\s+act\b"
        ],
        "NDPS_ACT_1985": [
            r"\bndps(?:\s+act)?(?:\s*,?\s*1985)?\b",
            r"\bnarcotic\s+drugs(?:\s+and\s+psychotropic\s+substances)?(?:\s+act)?\b"
        ],
        "CPC_1908": [
            r"\bcpc(?:\s*,?\s*1908)?\b",
            r"\bcode\s+of\s+civil\s+procedure(?:\s*,?\s*1908)?\b",
            r"\bcivil\s+procedure\s+code\b"
        ],
        "SPECIFIC_RELIEF_ACT_1963": [
            r"\bspecific\s+relief\s+act(?:\s*,?\s*1963)?\b",
            r"\bspecific\s+relief\b"
        ],
        "BNS": [
            r"\bbns(?:\s*,?\s*2023)?\b",
            r"\bbharatiya\s+nyaya\s+sanhita(?:\s*,?\s*2023)?\b"
        ],
        "BNSS": [
            r"\bbnss(?:\s*,?\s*2023)?\b",
            r"\bbharatiya\s+nagarik\s+suraksha\s+sanhita(?:\s*,?\s*2023)?\b"
        ],
        "BSA": [
            r"\bbsaa?(?:\s*,?\s*2023)?\b",
            r"\bbsa(?:\s*,?\s*2023)?\b",
            r"\bbharatiya\s+sakshya\s+adhiniyam(?:\s*,?\s*2023)?\b"
        ],
        "COI": [
            r"\bconstitution\s+of\s+india\b",
            r"\bindian\s+constitution\b",
            r"\bthe\s+constitution\b"
        ],
        "IT_ACT": [
            r"\binformation\s+technology\s+act(?:\s*,?\s*2000)?\b",
            r"\bit\s+act(?:\s*,?\s*2000)?\b",
            r"\bthe\s+it\s+act\b",
            r"\bunder\s+the\s+it\s+act\b",
            r"\bita(?:\s*,?\s*2000)?\b"
        ],
        "RTI_ACT": [
            r"\brti\s+act(?:\s*,?\s*2005)?\b",
            r"\bright\s+to\s+information(?:\s+act)?(?:\s*,?\s*2005)?\b"
        ],
        "NI_ACT": [
            r"\bnegotiable\s+instruments\s+act(?:\s*,?\s*1881)?\b",
            r"\bni\s+act(?:\s*,?\s*1881)?\b"
        ],
        "CONTRACT_ACT": [
            r"\bindian\s+contract\s+act(?:\s*,?\s*1872)?\b",
            r"\bcontract\s+act(?:[\s\-]+1872)?\b"
        ],
        "MOTOR_VEHICLES_ACT_1988": [
            r"\bmotor\s+vehicles?\s+act(?:\s*,?\s*1988)?\b",
            r"\bmva\b"
        ],
        "CONSUMER_PROTECTION_ACT_2019": [
            r"\bconsumer\s+protection\s+act(?:\s*,?\s*2019)?\b",
            r"\bcpa\s*2019\b"
        ],
        "TRANSFER_OF_PROPERTY_ACT_1882": [
            r"\btransfer\s+of\s+property\s+act(?:\s*,?\s*1882)?\b",
            r"\btpa(?:\s*1882)?\b"
        ],
        "SC_ST_POA_ACT_1989": [
            r"\bsc[\s\/]+st\s+act\b",
            r"\bsc\s+and\s+st\s+(?:prevention\s+of\s+atrocities\s+)?act\b",
            r"\bprevention\s+of\s+atrocities\s+act\b"
        ],
        "IEA": [
            r"\bindian\s+evidence\s+act(?:\s*,?\s*1872)?\b",
            r"\bevidence\s+act(?:\s*,?\s*1872)?\b",
            r"\biea(?:\s*,?\s*1872)?\b"
        ],
        "IPC": [
            r"\bindian\s+penal\s+code(?:\s*,?\s*1860)?\b",
            r"\bpenal\s+code\b",
            r"\bipc(?:\s*,?\s*1860)?\b"
        ],
        "CRPC": [
            r"\bcode\s+of\s+criminal\s+procedure(?:\s*,?\s*1973)?\b",
            r"\bcriminal\s+procedure\s+code\b",
            r"\bcrpc(?:\s*,?\s*1973)?\b"
        ]
    }

    ROMAN_MAP = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15, 'XVI': 16, 'XVII': 17, 'XVIII': 18,
        'XIX': 19, 'XX': 20, 'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25, 'XXVI': 26,
        'XXVII': 27, 'XXVIII': 28, 'XXIX': 29, 'XXX': 30, 'XXXI': 31, 'XXXII': 32, 'XXXIII': 33,
        'XXXIV': 34, 'XXXV': 35, 'XXXVI': 36, 'XXXVII': 37, 'XXXVIII': 38, 'XXXIX': 39, 'XL': 40,
        'XLI': 41, 'XLII': 42, 'XLIII': 43, 'XLIV': 44, 'XLV': 45, 'XLVI': 46, 'XLVII': 47, 'XLVIII': 48,
        'XLIX': 49, 'L': 50, 'LI': 51
    }

    def __init__(self, db_manager: Optional[IndianLegalDatabaseManager] = None):
        self.db = db_manager
        self.indexed_acts: List[Dict[str, Any]] = []
        if self.db:
            try:
                with self.db._get_connection() as conn:
                    rows = conn.execute("SELECT act_prefix, title, legal_domain FROM indian_legal_documents").fetchall()
                    for r in rows:
                        self.indexed_acts.append({
                            "prefix": r["act_prefix"],
                            "title": r["title"],
                            "domain": r["legal_domain"]
                        })
            except Exception:
                pass

    def _normalize_provision(self, raw_prov: str) -> str:
        if not raw_prov:
            return ""
        clean = raw_prov.strip().replace(" ", "").replace("-", "")
        normalized = ""
        in_paren = False
        for char in clean:
            if char == '(':
                in_paren = True
                normalized += char
            elif char == ')':
                in_paren = False
                normalized += char
            elif not in_paren and char.isalpha():
                normalized += char.upper()
            else:
                normalized += char
        return normalized

    def _extract_act_from_text(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str], int]:
        for prefix, patterns in self.ACT_PATTERNS.items():
            for pat in patterns:
                m_act = re.search(pat, text, re.I)
                if m_act:
                    matched_title = prefix
                    matched_domain = "General Indian Law"
                    for act in self.indexed_acts:
                        if act["prefix"] == prefix:
                            matched_title = act["title"]
                            matched_domain = act["domain"]
                            break
                    if prefix == "IT_ACT" and matched_title == "IT_ACT":
                        matched_title = "Information Technology Act, 2000"
                        matched_domain = "Cyber & Technology Law"
                    elif prefix == "IEA" and matched_title == "IEA":
                        matched_title = "Indian Evidence Act, 1872"
                        matched_domain = "Evidence Law"
                    elif prefix == "IPC" and matched_title == "IPC":
                        matched_title = "Indian Penal Code, 1860"
                        matched_domain = "Criminal Law"
                    elif prefix == "CRPC" and matched_title == "CRPC":
                        matched_title = "Code of Criminal Procedure, 1973"
                        matched_domain = "Criminal Procedure"
                    elif prefix == "IT_RULES_2021":
                        matched_title = "Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021"
                        matched_domain = "Cyber & Technology Law"
                    return prefix, matched_title, matched_domain, m_act.end()
        return None, None, None, -1

    def resolve(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        cleaned = query.strip()

        # Check cybercrime domains
        cyber_cats = detect_cybercrime_domains(cleaned)
        is_cybercrime = len(cyber_cats) > 0

        # 1. Order and Rule syntax (e.g. Order 39 Rule 1, Order XXXIX Rule 1)
        order_match = re.search(r'\b(?:order|o\.)\s*([0-9IVXLCDM]+)\s*(?:rule|r\.)\s*([0-9]+[A-Za-z]*)', cleaned, re.I)
        provision_number = None
        provision_type = ProvisionType.SECTION
        subclause = None

        if order_match:
            raw_order = order_match.group(1).upper()
            rule_val = order_match.group(2).upper()
            order_num = self.ROMAN_MAP.get(raw_order, raw_order)
            provision_number = f"ORDER_{order_num}_RULE_{rule_val}"
            provision_type = ProvisionType.ORDER_RULE
        else:
            # 2. Extract statutory provision with standard prefixes (Section 9: section, sec, s, article, art, provision, prov, act)
            prov_match = re.search(
                r'\b(section|sec\.?|s\.?|u\/s|article|art\.?|provision|prov\.?|act)\s*([0-9]+[A-Za-z]*(?:\s*[\-\s]\s*[A-Za-z])?(?:\s*\([0-9a-zA-Z]+\))*)\b',
                cleaned,
                re.I
            )
            if prov_match:
                prefix_word = prov_match.group(1).lower()
                raw_full = prov_match.group(2)
                # If matched prefix is 'act', ensure it is not a 4-digit year (e.g. 'Act 2013' or 'Act 1961')
                is_year = raw_full.isdigit() and len(raw_full) == 4 and (1800 <= int(raw_full) <= 2030)
                if not (prefix_word == "act" and is_year):
                    sub_match = re.search(r'\(([^)]+)\)', raw_full)
                    if sub_match:
                        subclause = sub_match.group(1)
                    provision_number = self._normalize_provision(raw_full)
                    if prefix_word in ("article", "art", "art."):
                        provision_type = ProvisionType.ARTICLE
                    else:
                        provision_type = ProvisionType.SECTION

        # 3. Explicit Act matching in current query (Priority 1)
        matched_prefix, matched_title, matched_domain, matched_end_pos = self._extract_act_from_text(cleaned)

        # 4. Trailing provision syntax: e.g. "Companies Act 89", "BNS 103", "IT Act 66C"
        if matched_prefix and not provision_number and matched_end_pos > 0:
            after_act = cleaned[matched_end_pos:].strip()
            trailing_prov_match = re.match(r'^[-:\s]*([0-9]+[A-Za-z]*(?:\s*[\-\s]\s*[A-Za-z])?(?:\s*\([0-9a-zA-Z]+\))*)\b', after_act, re.I)
            if trailing_prov_match:
                candidate_prov = trailing_prov_match.group(1).strip()
                if not (candidate_prov.isdigit() and len(candidate_prov) == 4 and int(candidate_prov) in range(1800, 2030)):
                    provision_number = self._normalize_provision(candidate_prov)
                    provision_type = ProvisionType.SECTION

        # 4B. Legal Concept & Offense Mapping
        # When user asks about a specific offense, term, or procedure by name (e.g. "theft under BNS", "murder in BNS", "bail under BNSS")
        if matched_prefix and not provision_number:
            q_lower = cleaned.lower()
            if matched_prefix == "BNS":
                BNS_OFFENSE_MAP = {
                    "theft": "303",
                    "snatching": "304",
                    "extortion": "308",
                    "robbery": "309",
                    "dacoity": "310",
                    "cheating": "318",
                    "criminal breach of trust": "316",
                    "dishonest misappropriation": "314",
                    "receiving stolen property": "317",
                    "murder": "103",
                    "culpable homicide": "100",
                    "causing death by negligence": "106",
                    "hit and run": "106",
                    "hurt": "115",
                    "grievous hurt": "116",
                    "acid attack": "124",
                    "kidnapping": "137",
                    "abduction": "138",
                    "trafficking": "143",
                    "rape": "64",
                    "gang rape": "70",
                    "sexual assault": "74",
                    "outraging modesty": "74",
                    "dowry death": "80",
                    "cruelty by husband": "85",
                    "criminal conspiracy": "61",
                    "sedition": "152",
                    "endangering sovereignty": "152",
                    "defamation": "356",
                    "forgery": "336",
                    "criminal intimidation": "351",
                    "organized crime": "111",
                    "petty organized crime": "112",
                    "terrorist act": "113",
                    "mob lynching": "103"
                }
                for offense, sec in sorted(BNS_OFFENSE_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(rf'\b{re.escape(offense)}\b', q_lower):
                        provision_number = sec
                        provision_type = ProvisionType.SECTION
                        break

            elif matched_prefix == "BNSS":
                BNSS_PROCEDURE_MAP = {
                    "regular bail": "480",
                    "bail in non-bailable": "480",
                    "anticipatory bail": "482",
                    "special powers of high court or court of session regarding bail": "483",
                    "maximum period for which an under-trial prisoner can be detained": "479",
                    "undertrial bail": "479",
                    "quashing": "528",
                    "inherent powers": "528",
                    "zero fir": "173",
                    "information in cognizable cases": "173",
                    "fir": "173",
                    "arrest of persons": "35",
                    "notice of appearance before police officer": "35",
                    "arrest": "35",
                    "search warrant": "96",
                    "police custody": "187",
                    "remand": "187",
                    "charge sheet": "193",
                    "discharge": "250",
                    "plea bargaining": "289"
                }
                for proc, sec in sorted(BNSS_PROCEDURE_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(rf'\b{re.escape(proc)}\b', q_lower):
                        provision_number = sec
                        provision_type = ProvisionType.SECTION
                        break

            elif matched_prefix == "BSA":
                BSA_MAP = {
                    "electronic record": "63",
                    "electronic evidence": "63",
                    "certificate for electronic evidence": "63",
                    "section 65b equivalent": "63",
                    "primary evidence": "57",
                    "secondary evidence": "58",
                    "admission": "15",
                    "confession": "21",
                    "dying declaration": "26",
                    "expert opinion": "39",
                    "burden of proof": "104",
                    "presumption as to electronic records": "86",
                    "accomplice": "138",
                    "hostile witness": "145"
                }
                for term, sec in sorted(BSA_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(rf'\b{re.escape(term)}\b', q_lower):
                        provision_number = sec
                        provision_type = ProvisionType.SECTION
                        break

            elif matched_prefix == "IPC":
                IPC_MAP = {
                    "theft": "378",
                    "punishment for theft": "379",
                    "extortion": "383",
                    "robbery": "390",
                    "dacoity": "391",
                    "cheating": "415",
                    "criminal breach of trust": "405",
                    "murder": "300",
                    "punishment for murder": "302",
                    "culpable homicide": "299",
                    "rape": "375",
                    "defamation": "499",
                    "forgery": "463",
                    "sedition": "124A"
                }
                for term, sec in sorted(IPC_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(rf'\b{re.escape(term)}\b', q_lower):
                        provision_number = sec
                        provision_type = ProvisionType.SECTION
                        break

            elif matched_prefix == "CRPC":
                CRPC_MAP = {
                    "anticipatory bail": "438",
                    "regular bail": "437",
                    "special bail": "439",
                    "quashing": "482",
                    "inherent powers": "482",
                    "fir": "154",
                    "remand": "167"
                }
                for term, sec in sorted(CRPC_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(rf'\b{re.escape(term)}\b', q_lower):
                        provision_number = sec
                        provision_type = ProvisionType.SECTION
                        break

            elif matched_prefix == "IEA":
                IEA_MAP = {
                    "electronic record": "65B",
                    "electronic evidence": "65B",
                    "certificate": "65B",
                    "dying declaration": "32"
                }
                for term, sec in sorted(IEA_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(rf'\b{re.escape(term)}\b', q_lower):
                        provision_number = sec
                        provision_type = ProvisionType.SECTION
                        break

        # 5. Act Overview check
        is_act_overview = False
        if matched_prefix and not provision_number:
            overview_pattern = r'\b(?:what\s+is|what\s+does|overview\s+of|explain|summarize|tell\s+me\s+about|scope\s+of|brief\s+on)\b'
            if re.search(overview_pattern, cleaned, re.I):
                stripped = re.sub(overview_pattern, '', cleaned, flags=re.I)
                act_tokens = [
                    "bharatiya nyaya sanhita", "bharatiya nagarik suraksha sanhita", "bharatiya sakshya adhiniyam",
                    "indian penal code", "code of criminal procedure", "code of civil procedure", "indian evidence act",
                    "information technology act", "companies act", "constitution of india", "arbitration and conciliation act",
                    "bns", "bnss", "bsa", "ipc", "crpc", "cpc", "iea", "it act",
                    "sanhita", "adhiniyam", "code", "act", "law", "statute",
                    "2023", "1860", "1973", "1908", "1872", "2000", "2013", "1996"
                ]
                if matched_title:
                    act_tokens.append(matched_title.lower())
                if matched_prefix:
                    act_tokens.append(matched_prefix.lower())

                for tok in sorted(act_tokens, key=len, reverse=True):
                    stripped = re.sub(rf'\b{re.escape(tok)}\b', '', stripped, flags=re.I)

                stripped = re.sub(r'\b(?:the|a|an|in|under|of|for|to|about|new|old|criminal|civil|central|state|all)\b', '', stripped, flags=re.I)
                stripped = re.sub(r'[^a-zA-Z0-9\s]', '', stripped).strip()
                substantive_tokens = [w for w in stripped.split() if len(w) > 2]
                if len(substantive_tokens) == 0:
                    is_act_overview = True

        # 6. Context inheritance (Priority 3)
        inherited_from_history = False
        if provision_number and not matched_prefix and conversation_history:
            for turn in reversed(conversation_history):
                content = turn.get("content", "") or ""
                prev_prefix, prev_title, prev_domain, _ = self._extract_act_from_text(content)
                if prev_prefix:
                    matched_prefix = prev_prefix
                    matched_title = prev_title
                    matched_domain = prev_domain
                    inherited_from_history = True
                    break

        # 7. Unindexed Act check (Structural recognition of Central / State enactments)
        if not matched_prefix:
            is_act_number_query = bool(re.search(r'\bact\s+number\b', cleaned, re.I))
            s_cand = re.sub(r'\b(?:section|sec\.?|s\.?|article|art\.?|rule|r\.?|order|o\.?|provision|prov\.?|act)\s*[0-9]+[A-Za-z]*(?:\s*[\-\s]\s*[A-Za-z])?(?:\s*\([0-9a-zA-Z]+\))*\b', '', cleaned, flags=re.I).strip()
            s_cand = re.sub(r'\b(?:what\s+is|what\s+does|what\s+are|overview\s+of|explain|summarize|tell\s+me\s+about|act\s+number(?:\s+of)?)\b', '', s_cand, flags=re.I).strip()
            s_cand = re.sub(r'^(?:the|an|under|of|in|for|about)\s+', '', s_cand, flags=re.I).strip()
            unindexed_match = re.search(
                r'\b([A-Z][A-Za-z0-9\s,\-\'\&]{1,50}?\s+(?:Act|Code|Sanhita|Adhiniyam|Ordinance|Rules|Regulations)(?:\s*,?\s*\d{4})?)\b',
                s_cand
            )
            if unindexed_match:
                cand = unindexed_match.group(1).strip()
                cand_lower = cand.lower()
                if cand_lower not in ("legal authorities", "authoritative act", "an act", "the act", "this act", "it rules 2021", "it rules", "spdi rules"):
                    return {
                        "intent": "ACT_METADATA_QUERY" if is_act_number_query else ("EXACT_PROVISION_QUERY" if provision_number else "GENERAL_LEGAL"),
                        "entity_type": provision_type.value,
                        "act": cand,
                        "act_prefix": None,
                        "act_title": cand,
                        "legal_domain": "CYBERCRIME" if is_cybercrime else None,
                        "provision_type": provision_type.value,
                        "provision_number": provision_number,
                        "subclause": subclause,
                        "temporal_reference": None,
                        "context_reference": "CURRENT_QUERY",
                        "confidence": 0.9,
                        "needs_clarification": False,
                        "clarification_question": None,
                        "is_unindexed_act": True,
                        "unindexed_act_name": cand,
                        "is_act_number_query": is_act_number_query,
                        "inherited_from_history": False,
                        "domain": "CYBERCRIME" if is_cybercrime else "GENERAL_LEGAL",
                        "cybercrime_categories": [c.value for c in cyber_cats]
                    }

        # 7B. Check if this is a known landmark judgment query
        is_known_judgment_query = any(name in cleaned.lower() for name in ["shreya singhal", "arjun panditrao", "anvar p.v", "anvar pv", "selvi", "puttaswamy"])
        if is_known_judgment_query:
            if "shreya singhal" in cleaned.lower():
                matched_prefix = "IT_ACT"
                matched_title = "Information Technology Act, 2000"
            elif "arjun panditrao" in cleaned.lower() or "anvar" in cleaned.lower():
                if "65b" in cleaned.lower() or "65a" in cleaned.lower():
                    matched_prefix = "IEA"
                    matched_title = "Indian Evidence Act, 1872"
                else:
                    matched_prefix = "BSA"
                    matched_title = "Bharatiya Sakshya Adhiniyam, 2023"

        # 8. Ambiguity detection (Step 15 & Absolute Rule 10: Zero semantic fallback for exact provision queries)
        if provision_number and not matched_prefix:
            sec_display = f"Section {provision_number}" if provision_type == ProvisionType.SECTION else f"{provision_type.value} {provision_number}"
            clarification_msg = (
                f"Which Act or Code are you referring to regarding {sec_display}? "
                f"(e.g., The Companies Act, 2013, The Advocates Act, 1961, The Information Technology Act, 2000, etc.)"
            )
            return {
                "intent": "AMBIGUOUS_PROVISION",
                "entity_type": provision_type.value,
                "act": None,
                "act_prefix": None,
                "act_title": None,
                "legal_domain": "CYBERCRIME" if is_cybercrime else None,
                "provision_type": provision_type.value,
                "provision_number": provision_number,
                "subclause": subclause,
                "temporal_reference": None,
                "context_reference": None,
                "confidence": 0.0,
                "needs_clarification": True,
                "clarification_question": clarification_msg,
                "is_unindexed_act": False,
                "unindexed_act_name": None,
                "is_act_number_query": False,
                "inherited_from_history": False,
                "domain": "CYBERCRIME" if is_cybercrime else "AMBIGUOUS",
                "cybercrime_categories": [c.value for c in cyber_cats]
            }

        # 9. Intent assignment
        if is_act_overview:
            intent = "ACT_OVERVIEW"
        elif provision_number and matched_prefix:
            intent = "EXACT_PROVISION_QUERY"
        else:
            intent = "GENERAL_LEGAL"

        # Domain assignment
        effective_domain = "CYBERCRIME" if (is_cybercrime or matched_prefix == "IT_ACT") else (matched_domain or "General Indian Law")

        return {
            "intent": intent,
            "entity_type": provision_type.value,
            "act": matched_title or matched_prefix,
            "act_prefix": matched_prefix,
            "act_title": matched_title or matched_prefix,
            "legal_domain": matched_domain or effective_domain,
            "domain": "CYBERCRIME" if (is_cybercrime or matched_prefix == "IT_ACT") else "GENERAL_LEGAL",
            "cybercrime_categories": [c.value for c in cyber_cats],
            "provision_type": provision_type.value,
            "provision_number": provision_number,
            "subclause": subclause,
            "temporal_reference": None,
            "context_reference": "HISTORY_INHERITED" if inherited_from_history else "EXPLICIT_QUERY",
            "confidence": 1.0 if matched_prefix else 0.5,
            "needs_clarification": False,
            "clarification_question": None,
            "is_unindexed_act": False,
            "unindexed_act_name": None,
            "is_act_number_query": False,
            "inherited_from_history": inherited_from_history
        }

    @classmethod
    def extract_all_statutory_references(cls, text: str) -> List[Tuple[str, str, str]]:
        """
        Extracts all (act_prefix, provision_number, provision_type) tuples from text.
        Handles compound mentions like:
        - BNS Section 303 compared to old IPC Section 378/379
        - Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA) and how it replaces Section 65B of IEA
        - Section 480 of BNSS and Section 479
        - BNSS Section 173
        """
        ACT_PATTERNS = {
            "BNS": [r"\bbns(?:\s*,?\s*2023)?\b", r"\bbharatiya\s+nyaya\s+sanhita(?:\s*,?\s*2023)?\b"],
            "BNSS": [r"\bbnss(?:\s*,?\s*2023)?\b", r"\bbharatiya\s+nagarik\s+suraksha\s+sanhita(?:\s*,?\s*2023)?\b"],
            "BSA": [r"\bbsaa?(?:\s*,?\s*2023)?\b", r"\bbsa(?:\s*,?\s*2023)?\b", r"\bbharatiya\s+sakshya\s+adhiniyam(?:\s*,?\s*2023)?\b"],
            "IPC": [r"\bipc(?:\s*,?\s*1860)?\b", r"\bindian\s+penal\s+code(?:\s*,?\s*1860)?\b", r"\bpenal\s+code\b"],
            "CRPC": [r"\bcrpc(?:\s*,?\s*1973)?\b", r"\bcode\s+of\s+criminal\s+procedure(?:\s*,?\s*1973)?\b", r"\bcriminal\s+procedure\s+code\b"],
            "IEA": [r"\biea(?:\s*,?\s*1872)?\b", r"\bindian\s+evidence\s+act(?:\s*,?\s*1872)?\b", r"\bevidence\s+act(?:\s*,?\s*1872)?\b"],
            "IT_ACT": [r"\bit\s+act(?:\s*,?\s*2000)?\b", r"\binformation\s+technology\s+act(?:\s*,?\s*2000)?\b"],
            "COMPANIES_ACT_2013": [r"\bcompanies\s+act(?:\s*,?\s*2013)?\b", r"\bca\s*2013\b"],
            "CPC_1908": [r"\bcpc(?:\s*,?\s*1908)?\b", r"\bcode\s+of\s+civil\s+procedure\b"],
            "IBC_2016": [r"\bibc(?:\s*,?\s*2016)?\b", r"\binsolvency\s+and\s+bankruptcy\s+code\b"],
        }

        results = []

        # 1. Pattern: [ACT] [optional Section] [NUMBERS...]
        for act_pfx, patterns in ACT_PATTERNS.items():
            for pat in patterns:
                regex1 = rf'(?:{pat})\s*(?:,|under|in)?\s*(?:sections?|sec\.?|s\.?)?\s*([0-9]+[A-Za-z]*(?:[,\s/&]+(?:and\s+)?[0-9]+[A-Za-z]*)*)'
                for m in re.finditer(regex1, text, re.I):
                    num_block = m.group(1).strip()
                    nums = re.findall(r'\b[0-9]+[A-Za-z]*\b', num_block)
                    for n in nums:
                        if not (len(n) == 4 and n.isdigit() and int(n) in range(1800, 2030)):
                            results.append((act_pfx, n.upper(), "SECTION"))

                regex2 = rf'(?:sections?|sec\.?|s\.?)\s*([0-9]+[A-Za-z]*(?:[,\s/&]+(?:and\s+)?[0-9]+[A-Za-z]*)*)\s+(?:of\s+)?(?:the\s+)?(?:{pat})'
                for m in re.finditer(regex2, text, re.I):
                    num_block = m.group(1).strip()
                    nums = re.findall(r'\b[0-9]+[A-Za-z]*\b', num_block)
                    for n in nums:
                        if not (len(n) == 4 and n.isdigit() and int(n) in range(1800, 2030)):
                            results.append((act_pfx, n.upper(), "SECTION"))

        # 2. Check for bare section mentions that inherit the primary Act
        if results:
            primary_act = results[0][0]
            all_sec_matches = re.finditer(r'\b(?:sections?|sec\.?|s\.?)\s+([0-9]+[A-Za-z]*)\b', text, re.I)
            for m in all_sec_matches:
                sec_n = m.group(1).upper()
                if not (len(sec_n) == 4 and sec_n.isdigit() and int(sec_n) in range(1800, 2030)):
                    already_matched = any(item[1] == sec_n for item in results)
                    if not already_matched:
                        results.append((primary_act, sec_n, "SECTION"))

        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for item in results:
            key = (item[0], item[1])
            if key not in seen:
                seen.add(key)
                deduped.append(item)

        return deduped

