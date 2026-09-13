"""Statutory concordance system between legacy codes and 2023 enactments.

Strict Safety Rule:
Mappings must be verified against authoritative parliamentary comparative tables.
Unverified mappings are marked 'UNVERIFIED' and strictly blocked from authoritative retrieval.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any


@dataclass
class ConcordanceMapping:
    legacy_act: str
    legacy_section: str
    modern_act: str
    modern_section: str
    mapping_type: str  # EQUIVALENT, SUBDIVISION, EXPANDED_EQUIVALENT, SUBSTITUTED_RESTRUCTURED
    authority: str
    verification_status: str  # VERIFIED_STATUTORY_CONCORDANCE or UNVERIFIED
    notes: Optional[str] = None


# Authoritative parliamentary comparative concordance table
AUTHORITATIVE_CONCORDANCE: List[ConcordanceMapping] = [
    # IPC -> BNS
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="302",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="103",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 246) & BNS 2023 Schedule",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Punishment for murder. Section 103(1) covers individual; 103(2) covers mob lynching."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="300",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="101",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 246)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Definition of Murder and exceptions."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="299",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="100",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 246)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Culpable homicide not amounting to murder definition."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="304B",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="80",
        mapping_type="EQUIVALENT",
        authority="Ministry of Home Affairs Legislative Concordance Table 2023",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Dowry death."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="376",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="64",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 246)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Punishment for rape."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="420",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="318(4)",
        mapping_type="SUBDIVISION",
        authority="Ministry of Home Affairs Legislative Concordance Table 2023",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Cheating and dishonestly inducing delivery of property."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="498A",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="85",
        mapping_type="EQUIVALENT",
        authority="Ministry of Home Affairs Legislative Concordance Table 2023",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Husband or relative of husband of a woman subjecting her to cruelty."
    ),
    ConcordanceMapping(
        legacy_act="Indian Penal Code, 1860",
        legacy_section="124A",
        modern_act="Bharatiya Nyaya Sanhita, 2023",
        modern_section="152",
        mapping_type="SUBSTITUTED_RESTRUCTURED",
        authority="Parliamentary Standing Committee on Home Affairs (Report 246)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Sedition repealed; substituted with acts endangering sovereignty, unity and integrity of India."
    ),

    # CrPC -> BNSS
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="438",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="482",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247) & BNSS 2023 Schedule",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Direction for grant of bail to person apprehending arrest (Anticipatory bail)."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="482",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="528",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Saving of inherent powers of High Court."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="167",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="187",
        mapping_type="EXPANDED_EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Procedure when investigation cannot be completed in twenty-four hours (Remand/Custody)."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="173",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="193",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Report of police officer on completion of investigation."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="125",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="144",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Order for maintenance of wives, children and parents."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="154",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="173",
        mapping_type="EXPANDED_EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Information in cognizable cases (FIR), including e-FIR provisions."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="437",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="480",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="When bail may be taken in case of non-bailable offence."
    ),
    ConcordanceMapping(
        legacy_act="Code of Criminal Procedure, 1973",
        legacy_section="439",
        modern_act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        modern_section="483",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 247)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Special powers of High Court or Court of Session regarding bail."
    ),

    # IEA -> BSA
    ConcordanceMapping(
        legacy_act="Indian Evidence Act, 1872",
        legacy_section="65B",
        modern_act="Bharatiya Sakshya Adhiniyam, 2023",
        modern_section="63",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 248) & BSA 2023 Schedule",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Admissibility of electronic records and certificate requirement (Schedule Part A/B)."
    ),
    ConcordanceMapping(
        legacy_act="Indian Evidence Act, 1872",
        legacy_section="25",
        modern_act="Bharatiya Sakshya Adhiniyam, 2023",
        modern_section="23(1)",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 248)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Confession to police officer not to be proved."
    ),
    ConcordanceMapping(
        legacy_act="Indian Evidence Act, 1872",
        legacy_section="27",
        modern_act="Bharatiya Sakshya Adhiniyam, 2023",
        modern_section="23(2) proviso",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 248)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="How much of information received from accused may be proved (Recovery)."
    ),
    ConcordanceMapping(
        legacy_act="Indian Evidence Act, 1872",
        legacy_section="45",
        modern_act="Bharatiya Sakshya Adhiniyam, 2023",
        modern_section="39",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 248)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Opinions of experts."
    ),
    ConcordanceMapping(
        legacy_act="Indian Evidence Act, 1872",
        legacy_section="113A",
        modern_act="Bharatiya Sakshya Adhiniyam, 2023",
        modern_section="117",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 248)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Presumption as to abetment of suicide by married woman."
    ),
    ConcordanceMapping(
        legacy_act="Indian Evidence Act, 1872",
        legacy_section="113B",
        modern_act="Bharatiya Sakshya Adhiniyam, 2023",
        modern_section="118",
        mapping_type="EQUIVALENT",
        authority="Parliamentary Standing Committee on Home Affairs (Report 248)",
        verification_status="VERIFIED_STATUTORY_CONCORDANCE",
        notes="Presumption as to dowry death."
    )
]


class ConcordanceRegistry:
    """Manages statutory concordance lookups and verification guards."""

    def __init__(self, mappings: Optional[List[ConcordanceMapping]] = None):
        self.mappings = mappings or AUTHORITATIVE_CONCORDANCE

    def _matches_act(self, search_act: str, target_act: str) -> bool:
        s = search_act.lower().strip()
        t = target_act.lower().strip()
        if s in t or t in s:
            return True
        acronyms = {
            "ipc": "indian penal code",
            "crpc": "code of criminal procedure",
            "iea": "indian evidence act",
            "evidence act": "indian evidence act",
            "bns": "bharatiya nyaya sanhita",
            "bnss": "bharatiya nagarik suraksha sanhita",
            "bsa": "bharatiya sakshya adhiniyam"
        }
        for acr, full in acronyms.items():
            if (s == acr or acr in s) and full in t:
                return True
        return False

    def lookup_legacy_to_modern(self, legacy_act_fragment: str, legacy_section: str) -> Optional[ConcordanceMapping]:
        """Looks up a modern section given a legacy reference."""
        clean_sec = legacy_section.strip().lower()
        
        for m in self.mappings:
            if m.verification_status != "VERIFIED_STATUTORY_CONCORDANCE":
                continue
            if clean_sec == m.legacy_section.lower() and self._matches_act(legacy_act_fragment, m.legacy_act):
                return m
        return None

    def lookup_modern_to_legacy(self, modern_act_fragment: str, modern_section: str) -> Optional[ConcordanceMapping]:
        """Looks up a legacy predecessor given a modern section."""
        clean_sec = modern_section.strip().lower()
        
        for m in self.mappings:
            if m.verification_status != "VERIFIED_STATUTORY_CONCORDANCE":
                continue
            if clean_sec == m.modern_section.lower() and self._matches_act(modern_act_fragment, m.modern_act):
                return m
        return None

    def get_all_verified_mappings(self) -> List[Dict[str, Any]]:
        """Returns all verified concordance mappings for database insertion."""
        return [asdict(m) for m in self.mappings if m.verification_status == "VERIFIED_STATUTORY_CONCORDANCE"]
