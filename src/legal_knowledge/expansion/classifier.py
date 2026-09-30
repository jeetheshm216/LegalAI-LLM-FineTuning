"""Conservative domain classifier for Indian Central and State Acts."""

import re
from typing import Tuple
from ..models import LegalDomain


class IndianDomainClassifier:
    """Classifies an Act into a standard Indian legal domain based on high-confidence title and statutory markers."""

    DOMAIN_RULES = [
        # Criminal Law & Offences
        (r'\b(?:penal|nyaya\s+sanhita|crimes?|criminal\s+law|pocso|sexual\s+offences?|atrocities|narcotic|ndps|money[\s-]laundering|pmla|corruption|terrorist|uapa)\b', LegalDomain.CRIMINAL.value),
        # Criminal Procedure
        (r'\b(?:nagarik\s+suraksha|criminal\s+procedure|crpc|extradition|prison|prisoners)\b', LegalDomain.PROCEDURAL.value),
        # Evidence
        (r'\b(?:sakshya|evidence)\b', LegalDomain.EVIDENCE.value),
        # Constitutional
        (r'\b(?:constitution|citizenship|representation\s+of\s+the\s+people|delimitation|official\s+languages)\b', LegalDomain.CONSTITUTIONAL.value),
        # Corporate Law
        (r'\b(?:companies|limited\s+liability\s+partnership|llp|securities|sebi|depositories)\b', LegalDomain.CORPORATE.value),
        # Insolvency & Bankruptcy
        (r'\b(?:insolvency|bankruptcy|ibc|sick\s+industrial)\b', LegalDomain.INSOLVENCY.value),
        # Arbitration & Alternative Dispute Resolution
        (r'\b(?:arbitration|conciliation|mediation|lok\s+adalat|legal\s+services\s+authorities)\b', LegalDomain.ARBITRATION.value),
        # Consumer Protection
        (r'\b(?:consumer\s+protection|standard\s+of\s+weights|bureau\s+of\s+indian\s+standards|food\s+safety)\b', LegalDomain.CONSUMER.value),
        # Property Law
        (r'\b(?:transfer\s+of\s+property|easements|registration|stamp|land\s+acquisition|rera|real\s+estate)\b', LegalDomain.PROPERTY.value),
        # Civil Procedure
        (r'\b(?:civil\s+procedure|cpc|court\s+fees|suits\s+valuation)\b', LegalDomain.CIVIL.value),
        # Contract & Commercial
        (r'\b(?:contract|sale\s+of\s+goods|partnership|specific\s+relief)\b', LegalDomain.CONTRACT.value),
        # Banking & Finance
        (r'\b(?:banking|reserve\s+bank|rbi|negotiable\s+instruments|sarfaesi|debt\s+recovery|foreign\s+exchange|fema)\b', LegalDomain.BANKING_FINANCE.value),
        # Tax Law
        (r'\b(?:income\s+tax|goods\s+and\s+services\s+tax|gst|customs|central\s+excise)\b', LegalDomain.TAX.value),
        # Labour & Employment
        (r'\b(?:industrial\s+disputes|factories|payment\s+of\s+wages|minimum\s+wages|workmen|provident\s+fund|gratuity|maternity|posh)\b', LegalDomain.LABOUR.value),
        # Intellectual Property
        (r'\b(?:copyright|patents|trade\s*marks|designs|geographical\s+indications)\b', LegalDomain.INTELLECTUAL_PROPERTY.value),
        # Cyber & Technology
        (r'\b(?:information\s+technology|data\s+protection|dpdp|digital|cyber|telecom|trai)\b', LegalDomain.CYBER_TECH.value),
        # Family & Personal Law
        (r'\b(?:hindu\s+marriage|hindu\s+succession|special\s+marriage|divorce|guardians|maintenance|domestic\s+violence)\b', LegalDomain.FAMILY.value),
        # Motor Vehicles
        (r'\b(?:motor\s+vehicles?|road\s+safety|national\s+highways)\b', LegalDomain.MOTOR_VEHICLES.value),
        # Environmental
        (r'\b(?:environment|air\s+prevention|water\s+prevention|forest|wildlife|national\s+green\s+tribunal|ngt)\b', LegalDomain.ENVIRONMENTAL.value),
    ]

    def classify_act(self, act_title: str, text_sample: str = "") -> Tuple[str, float]:
        """
        Classifies an Act into an Indian legal domain with confidence score.
        Defaults to 'Other / Unclassified' if confidence is low.
        """
        title_lower = act_title.lower()

        # Check title first (highest confidence)
        for pattern, domain in self.DOMAIN_RULES:
            if re.search(pattern, title_lower):
                return domain, 0.95

        # Check initial text sample if provided
        if text_sample:
            sample_lower = text_sample[:2000].lower()
            for pattern, domain in self.DOMAIN_RULES:
                if re.search(pattern, sample_lower):
                    return domain, 0.75

        # Safe fallback: Do not hallucinate or guess
        return "Other / Unclassified", 0.0
