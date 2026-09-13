"""
grounded_prompt.py

Production grounded prompt construction for LegalAI V2 + Legal RAG.
Enforces explicit statutory evidence boundaries, domain isolation,
Article 20(1) non-retroactivity, and structured evidence sufficiency states.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


GROUNDED_SYSTEM_PROMPT = """You are LegalAI, an expert advocate and legal intelligence system specializing in Indian statutory law.
You provide precise, cautious, advocate-grade legal analysis strictly grounded in authoritative Indian statutes.

MANDATORY RULES OF LEGAL REASONING & EVIDENCE BOUNDARIES:
1. PRIMARY STATUTORY GROUNDING & BOUNDARIES:
   - The provided retrieved provisions are the ONLY authoritative statutory evidence for legal claims.
   - If a retrieved statutory chunk is merely semantically similar but does NOT address the user's specific legal question, you must NOT cite or rely on it.
   - NEVER use a Bharatiya Nyaya Sanhita (BNS), BNSS, or BSA section as a substitute for an unavailable or unrelated Act (e.g., do NOT cite BNS for cheque bounce, contracts, RTI, consumer disputes, property leases, or constitutional provisions).

2. ABSOLUTE PROHIBITION ON STATUTORY INVENTION:
   - NEVER invent, extrapolate, or guess a statutory section number, subsection, penalty, or case citation.
   - If a specific statutory section number or provision is not present in the retrieved sources, do NOT fabricate one.
   - If a requested provision belongs to an Act not present in the available corpus, clearly state:
     "Insufficient authoritative source coverage: the requested provision belongs to an Act outside the current LegalAI statutory database. I cannot verify this provision from the available authoritative sources."
   - Do NOT interpret absence from retrieval as proof that a law, section, fact, or document does not exist.

3. INSUFFICIENT EVIDENCE & ABSTENTION:
   - If the retrieved context is insufficient to answer or verify the legal point, explicitly state:
     "The available legal sources do not provide sufficient information to verify this point."
   - Do NOT silently fill missing statutory information from model memory if the authoritative text is not in the retrieved context.

4. STATUTORY DOMAIN SEPARATION:
   Always maintain the strict legal distinction between the three core enactments:
   - Bharatiya Nyaya Sanhita, 2023 (BNS): Substantive criminal law (offences, definitions, punishments, general exceptions).
   - Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS): Criminal procedure (FIR, arrest, remand, custody, investigation, bail, inquiry, trial).
   - Bharatiya Sakshya Adhiniyam, 2023 (BSA): Evidence law (admissibility, burden of proof, electronic records, competency, witness examination).

5. NUANCED TEMPORAL LAW & TRANSITIONAL ANALYSIS:
   Do NOT make crude assumptions such as "before July 1, 2024 is always IPC/CrPC" or "after July 1, 2024 is always BNS/BNSS/BSA".
   Instead, strictly evaluate:
   - Nature of the issue: Substantive criminal liability vs. Criminal procedure vs. Evidentiary rules.
   - Substantive Criminal Liability & Article 20(1): Under Article 20(1) of the Constitution of India (protection against ex post facto laws), an act can only be prosecuted and punished under the substantive penal law in force at the exact date the conduct occurred. Offences committed prior to July 1, 2024 are governed substantively by the Indian Penal Code, 1860; offences committed on or after July 1, 2024 are governed by the Bharatiya Nyaya Sanhita, 2023. BNS CANNOT be applied retroactively to an offence committed before July 1, 2024.
   - Procedural Matters: Procedural steps (FIR, investigation, trial) initiated after July 1, 2024 are generally governed by BNSS 2023, subject to Section 531 BNSS savings for pending trials.
   - Evidentiary Rules: Governed by BSA 2023 for proceedings conducted under it, subject to Section 170 BSA savings.

6. CITATION INTEGRITY:
   - Every cited section must actually support the claim made.
   - Always cite the exact statutory section and Act name when discussing a provision.
   - Never invent or fabricate URLs or citations."""


@dataclass
class GroundedPromptContext:
    system_prompt: str
    user_prompt: str
    retrieved_sections_text: str
    citations_text: str
    temporal_guidance: str
    evidence_status: str


def build_grounded_prompt(
    question: str,
    retrieved_chunks: List[Any],
    concordance_mappings: Optional[List[Any]] = None,
    effective_date: Optional[str] = None,
    temporal_guidance: Optional[str] = None,
    evidence_status: str = "ANSWERABLE",
    out_of_corpus_statute: Optional[str] = None
) -> GroundedPromptContext:
    """
    Constructs the grounded prompt containing retrieved statutory provisions,
    concordance bridges, and temporal boundaries.
    """
    # 1. Format Context Chunks
    context_blocks = []
    citations_list = []

    for idx, c in enumerate(retrieved_chunks, 1):
        act = getattr(c, "act", getattr(c, "act_name", "Unknown Act"))
        sec = getattr(c, "section", getattr(c, "section_number", "N/A"))
        title = getattr(c, "section_title", "Untitled Section")
        text = getattr(c, "text", getattr(c, "content", ""))
        source_url = getattr(c, "source_url", "")
        eff_from = getattr(c, "effective_date", getattr(c, "effective_from", "2024-07-01"))

        block = (
            f"[Source {idx}] {act}, Section {sec}: {title}\n"
            f"Effective From: {eff_from} | Authority: Government of India (India Code)\n"
            f"Official Statutory Text:\n{text.strip()}\n"
        )
        context_blocks.append(block)

        if source_url:
            citations_list.append(f"Section {sec} ('{title}'), {act} ({source_url})")
        else:
            citations_list.append(f"Section {sec} ('{title}'), {act}")

    # 2. Format Concordance Bridges
    concordance_text = ""
    if concordance_mappings:
        concordance_blocks = []
        for m in concordance_mappings:
            if hasattr(m, "legacy_act"):
                c_str = (
                    f"• {m.legacy_act} Section {m.legacy_section} ➔ {m.modern_act} Section {m.modern_section} "
                    f"({m.mapping_type}, Verified: {m.verification_status})"
                )
            else:
                c_str = (
                    f"• {m.get('legacy_act')} Section {m.get('legacy_section')} ➔ {m.get('modern_act')} Section {m.get('modern_section')} "
                    f"({m.get('mapping_type')}, Verified: {m.get('verification_status')})"
                )
            concordance_blocks.append(c_str)
        concordance_text = (
            "\n### Verified Statutory Concordance Reference (Parliamentary Comparative Tables):\n"
            + "\n".join(concordance_blocks)
            + "\n"
        )

    retrieved_sections_text = "\n".join(context_blocks) if context_blocks else "NO VERIFIED STATUTORY PROVISIONS RETRIEVED."
    citations_text = "\n".join(f"- {c}" for c in citations_list) if citations_list else "None."

    # 3. Format Temporal Directives
    temp_block = ""
    if temporal_guidance:
        temp_block = f"\n### Mandatory Temporal & Transitional Rule:\n{temporal_guidance}\n"
    elif effective_date:
        temp_block = f"\nRelevant Date of Incident / Inquiry: {effective_date}\n"

    # 4. Out-of-corpus directive
    corpus_directive = ""
    if evidence_status == "OUT_OF_CORPUS" and out_of_corpus_statute:
        corpus_directive = (
            f"\n### Corpus Boundary Notice:\n"
            f"The legal matter in this query primarily falls under '{out_of_corpus_statute}', "
            f"which is NOT present in the current 3-Act (BNS, BNSS, BSA) database. "
            f"Do NOT substitute unrelated criminal provisions. State that the required statute is not in the database.\n"
        )

    user_prompt = (
        f"### Legal Query:\n{question}\n"
        f"{temp_block}"
        f"{corpus_directive}"
        f"{concordance_text}\n"
        f"### Retrieved Authoritative Statutory Provisions:\n"
        f"{retrieved_sections_text}\n\n"
        f"### Retrieved Statutory Citations:\n"
        f"{citations_text}\n\n"
        f"Provide a clear, advocate-grade legal answer strictly adhering to the mandatory rules of legal reasoning."
    )

    return GroundedPromptContext(
        system_prompt=GROUNDED_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        retrieved_sections_text=retrieved_sections_text,
        citations_text=citations_text,
        temporal_guidance=temporal_guidance or "",
        evidence_status=evidence_status
    )
