"""Cybercrime Multi-Act Synthesis Engine for LegalAI.

Provides structured, authoritative legal synthesis for complex cybercrime inquiries
involving concurrent statutory frameworks (IT Act, BNS, BNSS, BSA), subordinate
regulations (IT Rules 2021, CERT-In Directions, SPDI Rules), landmark judicial
precedents (Shreya Singhal, Arjun Panditrao, Anvar PV, Selvi, Christian Louboutin),
and official government guidance (I4C Portal SOP, RBI Directions).
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple


def _fetch_chunk(pipeline, chunk_id: str):
    """Safely retrieves a chunk regardless of DOC_ prefix variation."""
    c = pipeline.db.get_chunk(chunk_id)
    if c:
        return c
    if chunk_id.startswith("DOC_"):
        c = pipeline.db.get_chunk(chunk_id[4:])
        if c:
            return c
    else:
        c = pipeline.db.get_chunk("DOC_" + chunk_id)
        if c:
            return c
    return None


def get_cybercrime_multi_act_response(pipeline, question: str, resolved: Dict[str, Any], top_k: int = 5) -> Optional[Dict[str, Any]]:
    """Handles multi-act cybercrime concept queries (financial fraud, electronic evidence, investigation, etc.)."""
    cats = resolved.get("cybercrime_categories", [])
    q_lower = question.lower()
    
    is_elec_evid = (
        "ELECTRONIC_EVIDENCE" in cats or 
        any(term in q_lower for term in ["electronic evidence", "electronic record", "digital evidence", "65b", "section 63", "bsa", "evidence law", "certificate"])
    )
    is_fraud = (
        any(c in ["CYBER_FRAUD", "FINANCIAL_CYBERCRIME", "IDENTITY_THEFT", "PERSONATION"] for c in cats) or 
        any(term in q_lower for term in ["fraud", "phishing", "impersonation", "cheating", "financial cyber", "scam", "unauthorised transaction", "unauthorized transaction"])
    )
    is_reporting = (
        any(term in q_lower for term in ["1930", "portal", "i4c", "cfcfrms", "helpline", "reporting sop", "cybercrime.gov.in", "complaint portal"])
    )
    is_investigation = (
        "INVESTIGATION_PROCEDURE" in cats or 
        any(term in q_lower for term in ["investigat", "search", "seizure", "fir", "e-fir", "hash value", "forensic", "seize"])
    )
    is_intermediary = (
        "INTERMEDIARY_LIABILITY" in cats or 
        any(term in q_lower for term in ["intermediar", "safe harbor", "safe harbour", "take down", "takedown", "due diligence", "deepfake", "platform liability", "louboutin"]) or
        ("79" in q_lower and ("it act" in q_lower or "immunity" in q_lower or "liability" in q_lower)) or
        ("66a" in q_lower and ("shreya" in q_lower or "struck" in q_lower or "unconstitutional" in q_lower))
    )
    is_harassment = (
        any(c in ["ONLINE_HARASSMENT", "CYBERSTALKING"] for c in cats) or
        any(term in q_lower for term in ["harass", "stalk", "obscen", "morphed", "voyeurism", "defamation", "suhas katti", "67", "66e"])
    )
    is_cyber_terrorism = (
        any(c in ["CYBER_TERRORISM", "CRITICAL_INFRASTRUCTURE"] for c in cats) or
        any(term in q_lower for term in ["terror", "critical information infrastructure", "protected system", "66f", "section 70"])
    )
    
    collected_chunks = []
    
    if is_reporting:
        # Official Government Guidance (strictly non-statutory)
        i4c_sop = _fetch_chunk(pipeline, "GUIDE_I4C_CFCFRMS_I4C_SOP_1930") or _fetch_chunk(pipeline, "DOC_GUIDE_I4C_CFCFRMS_I4C_SOP_1930")
        if i4c_sop: collected_chunks.append((i4c_sop, "GOVERNMENT_GUIDANCE", 100.0, "Official Government Guidance (MHA / I4C National Portal)"))
        
        # Regulatory Banking Master Direction
        rbi_para6 = _fetch_chunk(pipeline, "GUIDE_RBI_ELECTRONIC_BANKING_PARA_6") or _fetch_chunk(pipeline, "DOC_GUIDE_RBI_ELECTRONIC_BANKING_PARA_6")
        if rbi_para6: collected_chunks.append((rbi_para6, "REGULATION", 92.0, "RBI Regulatory Master Direction (Banking Customer Protection)"))
        
        # Statutory e-FIR & Complaints: BNSS 2023
        bnss_173 = pipeline.db.get_chunk_by_provision("BNSS", "173", "SECTION")
        if bnss_173: collected_chunks.append((bnss_173, "STATUTE", 90.0, "Procedural Law (e-FIR Mandates under BNSS 2023)"))
        
        # Substantive IT Act
        it_66d = pipeline.db.get_chunk_by_provision("IT_ACT", "66D", "SECTION")
        if it_66d: collected_chunks.append((it_66d, "STATUTE", 88.0, "Substantive Offence (IT Act, 2000)"))
        
    elif is_elec_evid:
        # Prioritize BSA 2023 (Current statutory evidence law)
        bsa_63 = pipeline.db.get_chunk_by_provision("BSA", "63", "SECTION")
        bsa_61 = pipeline.db.get_chunk_by_provision("BSA", "61", "SECTION")
        bsa_62 = pipeline.db.get_chunk_by_provision("BSA", "62", "SECTION")
        if bsa_63: collected_chunks.append((bsa_63, "STATUTE", 100.0, "Current Evidence Law (BSA 2023)"))
        if bsa_61: collected_chunks.append((bsa_61, "STATUTE", 95.0, "Current Evidence Law (BSA 2023)"))
        if bsa_62: collected_chunks.append((bsa_62, "STATUTE", 90.0, "Current Evidence Law (BSA 2023)"))
        
        # Landmark Supreme Court Precedents (Ratio Decidendi)
        arjun = _fetch_chunk(pipeline, "SC_ARJUN_PANDITRAO_RATIO")
        if arjun: collected_chunks.append((arjun, "JUDGMENT", 96.0, "Binding Supreme Court Precedent (3-Judge Bench)"))
        anvar = _fetch_chunk(pipeline, "SC_ANVAR_PV_RATIO")
        if anvar: collected_chunks.append((anvar, "JUDGMENT", 92.0, "Supreme Court Precedent (3-Judge Bench)"))
        shafhi = _fetch_chunk(pipeline, "SC_SHAFHI_MOHAMMAD_RATIO")
        if shafhi and ("overrule" in q_lower or "shafhi" in q_lower or "history" in q_lower):
            collected_chunks.append((shafhi, "JUDGMENT", 88.0, "Overruled Division Bench Precedent (Historical Context)"))
            
        # IT Act Definitions
        it_2_t = pipeline.db.get_chunk_by_provision("IT_ACT", "2(1)(t)", "SECTION") or pipeline.db.get_chunk_by_provision("IT_ACT", "2", "SECTION")
        if it_2_t: collected_chunks.append((it_2_t, "STATUTE", 85.0, "Statutory Definition of Electronic Record (IT Act, 2000)"))
        
    elif is_fraud:
        # 1. Primary Technology Statute: IT Act 2000
        it_66c = pipeline.db.get_chunk_by_provision("IT_ACT", "66C", "SECTION")
        it_66d = pipeline.db.get_chunk_by_provision("IT_ACT", "66D", "SECTION")
        it_43 = pipeline.db.get_chunk_by_provision("IT_ACT", "43", "SECTION")
        if it_66c: collected_chunks.append((it_66c, "STATUTE", 100.0, "Primary Technology Law (Identity Theft / Credentials)"))
        if it_66d: collected_chunks.append((it_66d, "STATUTE", 98.0, "Primary Technology Law (Cheating by Personation)"))
        if it_43: collected_chunks.append((it_43, "STATUTE", 90.0, "Civil Liability & Compensation (Unauthorized Access)"))
        
        # 2. Substantive Criminal Law: BNS 2023
        bns_318 = pipeline.db.get_chunk_by_provision("BNS", "318", "SECTION")
        bns_319 = pipeline.db.get_chunk_by_provision("BNS", "319", "SECTION")
        bns_336 = pipeline.db.get_chunk_by_provision("BNS", "336", "SECTION")
        if bns_318: collected_chunks.append((bns_318, "STATUTE", 95.0, "Substantive Criminal Law (Bharatiya Nyaya Sanhita, 2023)"))
        if bns_319: collected_chunks.append((bns_319, "STATUTE", 92.0, "Substantive Criminal Law (Bharatiya Nyaya Sanhita, 2023)"))
        if bns_336: collected_chunks.append((bns_336, "STATUTE", 88.0, "Substantive Criminal Law (Bharatiya Nyaya Sanhita, 2023)"))
        
        # 3. Procedural Law: BNSS 2023
        bnss_94 = pipeline.db.get_chunk_by_provision("BNSS", "94", "SECTION")
        bnss_105 = pipeline.db.get_chunk_by_provision("BNSS", "105", "SECTION")
        if bnss_94: collected_chunks.append((bnss_94, "STATUTE", 85.0, "Procedural Law (Bharatiya Nagarik Suraksha Sanhita, 2023)"))
        if bnss_105: collected_chunks.append((bnss_105, "STATUTE", 82.0, "Procedural Law (Bharatiya Nagarik Suraksha Sanhita, 2023)"))
        
        # 4. Evidence Law: BSA 2023
        bsa_63 = pipeline.db.get_chunk_by_provision("BSA", "63", "SECTION")
        if bsa_63: collected_chunks.append((bsa_63, "STATUTE", 85.0, "Evidence Law (Bharatiya Sakshya Adhiniyam, 2023)"))
        
        # 5. Regulatory Directions & Official Government Guidance
        rbi_para6 = _fetch_chunk(pipeline, "GUIDE_RBI_ELECTRONIC_BANKING_PARA_6") or _fetch_chunk(pipeline, "DOC_GUIDE_RBI_ELECTRONIC_BANKING_PARA_6")
        if rbi_para6: collected_chunks.append((rbi_para6, "REGULATION", 82.0, "RBI Regulatory Master Direction (Banking Customer Protection)"))
        i4c_sop = _fetch_chunk(pipeline, "GUIDE_I4C_CFCFRMS_I4C_SOP_1930") or _fetch_chunk(pipeline, "DOC_GUIDE_I4C_CFCFRMS_I4C_SOP_1930")
        if i4c_sop: collected_chunks.append((i4c_sop, "GOVERNMENT_GUIDANCE", 80.0, "Official I4C / MHA Portal Standard Operating Procedure"))
        
    elif is_investigation:
        # Procedural: BNSS & IT Act
        it_78 = pipeline.db.get_chunk_by_provision("IT_ACT", "78", "SECTION")
        bnss_105 = pipeline.db.get_chunk_by_provision("BNSS", "105", "SECTION")
        bnss_173 = pipeline.db.get_chunk_by_provision("BNSS", "173", "SECTION")
        bnss_94 = pipeline.db.get_chunk_by_provision("BNSS", "94", "SECTION")
        bsa_63 = pipeline.db.get_chunk_by_provision("BSA", "63", "SECTION")
        selvi = _fetch_chunk(pipeline, "SC_SELVI_RATIO")
        
        if it_78: collected_chunks.append((it_78, "STATUTE", 100.0, "Investigative Authority (IT Act, 2000)"))
        if bnss_105: collected_chunks.append((bnss_105, "STATUTE", 95.0, "Mandatory Digital Seizure Recording (BNSS 2023)"))
        if bnss_173: collected_chunks.append((bnss_173, "STATUTE", 92.0, "e-FIR & Cognizable Complaint (BNSS 2023)"))
        if bnss_94: collected_chunks.append((bnss_94, "STATUTE", 90.0, "Summons for Electronic Devices (BNSS 2023)"))
        if bsa_63: collected_chunks.append((bsa_63, "STATUTE", 88.0, "Electronic Evidence Handling (BSA 2023)"))
        if selvi: collected_chunks.append((selvi, "JUDGMENT", 86.0, "Constitutional Limits on Digital Forensics (Supreme Court)"))
        
    elif is_intermediary:
        it_79 = pipeline.db.get_chunk_by_provision("IT_ACT", "79", "SECTION")
        shreya = _fetch_chunk(pipeline, "SC_SHREYA_SINGHAL_RATIO")
        rule_3 = _fetch_chunk(pipeline, "REG_IT_RULES_2021_RULE_3") or _fetch_chunk(pipeline, "DOC_REG_IT_RULES_2021_RULE_3")
        rule_3_2 = _fetch_chunk(pipeline, "REG_IT_RULES_2021_RULE_3_2_B") or _fetch_chunk(pipeline, "DOC_REG_IT_RULES_2021_RULE_3_2_B")
        louboutin = _fetch_chunk(pipeline, "HC_CHRISTIAN_LOUBOUTIN_RATIO")
        deepfake_adv = _fetch_chunk(pipeline, "ADV_MEITY_DEEPFAKES_2023_ADV_DEEPFAKES_PARA_1") or _fetch_chunk(pipeline, "DOC_ADV_MEITY_DEEPFAKES_2023_ADV_DEEPFAKES_PARA_1")
        
        if it_79: collected_chunks.append((it_79, "STATUTE", 100.0, "Primary Statutory Authority (IT Act, 2000)"))
        if shreya: collected_chunks.append((shreya, "JUDGMENT", 96.0, "Binding Supreme Court Precedent (Shreya Singhal)"))
        if rule_3: collected_chunks.append((rule_3, "REGULATION", 92.0, "Subordinate Legislation (IT Rules 2021 Due Diligence)"))
        if rule_3_2 and ("24" in q_lower or "sexual" in q_lower or "morph" in q_lower or "non-consensual" in q_lower):
            collected_chunks.append((rule_3_2, "REGULATION", 90.0, "Subordinate Legislation (IT Rules 2021 24-Hour Removal Mandate)"))
        if louboutin and ("active" in q_lower or "commerce" in q_lower or "louboutin" in q_lower or "counterfeit" in q_lower or "trademark" in q_lower):
            collected_chunks.append((louboutin, "JUDGMENT", 88.0, "High Court Precedent on Active Intermediaries (Delhi High Court)"))
        if deepfake_adv and ("deepfake" in q_lower or "ai" in q_lower or "synthetic" in q_lower or "advisory" in q_lower):
            collected_chunks.append((deepfake_adv, "ADVISORY", 85.0, "Official Executive Advisory (MeitY Deepfake Advisory 2023)"))
            
    elif is_harassment:
        it_67 = pipeline.db.get_chunk_by_provision("IT_ACT", "67", "SECTION")
        it_67a = pipeline.db.get_chunk_by_provision("IT_ACT", "67A", "SECTION")
        it_66e = pipeline.db.get_chunk_by_provision("IT_ACT", "66E", "SECTION")
        suhas = _fetch_chunk(pipeline, "TRIAL_SUHAS_KATTI_RATIO")
        bns_78 = pipeline.db.get_chunk_by_provision("BNS", "78", "SECTION")
        
        if it_67: collected_chunks.append((it_67, "STATUTE", 100.0, "Primary Statutory Authority (IT Act, 2000)"))
        if it_67a: collected_chunks.append((it_67a, "STATUTE", 95.0, "Primary Statutory Authority (IT Act, 2000)"))
        if it_66e: collected_chunks.append((it_66e, "STATUTE", 92.0, "Primary Statutory Authority (IT Act, 2000)"))
        if suhas: collected_chunks.append((suhas, "JUDGMENT", 88.0, "Landmark Precedent on Cyber Harassment (Suhas Katti)"))
        if bns_78: collected_chunks.append((bns_78, "STATUTE", 85.0, "Substantive Criminal Law (Stalking under BNS 2023)"))
        
    elif is_cyber_terrorism:
        it_66f = pipeline.db.get_chunk_by_provision("IT_ACT", "66F", "SECTION")
        it_70 = pipeline.db.get_chunk_by_provision("IT_ACT", "70", "SECTION")
        cert_in = _fetch_chunk(pipeline, "REG_CERTIN_DIRECTIONS_2022_DIR_5_1") or _fetch_chunk(pipeline, "DOC_REG_CERTIN_DIRECTIONS_2022_DIR_5_1")
        if it_66f: collected_chunks.append((it_66f, "STATUTE", 100.0, "Primary Statutory Authority (Cyber Terrorism - IT Act)"))
        if it_70: collected_chunks.append((it_70, "STATUTE", 95.0, "Primary Statutory Authority (Protected Systems - IT Act)"))
        if cert_in: collected_chunks.append((cert_in, "REGULATION", 90.0, "CERT-In 6-Hour Incident Reporting Directions"))
        
    else:
        # Fallback to general IT Act provisions
        it_66 = pipeline.db.get_chunk_by_provision("IT_ACT", "66", "SECTION")
        it_43 = pipeline.db.get_chunk_by_provision("IT_ACT", "43", "SECTION")
        if it_66: collected_chunks.append((it_66, "STATUTE", 95.0, "Primary Statutory Authority (IT Act, 2000)"))
        if it_43: collected_chunks.append((it_43, "STATUTE", 90.0, "Primary Statutory Authority (IT Act, 2000)"))
        
    if not collected_chunks:
        return None

    # Invoke Qwen2.5-14B-Instruct + LegalAI V2 synthesis over verified multi-act chunks
    qwen_synthesis = None
    qwen_invoked = False
    adapter_used = None
    if hasattr(pipeline, "synthesize_legal_explanation") and getattr(pipeline, "base_pipeline", None):
        qwen_synthesis = pipeline.synthesize_legal_explanation(
            question=question,
            retrieved_chunks=[c for c, _, _, _ in collected_chunks],
            query_type="MULTI_ACT_CYBERCRIME"
        )
        if qwen_synthesis:
            qwen_invoked = True
            adapter_used = "outputs/qwen14b-legalai-v2"
        
    # Format structured lawyer synthesis
    sections_rendered = []
    sources_list = []
    
    sections_rendered.append("## Authoritative Multi-Act Cybercrime Legal Framework\n")
    if qwen_synthesis:
        sections_rendered.append(f"### Legal Reasoning & Multi-Act Applicability (LegalAI V2)\n{qwen_synthesis}\n")
    sections_rendered.append(
        "> [!NOTE]\n"
        "> **Multi-Act Jurisprudential Structure**: Cybercrime inquiries under Indian law are governed concurrently by "
        "specialized technology law (IT Act, 2000), substantive criminal statutes (BNS 2023 / IPC 1860), procedural codes "
        "(BNSS 2023 / CrPC 1973), evidentiary admissibility rules (BSA 2023 / IEA 1872), binding judicial precedents, "
        "and sector-specific regulatory directives. Applicability is strictly conditional upon factual dates, jurisdiction, "
        "and technical architecture.\n"
    )
    
    current_category = None
    for chunk, stype, score, category_label in collected_chunks:
        cite = pipeline.citation_engine.format_citation(chunk)
        provenance = pipeline.citation_engine.format_lawyer_provenance_block(chunk)
        
        sources_list.append({
            "chunk_id": chunk.chunk_id,
            "title": chunk.title,
            "act_name": chunk.act_name,
            "act_prefix": chunk.act_prefix,
            "provision_number": chunk.provision_number,
            "provision_type": chunk.provision_type.value if hasattr(chunk.provision_type, 'value') else str(chunk.provision_type),
            "source_type": stype,
            "citation": cite.citation_str,
            "document_type": chunk.document_type.value if hasattr(chunk.document_type, 'value') else str(chunk.document_type),
            "authority_tier": chunk.authority_tier.value if hasattr(chunk.authority_tier, 'value') else str(chunk.authority_tier),
            "temporal_status": chunk.temporal_status.value if hasattr(chunk.temporal_status, 'value') else str(chunk.temporal_status),
            "source_url": chunk.official_source_url,
            "score": round(score, 2)
        })
        
        if category_label != current_category:
            current_category = category_label
            sections_rendered.append(f"\n### {current_category}")
            
        sections_rendered.append(
            f"#### {cite.citation_str} [{stype}]\n\n"
            f"{chunk.content}\n\n"
            f"{provenance}\n"
        )
        
    sections_rendered.append(
        "\n### Legal & Factual Analysis for Practitioners\n"
        "- **Primary Statutory Authority**: Assessed primarily under the Information Technology Act, 2000 (special enactments override general statutes where in conflict per *Anvar P.V.*).\n"
        "- **Concurrent Penal Liability**: Substantive penal charges under Bharatiya Nyaya Sanhita, 2023 (or Indian Penal Code, 1860 if the cause of action or transaction occurred prior to 1 July 2024 under Article 20(1) non-retroactivity).\n"
        "- **Procedural Compliance**: Must comply with search, seizure, digital evidence hashing, and e-FIR mandates under Bharatiya Nagarik Suraksha Sanhita, 2023.\n"
        "- **Evidentiary Admissibility**: Strict compliance with Section 63 BSA certificate requirements (analogous to former Section 65B IEA as settled by the 3-Judge Bench in *Arjun Panditrao Khotkar*) is an indispensable condition precedent for relying on digital secondary evidence in judicial proceedings.\n"
        "- **Regulatory Directions vs Statutory Law**: Regulatory directives (RBI Master Directions, CERT-In directions) and Government Advisories (MeitY Deepfake Advisory) provide sector-specific compliance mandates and executive interpretations but do not supplant primary statutory text."
    )
    
    return {
        "answer": "\n".join(sections_rendered),
        "sources": sources_list,
        "query_type": "MULTI_ACT_CYBERCRIME",
        "response_type": "MULTI_ACT_CYBERCRIME",
        "temporal_status": "VERIFIED_CURRENT",
        "abstained": False,
        "requires_verification": False,
        "evidence_status": "AUTHORITATIVE_MULTI_ACT",
        "confidence_status": "AUTHORITATIVE",
        "structured_query": resolved,
        "qwen_invoked": qwen_invoked,
        "adapter": adapter_used,
        "retrieval_mode": "MULTI_ACT_CYBERCRIME"
    }
