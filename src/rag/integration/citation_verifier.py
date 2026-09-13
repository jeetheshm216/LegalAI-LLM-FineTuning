"""
citation_verifier.py

Post-generation citation and statutory claim verification for LegalAI.
Extracts cited sections and enactments from the generated answer and validates
them against the retrieved authoritative chunks to prevent citation confabulation
and unsupported statutory claims.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple


@dataclass
class CitationVerificationResult:
    is_valid: bool
    cited_sections: List[str]
    supported_sections: List[str]
    unsupported_sections: List[str]
    hallucinated_provisions: List[str]
    verified_answer: str
    remediation_status: str


class StatutoryCitationVerifier:
    """Verifies that generated statutory claims match retrieved chunks and official enactments."""

    KNOWN_ACT_BOUNDS = {
        "BNS": 358,
        "BNSS": 531,
        "BSA": 170
    }

    def verify(
        self,
        answer: str,
        retrieved_chunks: List[Any],
        target_statute_code: Optional[str] = None
    ) -> CitationVerificationResult:
        """
        Parses all statutory citations from the generated answer and checks against retrieved chunks.
        """
        # Extract cited sections
        # e.g. "Section 103", "Section 482", "Section 63", "Section 505A", "Section 65B of the BSA"
        pattern = re.compile(r'\b(?:section|sec\.?|u/s|§)\s*([0-9]+[A-Za-z]*)', re.IGNORECASE)
        matches = pattern.findall(answer)
        cited_sections = list(dict.fromkeys(matches))  # deduplicate preserving order

        # Extract available sections from retrieved chunks
        retrieved_sections = set()
        retrieved_act_prefixes = set()
        for c in retrieved_chunks:
            sec = str(getattr(c, "section", "")).strip()
            if sec:
                retrieved_sections.add(sec.lower())
            act_p = getattr(c, "act_prefix", "").upper()
            if act_p:
                retrieved_act_prefixes.add(act_p)

        supported = []
        unsupported = []
        hallucinated = []

        for sec in cited_sections:
            sec_clean = sec.lower()

            # Check if section exceeds official enactment bounds
            sec_num = re.match(r'^([0-9]+)', sec)
            if sec_num:
                num_val = int(sec_num.group(1))
                # Check known criminal bounds
                if target_statute_code and target_statute_code in self.KNOWN_ACT_BOUNDS:
                    if num_val > self.KNOWN_ACT_BOUNDS[target_statute_code]:
                        hallucinated.append(f"Section {sec} (exceeds {target_statute_code} maximum of {self.KNOWN_ACT_BOUNDS[target_statute_code]})")
                        continue

            # Check if sec is in retrieved chunks
            if sec_clean in retrieved_sections:
                supported.append(sec)
            else:
                # Check for explicit hallucinations like 65B in BSA or 505A in BNS
                if "65b" in sec_clean and "bsa" in answer.lower():
                    hallucinated.append("Section 65B of BSA (non-existent provision; BSA equivalent is Section 63)")
                elif "505a" in sec_clean and "bns" in answer.lower():
                    hallucinated.append("Section 505A of BNS (non-existent provision)")
                elif "302b" in sec_clean and "bns" in answer.lower():
                    hallucinated.append("Section 302B of BNS (non-existent provision)")
                else:
                    unsupported.append(sec)

        # Decision
        if hallucinated:
            # Dangerous citation hallucination detected
            is_valid = False
            remediation = "HALLUCINATION_DETECTED"
            # Sanitize answer or replace with controlled rejection
            clean_answer = (
                f"Statutory Citation Warning: The generated answer referenced unverified or non-existent provisions: "
                f"{', '.join(hallucinated)}. "
                f"In accordance with strict legal fidelity rules, this citation cannot be validated from authoritative sources."
            )
        elif unsupported and not retrieved_sections:
            # Model generated sections without any retrieved chunks to back them up
            is_valid = False
            remediation = "UNSUPPORTED_CITATIONS"
            clean_answer = (
                "The available legal sources do not provide sufficient statutory evidence to support the cited section(s). "
                "The requested provision is outside the verified statutory corpus."
            )
        else:
            is_valid = True
            remediation = "VERIFIED_OR_PERMITTED"
            clean_answer = answer

        return CitationVerificationResult(
            is_valid=is_valid,
            cited_sections=cited_sections,
            supported_sections=supported,
            unsupported_sections=unsupported,
            hallucinated_provisions=hallucinated,
            verified_answer=clean_answer,
            remediation_status=remediation
        )
