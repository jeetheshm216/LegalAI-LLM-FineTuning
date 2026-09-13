"""
domain_detector.py

Comprehensive legal domain and statute detection for LegalAI RAG.
Identifies whether a legal query belongs to the 3-Act RAG corpus (BNS, BNSS, BSA)
or requires an external statute (Constitution, NI Act, IT Act, RERA, DPDP, etc.).
Prevents wrong-domain retrieval and unauthorized cross-statute confabulation.
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class DomainDetectionResult:
    detected_domain: str
    target_statute: Optional[str]
    statute_code: Optional[str]
    is_in_corpus: bool
    specific_provision: Optional[str]
    confidence: float
    explanation: str


class LegalDomainDetector:
    """Classifies legal queries into domain and identifies applicable enactments."""

    # Corpus enactments
    IN_CORPUS_ACTS = {
        "BNS": {
            "name": "The Bharatiya Nyaya Sanhita, 2023",
            "code": "BNS",
            "type": "SUBSTANTIVE_CRIMINAL",
            "max_section": 358
        },
        "BNSS": {
            "name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
            "code": "BNSS",
            "type": "CRIMINAL_PROCEDURE",
            "max_section": 531
        },
        "BSA": {
            "name": "The Bharatiya Sakshya Adhiniyam, 2023",
            "code": "BSA",
            "type": "EVIDENCE",
            "max_section": 170
        }
    }

    # External out-of-corpus statutes and their trigger patterns
    OUT_OF_CORPUS_RULES: List[Dict[str, Any]] = [
        {
            "domain": "Constitutional Law",
            "statute": "Constitution of India",
            "code": "CONSTITUTION",
            "patterns": [
                r'\barticle\s+(?:[1-9][0-9]{0,2}[A-Za-z]?)\b',
                r'\bconstitution\s+of\s+india\b',
                r'\bconstitutional\b',
                r'\bfundamental\s+rights?\b',
                r'\bdirective\s+principles?\b',
                r'\bwrit\s+(?:petition|of\s+habeas|of\s+mandamus|of\s+certiorari|of\s+prohibition|of\s+quo\s+warranto)\b',
                r'\barticle\s+21\b',
                r'\barticle\s+19\b',
                r'\barticle\s+14\b',
                r'\barticle\s+32\b',
                r'\barticle\s+226\b',
                r'\bpreamble\b',
            ]
        },
        {
            "domain": "Negotiable Instruments / Banking",
            "statute": "Negotiable Instruments Act, 1881",
            "code": "NI_ACT",
            "patterns": [
                r'\bsection\s+138\b',
                r'\bsec(?:tion)?\.?\s*138\b',
                r'\bcheque\s+(?:bounce|dishonour|dishonor)\b',
                r'\bnegotiable\s+instruments?\b',
                r'\bdrawer\s+of\s+(?:a\s+)?cheque\b',
                r'\bstatutory\s+notice\s+under\s+138\b',
                r'\b15\s+days?\s+notice\s+period\s+for\s+cheque\b',
            ]
        },
        {
            "domain": "Information Technology / Cyber Law",
            "statute": "Information Technology Act, 2000",
            "code": "IT_ACT",
            "patterns": [
                r'\bsection\s+79\b',
                r'\bsection\s+66[A-F]?\b',
                r'\binformation\s+technology\s+act\b',
                r'\bit\s+act\b',
                r'\bintermediary\s+liability\b',
                r'\bsafe\s+harbour\b',
                r'\bcyber\s+(?:crime|security|appellate)\b',
                r'\bdigital\s+signatures?\b',
            ]
        },
        {
            "domain": "Contract Law",
            "statute": "Indian Contract Act, 1872",
            "code": "CONTRACT_ACT",
            "patterns": [
                r'\bcontract\s+act\b',
                r'\bindian\s+contract\s+act\b',
                r'\bsection\s+74\b',
                r'\bsection\s+73\b',
                r'\bsection\s+27\b',
                r'\bsection\s+23\b',
                r'\bemployment\s+bonds?\b',
                r'\brestraint\s+of\s+trade\b',
                r'\bliquidated\s+damages\b',
                r'\bquantum\s+meruit\b',
                r'\bfrustration\s+of\s+contract\b',
                r'\bforce\s+majeure\b',
                r'\bnon-compete\s+clause\b',
                r'\bvalid\s+contract\s+elements?\b',
            ]
        },
        {
            "domain": "Real Estate / Housing",
            "statute": "Real Estate (Regulation and Development) Act, 2016",
            "code": "RERA",
            "patterns": [
                r'\brera\b',
                r'\breal\s+estate\s+\(regulation\b',
                r'\ballottee\b',
                r'\bbuilder\s+delay\b',
                r'\bpossession\s+delay\b',
                r'\breal\s+estate\s+regulatory\s+authority\b',
            ]
        },
        {
            "domain": "Data Protection / Privacy",
            "statute": "Digital Personal Data Protection Act, 2023",
            "code": "DPDP",
            "patterns": [
                r'\bdpdp\b',
                r'\bdigital\s+personal\s+data\s+protection\b',
                r'\bdata\s+fiduciary\b',
                r'\bdata\s+principal\b',
                r'\bconsent\s+manager\b',
                r'\bpersonal\s+data\s+breach\b',
            ]
        },
        {
            "domain": "Right to Information",
            "statute": "Right to Information Act, 2005",
            "code": "RTI",
            "patterns": [
                r'\brti\s+act\b',
                r'\bright\s+to\s+information\b',
                r'\bpublic\s+information\s+officer\b',
                r'\bcentral\s+information\s+commission\b',
                r'\brti\s+response\s+deadline\b',
                r'\b30\s+days?\s+deadline\s+for\s+rti\b',
            ]
        },
        {
            "domain": "Intellectual Property",
            "statute": "Trade Marks Act, 1999 / Patents Act, 1970 / Copyright Act, 1957",
            "code": "IPR",
            "patterns": [
                r'\btrade\s*marks?\b',
                r'\btrade\s*marks?\s+act\b',
                r'\bpatents?\b',
                r'\bpatents?\s+act\b',
                r'\bcopyrights?\b',
                r'\binventive\s+step\b',
                r'\bprior\s+art\b',
                r'\bdeceptive\s+similarity\b',
                r'\bpassing\s+off\b',
                r'\bpatentability\b',
                r'\bdescriptive\s+word\s+as\s+trademark\b',
            ]
        },
        {
            "domain": "Company / Corporate Law",
            "statute": "Companies Act, 2013 / Insolvency and Bankruptcy Code, 2016",
            "code": "COMPANY_LAW",
            "patterns": [
                r'\bcompanies\s+act\b',
                r'\bcorporate\s+governance\b',
                r'\bdirector\s+disqualification\b',
                r'\bindependent\s+directors?\b',
                r'\bnclt\b',
                r'\binsolvency\s+and\s+bankruptcy\b',
                r'\bibc\b',
                r'\bcorporate\s+debtor\b',
                r'\bcsr\s+spending\b',
            ]
        },
        {
            "domain": "Consumer Protection",
            "statute": "Consumer Protection Act, 2019",
            "code": "CONSUMER_LAW",
            "patterns": [
                r'\bconsumer\s+protection\b',
                r'\bconsumer\s+protection\s+act\b',
                r'\bconsumer\s+forum\b',
                r'\bdistrict\s+commission\b',
                r'\bstate\s+commission\b',
                r'\bunfair\s+trade\s+practice\b',
                r'\bdeficiency\s+in\s+service\b',
                r'\bpecuniary\s+jurisdiction\b',
            ]
        },
        {
            "domain": "Arbitration / Civil Procedure",
            "statute": "Arbitration and Conciliation Act, 1996 / Code of Civil Procedure, 1908",
            "code": "ARBITRATION_CIVIL",
            "patterns": [
                r'\barbitration\s+and\s+conciliation\b',
                r'\barbitration\s+act\b',
                r'\barbitral\s+tribunal\b',
                r'\bsection\s+9\s+arbitration\b',
                r'\bsection\s+11\s+arbitration\b',
                r'\bsection\s+34\b',
                r'\bsetting\s+aside\s+arbitral\s+award\b',
                r'\bcode\s+of\s+civil\s+procedure\b',
                r'\bcpc\b',
                r'\bres\s+judicata\b',
                r'\border\s+xxxix\b',
            ]
        },
        {
            "domain": "Labour & Employment Law",
            "statute": "Industrial Disputes Act / Payment of Wages / Gratuity Act",
            "code": "LABOUR_LAW",
            "patterns": [
                r'\bindustrial\s+disputes\b',
                r'\bpayment\s+of\s+wages\b',
                r'\bpayment\s+of\s+gratuity\b',
                r'\bretrenchment\b',
                r'\blay-off\b',
                r'\bworkman\s+definition\b',
                r'\bdeduct\s+salary\s+for\s+absence\b',
            ]
        },
        {
            "domain": "Family & Succession Law",
            "statute": "Hindu Marriage Act, 1955 / Special Marriage Act, 1954 / Succession Acts",
            "code": "FAMILY_LAW",
            "patterns": [
                r'\bhindu\s+marriage\s+act\b',
                r'\bspecial\s+marriage\s+act\b',
                r'\bhindu\s+succession\s+act\b',
                r'\bcoparcenary\b',
                r'\bmutual\s+consent\s+divorce\b',
                r'\bcooling-off\s+period\b',
                r'\bmaintenance\s+under\s+hindu\b',
            ]
        },
        {
            "domain": "Property & Tenancy Law",
            "statute": "Transfer of Property Act, 1882",
            "code": "PROPERTY_LAW",
            "patterns": [
                r'\btransfer\s+of\s+property\s+act\b',
                r'\btpa\b',
                r'\bsection\s+106\b',
                r'\bnotice\s+to\s+quit\b',
                r'\blease\s+termination\b',
                r'\bmortgage\b',
                r'\bdoctrine\s+of\s+lis\s+pendens\b',
                r'\bpart\s+performance\b',
            ]
        },
        {
            "domain": "Taxation Law",
            "statute": "Income Tax Act, 1961 / Central Goods and Services Tax Act, 2017",
            "code": "TAX_LAW",
            "patterns": [
                r'\bincome\s+tax\s+act\b',
                r'\bgst\b',
                r'\bgoods\s+and\s+services\s+tax\b',
                r'\bsingle\s+flat\s+gst\s+rate\b',
                r'\bsection\s+80c\b',
                r'\badvance\s+tax\b',
            ]
        }
    ]

    def detect(self, question: str) -> DomainDetectionResult:
        """
        Analyzes a legal question to identify target domain and statute authority.
        """
        q_clean = question.strip()

        # 1. First check explicit in-corpus statutes
        bns_match = re.search(r'\bBNS\b|bharatiya nyaya', q_clean, re.IGNORECASE)
        bnss_match = re.search(r'\bBNSS\b|bharatiya nagarik', q_clean, re.IGNORECASE)
        bsa_match = re.search(r'\bBSA\b|bharatiya sakshya', q_clean, re.IGNORECASE)

        # Extract explicit section if mentioned
        sec_m = re.search(r'(?:section|sec\.?|u/s|§)\s*([0-9]+[A-Za-z]*)', q_clean, re.IGNORECASE)
        sec_str = sec_m.group(1) if sec_m else None

        # Check for legacy criminal statutes (IPC, CrPC, IEA) which map to in-corpus concordance
        ipc_m = re.search(r'\b(?:IPC|indian penal code)\b', q_clean, re.IGNORECASE)
        crpc_m = re.search(r'\b(?:CrPC|code of criminal procedure)\b', q_clean, re.IGNORECASE)
        iea_m = re.search(r'\b(?:IEA|indian evidence act|evidence act)\b', q_clean, re.IGNORECASE)

        # Check for explicit out-of-corpus rules
        for rule in self.OUT_OF_CORPUS_RULES:
            for pattern in rule["patterns"]:
                if re.search(pattern, q_clean, re.IGNORECASE):
                    # Found explicit external statute reference
                    # Ensure it's not simply mentioning BSA vs Evidence Act comparison
                    if rule["code"] == "FAMILY_LAW" and (bns_match or bnss_match):
                        continue
                    if rule["code"] == "CONSTITUTION" and "article 20" in q_clean.lower() and (ipc_m or bns_match):
                        # Transition question involving Article 20(1) with criminal code
                        return DomainDetectionResult(
                            detected_domain="Criminal Law / Constitutional Non-Retroactivity",
                            target_statute="Bharatiya Nyaya Sanhita, 2023 / Article 20(1) Transition",
                            statute_code="BNS_TEMPORAL",
                            is_in_corpus=True,
                            specific_provision=sec_str,
                            confidence=0.95,
                            explanation="Query concerns substantive criminal liability transition under Article 20(1)."
                        )

                    return DomainDetectionResult(
                        detected_domain=rule["domain"],
                        target_statute=rule["statute"],
                        statute_code=rule["code"],
                        is_in_corpus=False,
                        specific_provision=sec_str,
                        confidence=0.95,
                        explanation=f"Query explicitly addresses {rule['statute']}, which is outside the current 3-Act (BNS/BNSS/BSA) RAG corpus."
                    )

        # 2. Check in-corpus triggers
        if bns_match:
            return DomainDetectionResult(
                detected_domain="Substantive Criminal Law",
                target_statute=self.IN_CORPUS_ACTS["BNS"]["name"],
                statute_code="BNS",
                is_in_corpus=True,
                specific_provision=sec_str,
                confidence=0.98,
                explanation="Query explicitly targets the Bharatiya Nyaya Sanhita, 2023."
            )
        if bnss_match:
            return DomainDetectionResult(
                detected_domain="Criminal Procedure",
                target_statute=self.IN_CORPUS_ACTS["BNSS"]["name"],
                statute_code="BNSS",
                is_in_corpus=True,
                specific_provision=sec_str,
                confidence=0.98,
                explanation="Query explicitly targets the Bharatiya Nagarik Suraksha Sanhita, 2023."
            )
        if bsa_match:
            return DomainDetectionResult(
                detected_domain="Evidence Law",
                target_statute=self.IN_CORPUS_ACTS["BSA"]["name"],
                statute_code="BSA",
                is_in_corpus=True,
                specific_provision=sec_str,
                confidence=0.98,
                explanation="Query explicitly targets the Bharatiya Sakshya Adhiniyam, 2023."
            )

        # 3. Check legacy criminal transitions
        if ipc_m or "murder" in q_clean.lower() or "theft" in q_clean.lower() or "dowry death" in q_clean.lower() or "rape" in q_clean.lower() or "sedition" in q_clean.lower():
            return DomainDetectionResult(
                detected_domain="Substantive Criminal Law",
                target_statute=self.IN_CORPUS_ACTS["BNS"]["name"],
                statute_code="BNS",
                is_in_corpus=True,
                specific_provision=sec_str,
                confidence=0.85,
                explanation="Query concerns substantive criminal offenses mapped to BNS 2023."
            )

        if crpc_m or "anticipatory bail" in q_clean.lower() or "remand" in q_clean.lower() or "police custody" in q_clean.lower() or "zero fir" in q_clean.lower():
            return DomainDetectionResult(
                detected_domain="Criminal Procedure",
                target_statute=self.IN_CORPUS_ACTS["BNSS"]["name"],
                statute_code="BNSS",
                is_in_corpus=True,
                specific_provision=sec_str,
                confidence=0.85,
                explanation="Query concerns criminal procedure mapped to BNSS 2023."
            )

        if iea_m or "electronic record" in q_clean.lower() or "secondary evidence" in q_clean.lower() or "confession to police" in q_clean.lower():
            return DomainDetectionResult(
                detected_domain="Evidence Law",
                target_statute=self.IN_CORPUS_ACTS["BSA"]["name"],
                statute_code="BSA",
                is_in_corpus=True,
                specific_provision=sec_str,
                confidence=0.85,
                explanation="Query concerns evidence rules mapped to BSA 2023."
            )

        # 4. Default: Ambiguous / General legal query
        return DomainDetectionResult(
            detected_domain="General / Ambiguous Legal Domain",
            target_statute=None,
            statute_code=None,
            is_in_corpus=False,
            specific_provision=sec_str,
            confidence=0.50,
            explanation="Query does not contain explicit criminal law keywords and may be outside the 3-Act corpus."
        )
