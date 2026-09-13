"""
temporal_guard.py

Temporal legal guard enforcing Article 20(1) non-retroactivity and transitional frameworks.
Ensures that substantive criminal law is strictly evaluated against the date of conduct,
and prevents retroactive application of the Bharatiya Nyaya Sanhita, 2023 to pre-July 1, 2024 offences.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Tuple, Dict, Any


COMMENCEMENT_DATE_BNS = date(2024, 7, 1)


@dataclass
class TemporalAnalysisResult:
    has_date_context: bool
    extracted_date: Optional[str]
    is_pre_commencement: bool
    is_substantive_liability: bool
    is_procedural_matter: bool
    is_evidence_matter: bool
    applicable_substantive_law: str
    applicable_procedural_law: str
    temporal_guidance: str
    is_valid_transition: bool


class TemporalLawGuard:
    """Evaluates temporal compatibility of legal queries and provisions."""

    # Date extraction regexes
    DATE_PATTERNS = [
        # e.g. "15 June 2024", "15th June 2024", "1 July 2024", "2 July 2024"
        r'\b([0-3]?[0-9])(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20[1-3][0-9])\b',
        # e.g. "June 15, 2024", "July 1, 2024"
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+([0-3]?[0-9])(?:st|nd|rd|th)?,?\s+(20[1-3][0-9])\b',
        # e.g. "2024-06-15"
        r'\b(20[1-3][0-9])-([0-1][0-9])-([0-3][0-9])\b',
        # e.g. "May 2024", "June 2024", "July 2024"
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20[1-3][0-9])\b',
    ]

    MONTH_MAP = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }

    def parse_incident_date(self, text: str) -> Optional[date]:
        """Extracts the earliest date mentioned in the query."""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if len(groups) == 3:
                        if groups[0].isdigit() and not groups[1].isdigit():
                            # Day Month Year
                            d = int(groups[0])
                            m = self.MONTH_MAP[groups[1].lower()]
                            y = int(groups[2])
                            return date(y, m, d)
                        elif not groups[0].isdigit() and groups[1].isdigit():
                            # Month Day Year
                            m = self.MONTH_MAP[groups[0].lower()]
                            d = int(groups[1])
                            y = int(groups[2])
                            return date(y, m, d)
                        elif groups[0].isdigit() and groups[1].isdigit() and groups[2].isdigit():
                            # YYYY-MM-DD
                            return date(int(groups[0]), int(groups[1]), int(groups[2]))
                    elif len(groups) == 2:
                        # Month Year (assume 1st of month)
                        m = self.MONTH_MAP[groups[0].lower()]
                        y = int(groups[1])
                        return date(y, m, 1)
                except (ValueError, KeyError):
                    continue
        return None

    def analyze(self, query: str, effective_date_param: Optional[str] = None) -> TemporalAnalysisResult:
        """
        Analyzes the query for temporal triggers, conduct dates, and applies Article 20(1) logic.
        """
        q_low = query.lower()
        extracted_d = self.parse_incident_date(query)
        if not extracted_d and effective_date_param:
            try:
                extracted_d = datetime.strptime(effective_date_param, "%Y-%m-%d").date()
            except ValueError:
                pass

        has_date = extracted_d is not None
        is_pre_commencement = (extracted_d < COMMENCEMENT_DATE_BNS) if extracted_d else False

        # Classify legal aspects
        substantive_triggers = ["offence", "offense", "theft", "murder", "penalty", "punishment", "guilty", "liable", "substantive"]
        procedural_triggers = ["fir", "arrest", "remand", "bail", "investigation", "trial", "procedure", "charge sheet"]
        evidence_triggers = ["evidence", "electronic record", "certificate", "admissibility", "witness", "confession"]

        is_substantive = any(t in q_low for t in substantive_triggers)
        is_procedural = any(t in q_low for t in procedural_triggers)
        is_evidence = any(t in q_low for t in evidence_triggers)

        # Default fallback
        if not is_substantive and not is_procedural and not is_evidence:
            is_substantive = True

        # Determine applicable laws
        if is_pre_commencement:
            applicable_sub = "Indian Penal Code, 1860 (IPC) [Article 20(1) Non-Retroactivity]"
            applicable_proc = "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) [for steps taken post-1 July 2024, subject to Section 531 BNSS savings]"
            guidance = (
                f"CONDUCT DATE IS PRIOR TO 1 JULY 2024 ({extracted_d.strftime('%d %B %Y') if extracted_d else 'Pre-July 2024'}).\n"
                f"- Substantive Criminal Liability: Strictly governed by the Indian Penal Code, 1860 under Article 20(1) of the Constitution.\n"
                f"  The Bharatiya Nyaya Sanhita, 2023 CANNOT be applied retrospectively to penalize acts committed prior to July 1, 2024.\n"
                f"- Criminal Procedure: Procedural actions (FIR, investigation, trial) initiated after July 1, 2024 are generally governed by BNSS 2023, subject to Section 531 savings."
            )
            is_valid = True
        elif extracted_d and extracted_d >= COMMENCEMENT_DATE_BNS:
            applicable_sub = "Bharatiya Nyaya Sanhita, 2023 (BNS)"
            applicable_proc = "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)"
            guidance = (
                f"CONDUCT DATE IS ON OR AFTER 1 JULY 2024 ({extracted_d.strftime('%d %B %Y')}).\n"
                f"- Substantive Criminal Liability: Governed by the Bharatiya Nyaya Sanhita, 2023 (BNS).\n"
                f"- Criminal Procedure: Governed by the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS).\n"
                f"- Evidence: Governed by the Bharatiya Sakshya Adhiniyam, 2023 (BSA)."
            )
            is_valid = True
        else:
            applicable_sub = "Bharatiya Nyaya Sanhita, 2023 (BNS) for current acts"
            applicable_proc = "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) for current procedure"
            guidance = (
                "NO SPECIFIC INCIDENT DATE DETECTED.\n"
                "If advising on current law (post-1 July 2024), apply BNS, BNSS, and BSA.\n"
                "If advising on conduct prior to 1 July 2024, substantive liability remains with IPC under Article 20(1)."
            )
            is_valid = True

        return TemporalAnalysisResult(
            has_date_context=has_date,
            extracted_date=extracted_d.isoformat() if extracted_d else None,
            is_pre_commencement=is_pre_commencement,
            is_substantive_liability=is_substantive,
            is_procedural_matter=is_procedural,
            is_evidence_matter=is_evidence,
            applicable_substantive_law=applicable_sub,
            applicable_procedural_law=applicable_proc,
            temporal_guidance=guidance,
            is_valid_transition=is_valid
        )
