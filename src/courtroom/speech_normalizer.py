"""
src/courtroom/speech_normalizer.py

Phonetic and contextual auto-corrector for Indian courtroom speech-to-text.
Corrects common Whisper / Web Speech API misrecognitions of legal terms,
statutes, case parties, and judicial entities.
"""

import re
from typing import Dict, List, Tuple

# Domain replacements (regex pattern -> clean legal term)
DOMAIN_REPLACEMENTS: List[Tuple[re.Pattern, str]] = [
    # Case Parties & Names
    (re.compile(r'\b(madness|martin is|martinez\'s|martynis|martine)\b', re.IGNORECASE), "Martinez"),
    (re.compile(r'\b(coastal holding|costal holdings|coastal holding ltd)\b', re.IGNORECASE), "Coastal Holdings Ltd."),
    (re.compile(r'\b(whit field|white field|witfield)\b', re.IGNORECASE), "Whitfield"),
    (re.compile(r'\b(apex logistic|apex logistics corp)\b', re.IGNORECASE), "Apex Logistics Corp."),
    (re.compile(r'\b(horizon freight|horizon freight services)\b', re.IGNORECASE), "Horizon Freight Services"),
    (re.compile(r'\b(harish salvi|harish salve\'s|advocate salve)\b', re.IGNORECASE), "Sr. Adv. Harish Salve"),
    (re.compile(r'\b(rekha bali|justice bali|justice rekha)\b', re.IGNORECASE), "Justice Rekha Palli"),
    (re.compile(r'\b(vikram rathod|inspector rathod)\b', re.IGNORECASE), "Inspector Vikram Rathore"),

    # Statutes & Legal Codes (New 2023-2024 Indian Codes)
    (re.compile(r'\b(b\s*n\s*s\s*s|beanies|b\s*n\s*s\s*s\s*act|b n s s)\b', re.IGNORECASE), "BNSS"),
    (re.compile(r'\b(b\s*n\s*s|bns act|b n s)\b', re.IGNORECASE), "BNS"),
    (re.compile(r'\b(b\s*s\s*a|bsa act|b s a)\b', re.IGNORECASE), "BSA"),
    (re.compile(r'\b(c\s*r\s*p\s*c|cr pc|crpc act)\b', re.IGNORECASE), "CrPC"),
    (re.compile(r'\b(c\s*p\s*c|c pc|sea pc)\b', re.IGNORECASE), "CPC"),
    (re.compile(r'\b(n\s*d\s*p\s*s|ndps act)\b', re.IGNORECASE), "NDPS Act"),

    # Common Court Document Terms
    (re.compile(r'\b(station dairy|general dairy|station daily)\b', re.IGNORECASE), "Station Diary"),
    (re.compile(r'\b(caesar memo|seizer memo|cease memo|sizer memo)\b', re.IGNORECASE), "Seizure Memo"),
    (re.compile(r'\b(punch witness|panch witness|punch nama|panchanama)\b', re.IGNORECASE), "Panch Witness"),
    (re.compile(r'\b(cfsl report|c f s l report)\b', re.IGNORECASE), "CFSL Report"),
    (re.compile(r'\b(exhibit p\s*four|exhibit p\s*4|ex\s*p\s*4)\b', re.IGNORECASE), "Exhibit P-4"),
    (re.compile(r'\b(exhibit p\s*one|exhibit p\s*1|ex\s*p\s*1)\b', re.IGNORECASE), "Exhibit P-1"),
    (re.compile(r'\b(exhibit p\s*two|exhibit p\s*2|ex\s*p\s*2)\b', re.IGNORECASE), "Exhibit P-2"),
    (re.compile(r'\b(exhibit d\s*one|exhibit d\s*1|ex\s*d\s*1)\b', re.IGNORECASE), "Exhibit D-1"),
    (re.compile(r'\b(exhibit d\s*two|exhibit d\s*2|ex\s*d\s*2)\b', re.IGNORECASE), "Exhibit D-2"),

    # Statutory Sections & Rules
    (re.compile(r'\b(section four eighty|section 480|sec 480)\b', re.IGNORECASE), "Section 480"),
    (re.compile(r'\b(order thirty nine|order 39|o 39)\b', re.IGNORECASE), "Order 39"),
    (re.compile(r'\b(rule one and two|rules 1 and 2|rule 1 and 2)\b', re.IGNORECASE), "Rules 1 & 2"),
    (re.compile(r'\b(section nine|section 9|sec 9)\b', re.IGNORECASE), "Section 9"),
    (re.compile(r'\b(section fifty|section 50|sec 50)\b', re.IGNORECASE), "Section 50"),
    (re.compile(r'\b(section one sixty one|section 161|161 statement)\b', re.IGNORECASE), "Section 161 statement"),
    (re.compile(r'\b(section one sixty four|section 164|164 statement)\b', re.IGNORECASE), "Section 164 statement"),

    # Courtroom Etiquette & Procedural Phrases
    (re.compile(r'\b(my lourd|my lord|m\'lud|milord|your honor|your honour)\b', re.IGNORECASE), "My Lord"),
    (re.compile(r'\b(interlocutory injunction|interim injunction|stay order)\b', re.IGNORECASE), "Interlocutory Injunction"),
    (re.compile(r'\b(pass over|passover memo)\b', re.IGNORECASE), "passover"),
    (re.compile(r'\b(adjournment|adjourn the matter)\b', re.IGNORECASE), "adjournment"),
]


def normalize_courtroom_speech(text: str) -> str:
    """Applies contextual legal substitutions to speech-to-text transcripts."""
    if not text:
        return ""
    normalized = text
    for pattern, replacement in DOMAIN_REPLACEMENTS:
        normalized = pattern.sub(replacement, normalized)
    return normalized
