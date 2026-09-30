"""Temporal legal validation for Indian law transitions, amendments, and struck-down provisions.

Enforces strict relationship-type concordance mapping between historical laws
(IPC 1860, CrPC 1973, IEA 1872) and current Sanhitas (BNS 2023, BNSS 2023, BSA 2023).
Guarantees that historical jurisprudence (e.g., Section 65B IEA) is not treated as
automatic direct equivalence to current statutory provisions (Section 63 BSA).
"""

from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime
from ..models import TemporalStatus
from ..cybercrime.registry import LegalRelationshipType


class IndianTemporalValidator:
    """Validates temporal applicability, struck-down provisions, and structured criminal concordance."""

    CRIMINAL_TRANSITION_DATE = "2024-07-01"

    # Known provisions struck down or invalidated by Indian Courts
    STRUCK_DOWN_PROVISIONS: Dict[str, Dict[str, Any]] = {
        "IT_ACT_66A": {
            "act_name": "Information Technology Act, 2000",
            "act_prefix": "IT_ACT",
            "section": "66A",
            "judgment": "Shreya Singhal v. Union of India",
            "citation": "(2015) 5 SCC 1",
            "decision_date": "2015-03-24",
            "reason": "Declared unconstitutional in its entirety as violating Article 19(1)(a) freedom of speech and expression.",
            "status": TemporalStatus.STRUCK_DOWN
        },
        "IPC_497": {
            "act_name": "Indian Penal Code, 1860",
            "act_prefix": "IPC",
            "section": "497",
            "judgment": "Joseph Shine v. Union of India",
            "citation": "(2019) 3 SCC 39",
            "decision_date": "2018-09-27",
            "reason": "Declared unconstitutional as violative of Articles 14, 15, and 21 (Adultery law).",
            "status": TemporalStatus.STRUCK_DOWN
        }
    }

    # Structured concordance mappings with explicit relationship types, effective dates, and authority sources
    STRUCTURED_CONCORDANCE_MAP: Dict[str, Dict[str, Any]] = {
        "IPC 378": {
            "historical_reference": "Section 378, Indian Penal Code, 1860",
            "current_reference": "Section 303(1), Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Theft (Definition)",
            "effective_date": "2024-07-01",
            "source": "Parliamentary Standing Committee on Home Affairs (Report 246)",
            "confidence": 1.0,
            "notes": "Section 303(1) BNS preserves the core definition of theft, explanations 1 to 5, and illustrations from Section 378 IPC."
        },
        "IPC 379": {
            "historical_reference": "Section 379, Indian Penal Code, 1860",
            "current_reference": "Section 303(2), Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.PARTIALLY_CORRESPONDING.value,
            "offence_title": "Punishment for theft",
            "effective_date": "2024-07-01",
            "source": "Parliamentary Standing Committee on Home Affairs (Report 246)",
            "confidence": 1.0,
            "notes": "BNS Section 303(2) consolidates theft punishment: ordinary term up to 3 years or fine; introduces community service for first-time theft below Rs 5,000 upon restoration/return of value; and introduces mandatory rigorous imprisonment of 1-5 years plus fine for second or subsequent convictions."
        },
        "IPC 300": {
            "historical_reference": "Section 300, Indian Penal Code, 1860",
            "current_reference": "Section 101, Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Murder (Definition and Exceptions)",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Direct correspondence with Section 101 BNS."
        },
        "CRPC 438": {
            "historical_reference": "Section 438, Code of Criminal Procedure, 1973",
            "current_reference": "Section 482, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Corresponds to Section 482 BNSS."
        },
        "CRPC 439": {
            "historical_reference": "Section 439, Code of Criminal Procedure, 1973",
            "current_reference": "Section 483, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Special powers of High Court or Court of Session regarding bail",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Corresponds to Section 483 BNSS."
        },
        "CRPC 437": {
            "historical_reference": "Section 437, Code of Criminal Procedure, 1973",
            "current_reference": "Section 480, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "When bail may be taken in case of non-bailable offence",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Corresponds to Section 480 BNSS."
        },
        "CRPC 482": {
            "historical_reference": "Section 482, Code of Criminal Procedure, 1973",
            "current_reference": "Section 528, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Saving of inherent powers of High Court",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Corresponds to Section 528 BNSS."
        },
        "CRPC 173": {
            "historical_reference": "Section 173, Code of Criminal Procedure, 1973",
            "current_reference": "Section 193, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Report of police officer on completion of investigation",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Corresponds to Section 193 BNSS."
        },
        "CRPC 167": {
            "historical_reference": "Section 167, Code of Criminal Procedure, 1973",
            "current_reference": "Section 187, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.PARTIALLY_CORRESPONDING.value,
            "offence_title": "Procedure when investigation cannot be completed in 24 hours (Custody/Remand)",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Section 187 BNSS permits police custody in parts during first 40 or 60 days."
        },
        "IPC 419": {
            "historical_reference": "Section 419, Indian Penal Code, 1860",
            "current_reference": "Section 319, Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Punishment for cheating by personation",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Governs offences committed prior to 1 July 2024; corresponds directly to Section 319 BNS."
        },
        "IPC 420": {
            "historical_reference": "Section 420, Indian Penal Code, 1860",
            "current_reference": "Section 318(4), Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.PARTIALLY_CORRESPONDING.value,
            "offence_title": "Cheating and dishonestly inducing delivery of property",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 0.95,
            "notes": "Section 318(4) BNS incorporates IPC 420 elements with restructured punishment provisions."
        },
        "IPC 468": {
            "historical_reference": "Section 468, Indian Penal Code, 1860",
            "current_reference": "Section 336(3), Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Forgery for purpose of cheating",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Applicable to forged physical documents or electronic records."
        },
        "IPC 471": {
            "historical_reference": "Section 471, Indian Penal Code, 1860",
            "current_reference": "Section 340(2), Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Using as genuine a forged document or electronic record",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Covers fraudulently using forged electronic record as genuine."
        },
        "IPC 302": {
            "historical_reference": "Section 302, Indian Penal Code, 1860",
            "current_reference": "Section 103(1), Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Punishment for murder",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Direct correspondence."
        },
        "IPC 307": {
            "historical_reference": "Section 307, Indian Penal Code, 1860",
            "current_reference": "Section 109, Bharatiya Nyaya Sanhita, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Attempt to murder",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 1.0,
            "notes": "Direct correspondence."
        },
        "CRPC 91": {
            "historical_reference": "Section 91, Code of Criminal Procedure, 1973",
            "current_reference": "Section 94, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.PARTIALLY_CORRESPONDING.value,
            "offence_title": "Summons to produce document or other thing",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 0.95,
            "notes": "Section 94 BNSS explicitly adds digital devices and electronic communication into the scope of summons."
        },
        "CRPC 100": {
            "historical_reference": "Section 100, Code of Criminal Procedure, 1973",
            "current_reference": "Section 103, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.PARTIALLY_CORRESPONDING.value,
            "offence_title": "Search procedures and witnesses",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 0.9,
            "notes": "Must be read alongside Section 105 BNSS which mandates audio-video electronic recording of search/seizure."
        },
        "CRPC 154": {
            "historical_reference": "Section 154, Code of Criminal Procedure, 1973",
            "current_reference": "Section 173, Bharatiya Nagarik Suraksha Sanhita, 2023",
            "relationship_type": LegalRelationshipType.PARTIALLY_CORRESPONDING.value,
            "offence_title": "Information in cognizable cases (FIR)",
            "effective_date": "2024-07-01",
            "source": "Ministry of Law & Justice Concordance Table",
            "confidence": 0.95,
            "notes": "Section 173 BNSS statutorily incorporates electronic information (e-FIR) to be signed within 3 days."
        },
        "IEA 65B": {
            "historical_reference": "Section 65B, Indian Evidence Act, 1872",
            "current_reference": "Section 63, Bharatiya Sakshya Adhiniyam, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Admissibility of electronic records and certificate requirement",
            "effective_date": "2024-07-01",
            "source": "Law Commission & Bharatiya Sakshya Legislative Framework",
            "confidence": 1.0,
            "notes": (
                "Section 63 BSA corresponds to Section 65B IEA. Landmark Supreme Court decisions interpreting Section 65B "
                "(Arjun Panditrao Khotkar, Anvar P.V.) interpret the repealed 1872 Act, which provides authoritative persuasive "
                "guidance on the mandatory nature of the Section 63(4) certificate under current law."
            )
        },
        "IEA 65A": {
            "historical_reference": "Section 65A, Indian Evidence Act, 1872",
            "current_reference": "Section 62, Bharatiya Sakshya Adhiniyam, 2023",
            "relationship_type": LegalRelationshipType.CORRESPONDING.value,
            "offence_title": "Special provisions as to evidence relating to electronic record",
            "effective_date": "2024-07-01",
            "source": "Bharatiya Sakshya Legislative Framework",
            "confidence": 1.0,
            "notes": "Provides that contents of electronic records must be proved under Section 63 BSA (formerly Section 65B IEA)."
        }
    }

    # Backward string mapping for legacy callers
    CRIMINAL_CONCORDANCE: Dict[str, str] = {
        k: f"{v['current_reference']} ({v['offence_title']}) [{v['relationship_type']}]"
        for k, v in STRUCTURED_CONCORDANCE_MAP.items()
    }

    def check_struck_down(self, act_or_prefix: str, provision_number: str) -> Tuple[bool, Optional[str]]:
        """Checks if a provision has been struck down by the Supreme Court."""
        clean_num = provision_number.upper().strip()

        for key, info in self.STRUCK_DOWN_PROVISIONS.items():
            if info["section"].upper() == clean_num:
                if (info["act_prefix"].lower() in act_or_prefix.lower() or
                    info["act_name"].lower() in act_or_prefix.lower() or
                    act_or_prefix.lower() in info["act_name"].lower() or
                    act_or_prefix.lower() in ("it", "it act", "it_act", "ipc")):
                    msg = (
                        f"CRITICAL LEGAL NOTICE: Section {info['section']} of the {info['act_name']} "
                        f"was struck down and declared unconstitutional by the Supreme Court of India in "
                        f"{info['judgment']} {info['citation']} on {info['decision_date']}. "
                        f"Reason: {info['reason']}. It is NOT currently enforceable law."
                    )
                    return True, msg
        return False, None

    def evaluate_criminal_temporal_regime(self, incident_date: Optional[str] = None) -> Dict[str, Any]:
        """Evaluates whether an offense is governed by IPC/CrPC/IEA (pre-1 July 2024) or BNS/BNSS/BSA (from 1 July 2024)."""
        if not incident_date:
            return {
                "applicable_substantive": "Bharatiya Nyaya Sanhita, 2023 (or Indian Penal Code, 1860 if alleged prior to 1 July 2024)",
                "applicable_procedural": "Bharatiya Nagarik Suraksha Sanhita, 2023 (or Code of Criminal Procedure, 1973 if investigation/trial instituted prior to 1 July 2024)",
                "applicable_evidence": "Bharatiya Sakshya Adhiniyam, 2023 (or Indian Evidence Act, 1872)",
                "transition_note": "Offenses committed before 1 July 2024 remain governed substantively by Indian Penal Code, 1860 (IPC); offenses from 1 July 2024 are governed by Bharatiya Nyaya Sanhita, 2023 (BNS)."
            }

        try:
            inc_dt = datetime.fromisoformat(incident_date[:10])
            cutoff = datetime.fromisoformat(self.CRIMINAL_TRANSITION_DATE)
            if inc_dt < cutoff:
                return {
                    "applicable_substantive": "Indian Penal Code, 1860 (IPC)",
                    "applicable_procedural": "Code of Criminal Procedure, 1973 (CrPC)",
                    "applicable_evidence": "Indian Evidence Act, 1872 (IEA)",
                    "transition_note": f"Offense date {incident_date[:10]} is prior to 1 July 2024. Governed by Indian Penal Code, 1860 (IPC), Code of Criminal Procedure, 1973 (CrPC), and Indian Evidence Act, 1872 (IEA) under Section 358 BNS / Section 531 BNSS savings clauses."
                }
            else:
                return {
                    "applicable_substantive": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
                    "applicable_procedural": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
                    "applicable_evidence": "Bharatiya Sakshya Adhiniyam, 2023 (BSA)",
                    "transition_note": f"Offense date {incident_date[:10]} is on or after 1 July 2024. Governed by Bharatiya Nyaya Sanhita, 2023 (BNS), Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS), and Bharatiya Sakshya Adhiniyam, 2023 (BSA)."
                }
        except Exception:
            return {
                "applicable_substantive": "BNS 2023 / IPC 1860 depending on date of occurrence",
                "transition_note": "Temporal regime governed by 1 July 2024 enforcement cutoff."
            }

    def get_concordance_info(self, legacy_key: str) -> Optional[str]:
        return self.CRIMINAL_CONCORDANCE.get(legacy_key.upper().strip())

    def get_structured_concordance(self, provision_key: str) -> Optional[Dict[str, Any]]:
        """Returns structured relationship metadata for concordance queries."""
        clean_key = provision_key.upper().strip().replace("SECTION ", "").replace("SEC ", "")
        for k, v in self.STRUCTURED_CONCORDANCE_MAP.items():
            if k == clean_key or clean_key in k:
                return v
        return None

