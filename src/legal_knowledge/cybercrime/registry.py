"""Cybercrime domain taxonomy, legal registry, and multi-act mapping definitions for LegalAI.

Provides:
1. Formal Cybercrime taxonomy categories
2. Multi-Act association mappings (IT Act, BNS, BNSS, BSA, Subordinate Rules, Judgments, Guidance)
3. Source type classifications (STATUTE, JUDGMENT, REGULATION, NOTIFICATION, GOVERNMENT_GUIDANCE, ADVISORY)
4. Legal relationship types (CORRESPONDING, PARTIALLY_CORRESPONDING, RELATED, REPLACED_BY, NO_DIRECT_EQUIVALENT)
5. Query domain classification triggers
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set
import re


class SourceType(str, Enum):
    """Authoritative legal source classification."""
    STATUTE = "STATUTE"
    JUDGMENT = "JUDGMENT"
    REGULATION = "REGULATION"
    NOTIFICATION = "NOTIFICATION"
    GOVERNMENT_GUIDANCE = "GOVERNMENT_GUIDANCE"
    ADVISORY = "ADVISORY"


class LegalRelationshipType(str, Enum):
    """Explicit relationship types between historical and current legal provisions."""
    CORRESPONDING = "CORRESPONDING"
    PARTIALLY_CORRESPONDING = "PARTIALLY_CORRESPONDING"
    RELATED = "RELATED"
    REPLACED_BY = "REPLACED_BY"
    NO_DIRECT_EQUIVALENT = "NO_DIRECT_EQUIVALENT"


class CybercrimeCategory(str, Enum):
    COMPUTER_OFFENCES = "COMPUTER_OFFENCES"
    CYBER_FRAUD = "CYBER_FRAUD"
    IDENTITY_THEFT = "IDENTITY_THEFT"
    PERSONATION = "PERSONATION"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DATA_PRIVACY_OFFENCES = "DATA_PRIVACY_OFFENCES"
    ELECTRONIC_EVIDENCE = "ELECTRONIC_EVIDENCE"
    DIGITAL_EVIDENCE_PRESERVATION = "DIGITAL_EVIDENCE_PRESERVATION"
    INVESTIGATION_PROCEDURE = "INVESTIGATION_PROCEDURE"
    SEARCH_AND_SEIZURE = "SEARCH_AND_SEIZURE"
    INTERMEDIARY_LIABILITY = "INTERMEDIARY_LIABILITY"
    ONLINE_HARASSMENT = "ONLINE_HARASSMENT"
    CYBERSTALKING = "CYBERSTALKING"
    FINANCIAL_CYBERCRIME = "FINANCIAL_CYBERCRIME"
    PHISHING = "PHISHING"
    ONLINE_IMPERSONATION = "ONLINE_IMPERSONATION"
    CYBER_TERRORISM = "CYBER_TERRORISM"
    CRITICAL_INFRASTRUCTURE = "CRITICAL_INFRASTRUCTURE"
    OTHER_CYBER_OFFENCES = "OTHER_CYBER_OFFENCES"


# Cybercrime Domain Taxonomical Mapping to Acts & Provisions
CYBERCRIME_TAXONOMY_MAP: Dict[CybercrimeCategory, Dict[str, Any]] = {
    CybercrimeCategory.COMPUTER_OFFENCES: {
        "title": "Computer-Related Offences & System Tampering",
        "primary_statutory": [("IT_ACT", "43"), ("IT_ACT", "65"), ("IT_ACT", "66")],
        "related_substantive": [("BNS", "324"), ("BNS", "326")],
        "description": "Unauthorized alteration, damage, or disruption of computer systems, data, or source code."
    },
    CybercrimeCategory.CYBER_FRAUD: {
        "title": "Cyber Fraud & Online Deception",
        "primary_statutory": [("IT_ACT", "66D")],
        "related_substantive": [("BNS", "318"), ("BNS", "319")],
        "historical_substantive": [("IPC", "419"), ("IPC", "420")],
        "procedural": [("BNSS", "94"), ("BNSS", "105"), ("BNSS", "173")],
        "evidence": [("BSA", "61"), ("BSA", "62"), ("BSA", "63")],
        "guidance": ["I4C CFCFRMS SOP", "RBI Customer Protection Master Direction"],
        "description": "Financial and fraudulent deception perpetrated using computer systems, networks, or telecommunication."
    },
    CybercrimeCategory.IDENTITY_THEFT: {
        "title": "Identity Theft & Digital Credential Misuse",
        "primary_statutory": [("IT_ACT", "66C")],
        "related_substantive": [("BNS", "319"), ("BNS", "336"), ("BNS", "340")],
        "historical_substantive": [("IPC", "419"), ("IPC", "468")],
        "description": "Fraudulent or dishonest use of electronic signatures, passwords, biometric identifiers, or personal data."
    },
    CybercrimeCategory.PERSONATION: {
        "title": "Personation & Online Impersonation",
        "primary_statutory": [("IT_ACT", "66D")],
        "related_substantive": [("BNS", "319")],
        "historical_substantive": [("IPC", "419")],
        "description": "Cheating by personating another person through computer resources, email, or communication devices."
    },
    CybercrimeCategory.UNAUTHORIZED_ACCESS: {
        "title": "Unauthorized Access, Hacking & Extraction",
        "primary_statutory": [("IT_ACT", "43"), ("IT_ACT", "66")],
        "description": "Accessing, downloading, copying, or extracting data or computer systems without permission."
    },
    CybercrimeCategory.DATA_PRIVACY_OFFENCES: {
        "title": "Data Protection & Privacy Breaches",
        "primary_statutory": [("IT_ACT", "43A"), ("IT_ACT", "72"), ("IT_ACT", "72A")],
        "precedents": ["K.S. Puttaswamy v. Union of India (2017) 10 SCC 1"],
        "description": "Failure to protect sensitive personal data, breach of confidentiality, or disclosure in breach of lawful contract."
    },
    CybercrimeCategory.ELECTRONIC_EVIDENCE: {
        "title": "Electronic & Digital Evidence Admissibility",
        "current_statutory": [("BSA", "61"), ("BSA", "62"), ("BSA", "63")],
        "historical_statutory": [("IEA", "65A"), ("IEA", "65B")],
        "precedents": [
            "Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal (2020) 7 SCC 1",
            "Anvar P.V. v. P.K. Basheer (2014) 10 SCC 473",
            "Shafhi Mohammad v. State of H.P. (2018) 2 SCC 801 [Overruled]"
        ],
        "description": "Admissibility, certificate conditions, preservation, integrity, and proof of secondary electronic records."
    },
    CybercrimeCategory.DIGITAL_EVIDENCE_PRESERVATION: {
        "title": "Digital Evidence Preservation & Intermediary Traffic Data",
        "primary_statutory": [("IT_ACT", "67C"), ("BNSS", "94")],
        "historical_statutory": [("CrPC", "91")],
        "regulations": ["Information Technology (Intermediary Guidelines) Rules, 2021", "CERT-In Directions 2022"],
        "description": "Preservation of internet logs, subscriber records, server data, and traffic information by service providers."
    },
    CybercrimeCategory.INVESTIGATION_PROCEDURE: {
        "title": "Cybercrime Investigation & Forensic Procedure",
        "primary_statutory": [("IT_ACT", "78"), ("IT_ACT", "80"), ("BNSS", "173"), ("BNSS", "176")],
        "historical_statutory": [("CrPC", "154"), ("CrPC", "156"), ("CrPC", "161")],
        "description": "Investigative powers of police officers (minimum rank DSP/ACP under IT Act Sec 78), e-FIR, and procedure."
    },
    CybercrimeCategory.SEARCH_AND_SEIZURE: {
        "title": "Digital Search & Seizure and Device Forensics",
        "primary_statutory": [("BNSS", "105"), ("BNSS", "106"), ("IT_ACT", "80")],
        "historical_statutory": [("CrPC", "100"), ("CrPC", "102")],
        "description": "Statutory rules for searching computer premises, seizing digital devices, and mandatory audio-video recording."
    },
    CybercrimeCategory.INTERMEDIARY_LIABILITY: {
        "title": "Intermediary Liability, Safe Harbor & Due Diligence",
        "primary_statutory": [("IT_ACT", "79")],
        "precedents": ["Shreya Singhal v. Union of India (2015) 5 SCC 1"],
        "regulations": ["Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021"],
        "description": "Exemption from liability for intermediaries subject to due diligence and court/government takedown notices."
    },
    CybercrimeCategory.ONLINE_HARASSMENT: {
        "title": "Online Harassment, Obscenity & CSAM",
        "primary_statutory": [("IT_ACT", "67"), ("IT_ACT", "67A"), ("IT_ACT", "67B")],
        "related_substantive": [("BNS", "78"), ("BNS", "79"), ("POCSO_ACT_2012", "15")],
        "historical_substantive": [("IPC", "354D"), ("IPC", "509")],
        "precedents": ["Shreya Singhal v. Union of India (2015) 5 SCC 1 [Section 66A struck down]"],
        "description": "Transmission of obscene content, sexually explicit acts, child sexual abuse material, or cyber harassment."
    },
    CybercrimeCategory.FINANCIAL_CYBERCRIME: {
        "title": "Financial Cybercrime & Banking Fraud",
        "primary_statutory": [("IT_ACT", "66D")],
        "related_substantive": [("BNS", "318"), ("BNS", "319")],
        "regulations": ["RBI Master Direction on Customer Protection ??? Limiting Liability in Unauthorised Electronic Banking Transactions"],
        "guidance": ["I4C SOP on National Cyber Crime Reporting Portal (Helpline 1930 & CFCFRMS)"],
        "description": "UPI fraud, unauthorized net banking, phishing scams, SIM swapping, and customer liability."
    },
    CybercrimeCategory.CYBER_TERRORISM: {
        "title": "Cyber Terrorism",
        "primary_statutory": [("IT_ACT", "66F")],
        "description": "Acts with intent to threaten the unity, integrity, security, or sovereignty of India via computer resources."
    },
    CybercrimeCategory.CRITICAL_INFRASTRUCTURE: {
        "title": "Protected Systems & CERT-In Compliance",
        "primary_statutory": [("IT_ACT", "70"), ("IT_ACT", "70B")],
        "regulations": ["CERT-In Directions under Section 70B(6) on Information Security Practices (2022)"],
        "description": "Protected systems, critical information infrastructure, and mandatory reporting of cybersecurity incidents."
    }
}

# Regex triggers for detecting cybercrime domains
CYBERCRIME_KEYWORD_TRIGGERS: List[Dict[str, Any]] = [
    {
        "category": CybercrimeCategory.ELECTRONIC_EVIDENCE,
        "patterns": [
            r"\belectronic\s+(?:evidence|record|records|document|documents)\b",
            r"\bdigital\s+evidence\b",
            r"\bsection\s*65b\b",
            r"\bsec\.?\s*65b\b",
            r"\bsection\s*63\s+(?:bsa|bharatiya\s+sakshya)\b",
            r"\bcertificate\s+under\s+section\s*65b\b",
            r"\b65b\s+certificate\b",
            r"\badmissibility\s+of\s+electronic\b",
            r"\bhash\s+value\b",
            r"\barjun\s+panditrao\b",
            r"\banvar\s+p\.?v\.?\b"
        ]
    },
    {
        "category": CybercrimeCategory.CYBER_FRAUD,
        "patterns": [
            r"\bcyber\s+fraud\b",
            r"\bonline\s+(?:fraud|scam|financial\s+fraud|banking\s+fraud)\b",
            r"\bphishing\b",
            r"\bonline\s+cheating\b",
            r"\bupi\s+fraud\b",
            r"\bsim\s+swap(?:ping)?\b",
            r"\bfinancial\s+cyber\b",
            r"\bsection\s*66d\b"
        ]
    },
    {
        "category": CybercrimeCategory.IDENTITY_THEFT,
        "patterns": [
            r"\bidentity\s+theft\b",
            r"\bsteal(?:ing)?\s+(?:identity|password|credentials|digital\s+signature)\b",
            r"\bsection\s*66c\b",
            r"\bsec\.?\s*66c\b"
        ]
    },
    {
        "category": CybercrimeCategory.PERSONATION,
        "patterns": [
            r"\bpersonat(?:ion|ing)\s+using\s+computer\b",
            r"\bonline\s+impersonation\b",
            r"\bimpersonat(?:ion|ing)\s+online\b",
            r"\bcheating\s+by\s+personation\b"
        ]
    },
    {
        "category": CybercrimeCategory.INTERMEDIARY_LIABILITY,
        "patterns": [
            r"\bintermediar(?:y|ies)\b",
            r"\bsafe\s+harbor\b",
            r"\bsection\s*79\b",
            r"\bit\s+rules\s*2021\b",
            r"\bshreya\s+singhal\b",
            r"\btakedown\s+notice\b"
        ]
    },
    {
        "category": CybercrimeCategory.INVESTIGATION_PROCEDURE,
        "patterns": [
            r"\binvestigat(?:ion|ing)\s+(?:of\s+)?(?:a\s+)?cybercrime\b",
            r"\bcyber\s+investigation\b",
            r"\be-?fir\b",
            r"\baudio-?video\s+(?:electronic\s+means|recording)\b",
            r"\bdigital\s+seizure\b",
            r"\bsection\s*78\s+it\s+act\b",
            r"\bsection\s*105\s+bnss\b"
        ]
    },
    {
        "category": CybercrimeCategory.ONLINE_HARASSMENT,
        "patterns": [
            r"\bobscene\s+(?:material|content)\s+in\s+electronic\s+form\b",
            r"\bsexually\s+explicit\s+act\b",
            r"\bchild\s+pornography\b",
            r"\bcsam\b",
            r"\bcyber\s*stalking\b",
            r"\bsection\s*67[ab]?\b"
        ]
    },
    {
        "category": CybercrimeCategory.CYBER_TERRORISM,
        "patterns": [
            r"\bcyber\s+terrorism\b",
            r"\bsection\s*66f\b"
        ]
    },
    {
        "category": CybercrimeCategory.DATA_PRIVACY_OFFENCES,
        "patterns": [
            r"\bbreach\s+of\s+confidentiality\b",
            r"\bsection\s*72[a]?\b",
            r"\bsection\s*43a\b",
            r"\bfailure\s+to\s+protect\s+data\b",
            r"\bputtaswamy\b"
        ]
    }
]


def detect_cybercrime_domains(query: str) -> List[CybercrimeCategory]:
    """Detects matching cybercrime categories from query text."""
    matches: Set[CybercrimeCategory] = set()
    cleaned = query.lower()
    
    # Check general cybercrime trigger terms
    is_general_cyber = bool(re.search(r'\b(?:cyber|cybercrime|it\s+act|computer\s+resource|electronic\s+record)\b', cleaned, re.I))
    
    for item in CYBERCRIME_KEYWORD_TRIGGERS:
        cat = item["category"]
        for pat in item["patterns"]:
            if re.search(pat, cleaned, re.I):
                matches.add(cat)
                break
                
    if is_general_cyber and not matches:
        matches.add(CybercrimeCategory.COMPUTER_OFFENCES)
        
    return list(matches)


def get_multi_act_retrieval_targets(categories: List[CybercrimeCategory]) -> Dict[str, Any]:
    """Resolves multi-act retrieval targets for detected cybercrime categories."""
    acts_to_query: Set[str] = set()
    specific_sections: Dict[str, Set[str]] = {}
    precedents: Set[str] = set()
    guidance: Set[str] = set()
    
    for cat in categories:
        meta = CYBERCRIME_TAXONOMY_MAP.get(cat, {})
        for key in ["primary_statutory", "current_statutory", "related_substantive", "procedural", "evidence"]:
            pairs = meta.get(key, [])
            for act, sec in pairs:
                acts_to_query.add(act)
                specific_sections.setdefault(act, set()).add(sec)
                
        for prec in meta.get("precedents", []):
            precedents.add(prec)
            
        for g in meta.get("guidance", []):
            guidance.add(g)
            
    return {
        "acts": list(acts_to_query),
        "provisions": {act: list(secs) for act, secs in specific_sections.items()},
        "precedents": list(precedents),
        "guidance": list(guidance)
    }

