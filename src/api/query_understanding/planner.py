"""
src/api/query_understanding/planner.py

Response Planning & Structure Engine for LegalAI.
Enforces intent-specific output structures, section schemas, and token constraints.
"""

from typing import Dict, Any, List, Optional
from .goals import SubIntent, UserGoal, OutputPlan


class ResponsePlanner:
    """
    Translates user goal and output plan into explicit structural formatting
    instructions for generation models and length parameters.
    """

    STRUCTURE_GUIDANCE: Dict[OutputPlan, Dict[str, Any]] = {
        OutputPlan.KEY_POINTS: {
            "max_tokens": 256,
            "system_instruction": (
                "Provide concise, high-impact key points for the advocate.\n"
                "STRUCTURE:\n"
                "### KEY POINTS\n"
                "1. [First critical point with document/fact citation]\n"
                "2. [Second critical point with document/fact citation]\n"
                "3. [Third critical point with document/fact citation]\n\n"
                "RULE: Keep response strictly concise. Do NOT turn this into a complete case analysis."
            ),
            "instruction": (
                "Provide concise, high-impact key points for the advocate.\n"
                "STRUCTURE:\n"
                "### KEY POINTS\n"
                "1. [First critical point with document/fact citation]\n"
                "2. [Second critical point with document/fact citation]\n"
                "3. [Third critical point with document/fact citation]\n\n"
                "RULE: Keep response strictly concise. Do NOT turn this into a complete case analysis."
            ),
            "sections": ["KEY POINTS", "Key Points"]
        },
        OutputPlan.FOCUS_AREAS: {
            "max_tokens": 300,
            "system_instruction": (
                "Identify the primary substantive focus areas requiring advocate attention.\n"
                "STRUCTURE:\n"
                "### PRIORITY FOCUS AREAS\n"
                "1. [Core claim or factual priority with document citation]\n"
                "2. [Critical evidentiary verification needed]\n"
                "3. [Key tactical risk or issue]\n"
                "Ground all focus areas directly in the supplied case facts."
            ),
            "instruction": (
                "Identify the primary substantive focus areas requiring advocate attention.\n"
                "STRUCTURE:\n"
                "### PRIORITY FOCUS AREAS\n"
                "1. [Core claim or factual priority with document citation]\n"
                "2. [Critical evidentiary verification needed]\n"
                "3. [Key tactical risk or issue]\n"
                "Ground all focus areas directly in the supplied case facts."
            ),
            "sections": ["PRIORITY FOCUS AREAS"]
        },
        OutputPlan.CASE_SUMMARY: {
            "max_tokens": 350,
            "system_instruction": (
                "Provide a concise matter summary based strictly on the case record.\n"
                "STRUCTURE:\n"
                "### CASE SUMMARY\n"
                "**Matter**: [Case Title (Case Number)]\n"
                "**Court**: [Court Name]\n"
                "**Status**: [Current Procedural Status]\n"
                "**Next Hearing**: [Scheduled Date / Bench]\n\n"
                "**What the case is about**:\n"
                "[Short, grounded summary of the core dispute and parties]\n\n"
                "**Current procedural position**:\n"
                "[Grounded procedural status and latest order/proceeding]\n\n"
                "RULE: Do NOT automatically append Evidence Gaps, Arguments, Risks, or Next Steps unless explicitly requested."
            ),
            "instruction": (
                "Provide a concise matter summary based strictly on the case record.\n"
                "STRUCTURE:\n"
                "### CASE SUMMARY\n"
                "**Matter**: [Case Title (Case Number)]\n"
                "**Court**: [Court Name]\n"
                "**Status**: [Current Procedural Status]\n"
                "**Next Hearing**: [Scheduled Date / Bench]\n\n"
                "**What the case is about**:\n"
                "[Short, grounded summary of the core dispute and parties]\n\n"
                "**Current procedural position**:\n"
                "[Grounded procedural status and latest order/proceeding]\n\n"
                "RULE: Do NOT automatically append Evidence Gaps, Arguments, Risks, or Next Steps unless explicitly requested."
            ),
            "sections": ["CASE SUMMARY", "What the case is about", "Current procedural position"]
        },
        OutputPlan.ESTABLISHED_FACTS: {
            "max_tokens": 400,
            "system_instruction": (
                "Strictly classify facts without presenting allegations as established truth.\n"
                "STRUCTURE:\n"
                "### ESTABLISHED FACTS\n"
                "1. [Documented, undisputed fact with citation]\n"
                "### ALLEGATIONS / CLAIMS\n"
                "1. [Contested claim or assertion made by a party]\n"
                "### UNKNOWN / NOT ESTABLISHED\n"
                "1. [Critical elements not substantiated by the supplied documents]\n"
                "RULE: Never convert allegations or claims into established facts."
            ),
            "instruction": (
                "Strictly classify facts without presenting allegations as established truth.\n"
                "STRUCTURE:\n"
                "### ESTABLISHED FACTS\n"
                "1. [Documented, undisputed fact with citation]\n"
                "### ALLEGATIONS / CLAIMS\n"
                "1. [Contested claim or assertion made by a party]\n"
                "### UNKNOWN / NOT ESTABLISHED\n"
                "1. [Critical elements not substantiated by the supplied documents]\n"
                "RULE: Never convert allegations or claims into established facts."
            ),
            "sections": ["ESTABLISHED FACTS", "ALLEGATIONS / CLAIMS", "UNKNOWN / NOT ESTABLISHED"]
        },
        OutputPlan.KEY_ISSUES: {
            "max_tokens": 350,
            "system_instruction": (
                "Identify the primary legal and factual issues in dispute.\n"
                "STRUCTURE:\n"
                "### KEY ISSUES\n"
                "1. [Primary factual dispute with document basis]\n"
                "2. [Primary statutory / procedural issue]\n"
                "State the factual or legal basis for each issue."
            ),
            "instruction": (
                "Identify the primary legal and factual issues in dispute.\n"
                "STRUCTURE:\n"
                "### KEY ISSUES\n"
                "1. [Primary factual dispute with document basis]\n"
                "2. [Primary statutory / procedural issue]\n"
                "State the factual or legal basis for each issue."
            ),
            "sections": ["KEY ISSUES"]
        },
        OutputPlan.AVAILABLE_EVIDENCE: {
            "max_tokens": 450,
            "system_instruction": (
                "Provide an evidence-focused response based ONLY on the retrieved case documents.\n"
                "STRUCTURE:\n"
                "### EVIDENCE IDENTIFIED\n"
                "1. **[Document / Exhibit Name]**\n"
                "   - **What it establishes**: [Specific fact directly evidenced in the document]\n"
                "   - **Source**: [Page number and citation]\n\n"
                "2. **[Document / Exhibit Name]**\n"
                "   - **What it establishes**: [Specific fact directly evidenced in the document]\n"
                "   - **Source**: [Page number and citation]\n\n"
                "GROUNDING RULE: Only include evidence actually supported by retrieved documents.\n"
                "NEVER infer that contracts, affidavits, communications, or certified records exist merely because they are common.\n"
                "If the documents do not establish something, state: 'The currently available case documents do not establish this.'\n"
                "Do NOT append unrequested Evidence Gaps, Risks, or Next Steps."
            ),
            "instruction": (
                "Provide an evidence-focused response based ONLY on the retrieved case documents.\n"
                "STRUCTURE:\n"
                "### EVIDENCE IDENTIFIED\n"
                "1. **[Document / Exhibit Name]**\n"
                "   - **What it establishes**: [Specific fact directly evidenced in the document]\n"
                "   - **Source**: [Page number and citation]\n\n"
                "2. **[Document / Exhibit Name]**\n"
                "   - **What it establishes**: [Specific fact directly evidenced in the document]\n"
                "   - **Source**: [Page number and citation]\n\n"
                "GROUNDING RULE: Only include evidence actually supported by retrieved documents.\n"
                "NEVER infer that contracts, affidavits, communications, or certified records exist merely because they are common.\n"
                "If the documents do not establish something, state: 'The currently available case documents do not establish this.'\n"
                "Do NOT append unrequested Evidence Gaps, Risks, or Next Steps."
            ),
            "sections": ["EVIDENCE IDENTIFIED"]
        },
        OutputPlan.EVIDENCE_GAPS: {
            "max_tokens": 450,
            "system_instruction": (
                "Identify evidentiary gaps and missing records strictly based on the available case record.\n"
                "STRUCTURE:\n"
                "### EVIDENCE GAPS\n"
                "1. [Specific record or proof referenced in the case record but missing from supplied files]\n"
                "2. [Specific evidentiary discrepancy or unproven claim]\n\n"
                "### INFORMATION TO VERIFY\n"
                "1. [Specific fact, date, or certification to verify with client or issuing authority]\n"
                "2. [Authentication requirement or statutory compliance point]\n\n"
                "RULE: Do NOT manufacture missing documents or assume a document is missing merely because it is common in litigation.\n"
                "Do NOT include unrequested Key Points or Next Steps."
            ),
            "instruction": (
                "Identify evidentiary gaps and missing records strictly based on the available case record.\n"
                "STRUCTURE:\n"
                "### EVIDENCE GAPS\n"
                "1. [Specific record or proof referenced in the case record but missing from supplied files]\n"
                "2. [Specific evidentiary discrepancy or unproven claim]\n\n"
                "### INFORMATION TO VERIFY\n"
                "1. [Specific fact, date, or certification to verify with client or issuing authority]\n"
                "2. [Authentication requirement or statutory compliance point]\n\n"
                "RULE: Do NOT manufacture missing documents or assume a document is missing merely because it is common in litigation.\n"
                "Do NOT include unrequested Key Points or Next Steps."
            ),
            "sections": ["EVIDENCE GAPS", "INFORMATION TO VERIFY"]
        },
        OutputPlan.ARGUMENT_ANALYSIS: {
            "max_tokens": 450,
            "system_instruction": (
                "Structure strategic legal arguments and counterarguments.\n"
                "STRUCTURE:\n"
                "### POTENTIAL CASE ARGUMENTS\n"
                "- [Argument supporting our position with document basis]\n"
                "### COUNTERARGUMENTS\n"
                "- [Arguments opposing counsel can raise]\n"
                "### RISKS / WEAKNESSES\n"
                "- [Vulnerabilities to address]\n"
                "Clearly distinguish legal analysis from established facts."
            ),
            "instruction": (
                "Structure strategic legal arguments and counterarguments.\n"
                "STRUCTURE:\n"
                "### POTENTIAL CASE ARGUMENTS\n"
                "- [Argument supporting our position with document basis]\n"
                "### COUNTERARGUMENTS\n"
                "- [Arguments opposing counsel can raise]\n"
                "### RISKS / WEAKNESSES\n"
                "- [Vulnerabilities to address]\n"
                "Clearly distinguish legal analysis from established facts."
            ),
            "sections": ["POTENTIAL CASE ARGUMENTS", "COUNTERARGUMENTS", "RISKS / WEAKNESSES"]
        },
        OutputPlan.POTENTIAL_ARGUMENTS: {
            "max_tokens": 450,
            "system_instruction": (
                "Formulate potential case arguments supporting the client's position.\n"
                "STRUCTURE:\n"
                "### POTENTIAL CASE ARGUMENTS\n"
                "1. **[Core Legal / Factual Argument]**\n"
                "   - **Documented position**: [Direct factual basis from the record]\n"
                "   - **Potential legal argument**: [Legal framing or statutory application]\n"
                "   - **Inference requiring lawyer review**: [Analytical deduction for advocate assessment]\n\n"
                "RULE: Clearly distinguish documented facts from strategic legal arguments. Do NOT present generated legal strategy as established fact."
            ),
            "instruction": (
                "Formulate potential case arguments supporting the client's position.\n"
                "STRUCTURE:\n"
                "### POTENTIAL CASE ARGUMENTS\n"
                "1. **[Core Legal / Factual Argument]**\n"
                "   - **Documented position**: [Direct factual basis from the record]\n"
                "   - **Potential legal argument**: [Legal framing or statutory application]\n"
                "   - **Inference requiring lawyer review**: [Analytical deduction for advocate assessment]\n\n"
                "RULE: Clearly distinguish documented facts from strategic legal arguments. Do NOT present generated legal strategy as established fact."
            ),
            "sections": ["POTENTIAL CASE ARGUMENTS"]
        },
        OutputPlan.OPPOSING_ARGUMENTS: {
            "max_tokens": 450,
            "system_instruction": (
                "Identify realistic potential counterarguments that opposing counsel could raise.\n"
                "STRUCTURE:\n"
                "### POTENTIAL OPPOSING ARGUMENTS\n"
                "1. **[Opposing Argument / Defense]**\n"
                "   - **Basis**: [Record weakness or contractual/statutory clause opponent may rely on]\n"
                "   - **Points requiring rebuttal**: [Counter-evidence or legal response needed]\n\n"
                "RULE: Clearly label these as potential arguments rather than documented facts. Do not invent opposing claims unsupported by the matter context."
            ),
            "instruction": (
                "Identify realistic potential counterarguments that opposing counsel could raise.\n"
                "STRUCTURE:\n"
                "### POTENTIAL OPPOSING ARGUMENTS\n"
                "1. **[Opposing Argument / Defense]**\n"
                "   - **Basis**: [Record weakness or contractual/statutory clause opponent may rely on]\n"
                "   - **Points requiring rebuttal**: [Counter-evidence or legal response needed]\n\n"
                "RULE: Clearly label these as potential arguments rather than documented facts. Do not invent opposing claims unsupported by the matter context."
            ),
            "sections": ["POTENTIAL OPPOSING ARGUMENTS", "Points requiring rebuttal"]
        },
        OutputPlan.CASE_RISKS: {
            "max_tokens": 450,
            "system_instruction": (
                "Identify realistic case risks and vulnerabilities grounded in the record.\n"
                "STRUCTURE:\n"
                "### CASE RISKS / ISSUES\n"
                "1. **[Risk Item]**\n"
                "   - **Why it matters**: [Potential legal exposure, evidentiary weakness, or procedural pitfall]\n"
                "   - **What needs verification**: [Contemporaneous record or factual element to verify]\n\n"
                "RULE: Do not invent vulnerabilities unsupported by the case record."
            ),
            "instruction": (
                "Identify realistic case risks and vulnerabilities grounded in the record.\n"
                "STRUCTURE:\n"
                "### CASE RISKS / ISSUES\n"
                "1. **[Risk Item]**\n"
                "   - **Why it matters**: [Potential legal exposure, evidentiary weakness, or procedural pitfall]\n"
                "   - **What needs verification**: [Contemporaneous record or factual element to verify]\n\n"
                "RULE: Do not invent vulnerabilities unsupported by the case record."
            ),
            "sections": ["CASE RISKS / ISSUES", "Why it matters", "What needs verification"]
        },
        OutputPlan.CHRONOLOGICAL_TIMELINE: {
            "max_tokens": 400,
            "system_instruction": (
                "Present chronological events strictly using document dates, orders, filings, and case metadata.\n"
                "STRUCTURE:\n"
                "### CASE TIMELINE\n"
                "- **[Date / Period]**: [Specific event with document citation]\n"
                "- **[Date / Period]**: [Specific event with document citation]\n\n"
                "RULE: Chronological events only. Do NOT manufacture dates or chronological events not substantiated by the record."
            ),
            "instruction": (
                "Present chronological events strictly using document dates, orders, filings, and case metadata.\n"
                "STRUCTURE:\n"
                "### CASE TIMELINE\n"
                "- **[Date / Period]**: [Specific event with document citation]\n"
                "- **[Date / Period]**: [Specific event with document citation]\n\n"
                "RULE: Chronological events only. Do NOT manufacture dates or chronological events not substantiated by the record."
            ),
            "sections": ["CASE TIMELINE"]
        },
        OutputPlan.ACTIONABLE_NEXT_STEPS: {
            "max_tokens": 300,
            "system_instruction": (
                "Recommend grounded next procedural and preparation steps for the lawyer.\n"
                "STRUCTURE:\n"
                "### RECOMMENDED NEXT STEPS\n"
                "1. [Immediate procedural action or filing requirement]\n"
                "2. [Evidence gathering or client consultation step]\n"
                "3. [Legal research or objection preparation]"
            ),
            "instruction": (
                "Recommend grounded next procedural and preparation steps for the lawyer.\n"
                "STRUCTURE:\n"
                "### RECOMMENDED NEXT STEPS\n"
                "1. [Immediate procedural action or filing requirement]\n"
                "2. [Evidence gathering or client consultation step]\n"
                "3. [Legal research or objection preparation]"
            ),
            "sections": ["RECOMMENDED NEXT STEPS"]
        },
        OutputPlan.HEARING_BRIEF: {
            "max_tokens": 550,
            "system_instruction": (
                "Formulate a targeted hearing preparation outline for the upcoming proceeding.\n"
                "STRUCTURE:\n"
                "### NEXT HEARING PREPARATION\n"
                "**Hearing**: [Proceeding description]\n"
                "**Date**: [Hearing Date]\n"
                "**Court**: [Court / Bench]\n\n"
                "**Key issues to prepare**:\n"
                "1. [Disputed factual or legal issue before the bench]\n\n"
                "**Documents/evidence to review**:\n"
                "1. [Specific document name and page to review]\n\n"
                "**Questions to resolve**:\n"
                "1. [Anticipated query or factual gap to address]\n\n"
                "**Potential arguments**:\n"
                "1. [Key oral argument to advance]\n\n"
                "RULE: Do not automatically produce an entire generic case analysis."
            ),
            "instruction": (
                "Formulate a targeted hearing preparation outline for the upcoming proceeding.\n"
                "STRUCTURE:\n"
                "### NEXT HEARING PREPARATION\n"
                "**Hearing**: [Proceeding description]\n"
                "**Date**: [Hearing Date]\n"
                "**Court**: [Court / Bench]\n\n"
                "**Key issues to prepare**:\n"
                "1. [Disputed factual or legal issue before the bench]\n\n"
                "**Documents/evidence to review**:\n"
                "1. [Specific document name and page to review]\n\n"
                "**Questions to resolve**:\n"
                "1. [Anticipated query or factual gap to address]\n\n"
                "**Potential arguments**:\n"
                "1. [Key oral argument to advance]\n\n"
                "RULE: Do not automatically produce an entire generic case analysis."
            ),
            "sections": [
                "NEXT HEARING PREPARATION", "Key issues to prepare",
                "Documents/evidence to review", "Questions to resolve", "Potential arguments"
            ]
        },
        OutputPlan.DRAFTING_WORKFLOW: {
            "max_tokens": 600,
            "system_instruction": (
                "Provide a structured legal draft outline tailored to the specified document type.\n"
                "Use standardized legal formatting with verification placeholders ([CLIENT_NAME], [DATE], [FACT_A]).\n"
                "Never invent missing client facts; mark them with [VERIFY: ...] tags."
            ),
            "instruction": (
                "Provide a structured legal draft outline tailored to the specified document type.\n"
                "Use standardized legal formatting with verification placeholders ([CLIENT_NAME], [DATE], [FACT_A]).\n"
                "Never invent missing client facts; mark them with [VERIFY: ...] tags."
            ),
            "sections": ["Draft Structure", "Operative Clauses", "Verification Items"]
        },
        OutputPlan.DRAFTING_CLARIFICATION: {
            "max_tokens": 200,
            "system_instruction": (
                "Ask a concise, professional clarification on the desired document type."
            ),
            "instruction": (
                "Ask a concise, professional clarification on the desired document type."
            ),
            "sections": []
        },
        OutputPlan.CASE_PRIORITY_BRIEF: {
            "max_tokens": 450,
            "system_instruction": (
                "Provide a grounded, prioritized case assessment based strictly on actual case metadata, court orders, and evidence on record.\n"
                "Do NOT invent urgency. Do NOT assign arbitrary numerical priority scores (e.g., '9/10').\n"
                "STRUCTURE:\n"
                "### Priority Areas\n"
                "1. **Immediate Procedural Issue**\n"
                "   [Procedural posture, immediate deadlines, or injunction status]\n"
                "2. **Key Evidentiary Focus**\n"
                "   [Core documentary or witness elements requiring immediate attention]\n"
                "3. **Upcoming Hearing / Deadline**\n"
                "   [Documented next court appearance or filing timeline]\n"
                "4. **Items Requiring Verification**\n"
                "   [Unresolved facts or record gaps to confirm with client]"
            ),
            "instruction": (
                "Provide a grounded, prioritized case assessment based strictly on actual case metadata, court orders, and evidence on record.\n"
                "Do NOT invent urgency. Do NOT assign arbitrary numerical priority scores (e.g., '9/10').\n"
                "STRUCTURE:\n"
                "### Priority Areas\n"
                "1. **Immediate Procedural Issue**\n"
                "   [Procedural posture, immediate deadlines, or injunction status]\n"
                "2. **Key Evidentiary Focus**\n"
                "   [Core documentary or witness elements requiring immediate attention]\n"
                "3. **Upcoming Hearing / Deadline**\n"
                "   [Documented next court appearance or filing timeline]\n"
                "4. **Items Requiring Verification**\n"
                "   [Unresolved facts or record gaps to confirm with client]"
            ),
            "sections": ["Priority Areas", "Immediate Procedural Issue", "Key Evidentiary Focus", "Upcoming Hearing / Deadline", "Items Requiring Verification"]
        },
        OutputPlan.ASSISTANT_IDENTITY: {
            "max_tokens": 100,
            "system_instruction": (
                "State the assistant identity cleanly and professionally."
            ),
            "instruction": (
                "State the assistant identity cleanly and professionally."
            ),
            "sections": []
        }
    }

    @classmethod
    def get_structure_guidance(cls, output_plan: Any) -> Dict[str, Any]:
        """Returns the formatting rules and token limits for an output plan."""
        # Robustly resolve from string or Enum
        if isinstance(output_plan, str):
            try:
                output_plan = OutputPlan(output_plan)
            except ValueError:
                pass
        res = cls.STRUCTURE_GUIDANCE.get(output_plan, {
            "max_tokens": 512,
            "system_instruction": "",
            "instruction": "",
            "sections": []
        })
        # Standardize both instruction and system_instruction keys
        if "instruction" not in res and "system_instruction" in res:
            res["instruction"] = res["system_instruction"]
        elif "system_instruction" not in res and "instruction" in res:
            res["system_instruction"] = res["instruction"]
        return res

    @classmethod
    def get_token_limit(cls, output_plan: Any, length_preference: str = "balanced") -> int:
        """Calculates token limit based on plan and explicit user length preference."""
        guidance = cls.get_structure_guidance(output_plan)
        base_tokens = guidance.get("max_tokens", 512)
        if length_preference == "concise":
            return min(base_tokens, 256)
        elif length_preference == "comprehensive":
            return max(base_tokens, 768)
        return base_tokens
