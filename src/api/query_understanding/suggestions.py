"""
src/api/query_understanding/suggestions.py

Contextual Lawyer Suggestion Generator for LegalAI.
Provides 2-3 focused, actionable follow-up action chips tailored to the
sub-intent, user goal, and active matter state.
"""

from typing import List, Dict, Any, Optional
from .goals import SubIntent, OutputPlan


class SuggestionGenerator:
    """
    Generates tailored, scope-preserving suggestion chips for lawyers.
    """

    DEFAULT_SUGGESTIONS: Dict[SubIntent, List[Dict[str, str]]] = {
        SubIntent.CASE_KEY_POINTS: [
            {"label": "Prepare for next hearing", "query": "What should I prepare for the next hearing?"},
            {"label": "Review evidence gaps", "query": "What evidence is missing in this case?"},
            {"label": "Identify key arguments", "query": "What are our strongest arguments in this matter?"},
        ],
        SubIntent.CASE_SUMMARY: [
            {"label": "Review key issues", "query": "What are the main issues in this case?"},
            {"label": "Identify evidence gaps", "query": "What evidence are we missing?"},
            {"label": "Prepare for next hearing", "query": "What should I prepare before the hearing?"},
        ],
        SubIntent.CASE_FACTS: [
            {"label": "Evaluate evidence", "query": "What evidence supports our claims?"},
            {"label": "Check for contradictions", "query": "What contradictions are present in the record?"},
            {"label": "View timeline", "query": "Give me the chronological timeline of events."},
        ],
        SubIntent.CASE_ISSUES: [
            {"label": "Formulate arguments", "query": "What arguments can we raise on these issues?"},
            {"label": "Anticipate counterarguments", "query": "What can the other side argue?"},
            {"label": "Prepare hearing brief", "query": "Prepare me for the next hearing on these issues."},
        ],
        SubIntent.CASE_EVIDENCE: [
            {"label": "Identify missing evidence", "query": "What evidence is missing?"},
            {"label": "Build evidence timeline", "query": "Give me the chronological timeline of events."},
            {"label": "Review hearing prep", "query": "What should I take to court for the next hearing?"},
        ],
        SubIntent.CASE_EVIDENCE_GAPS: [
            {"label": "Analyze case risks", "query": "Where is our case weak based on these gaps?"},
            {"label": "Recommended next steps", "query": "What are the recommended next steps to fill these gaps?"},
            {"label": "Hearing preparation", "query": "How will these evidence gaps impact the next hearing?"},
        ],
        SubIntent.CASE_ARGUMENTS: [
            {"label": "Review counterarguments", "query": "What can the other side argue in response?"},
            {"label": "Check supporting evidence", "query": "What evidence do we have to support these points?"},
            {"label": "Prepare judge questions", "query": "What questions might the judge ask at the hearing?"},
        ],
        SubIntent.CASE_COUNTERARGUMENTS: [
            {"label": "Find evidence gaps", "query": "What evidence are we missing to counter this?"},
            {"label": "Review our arguments", "query": "What are our arguments in response?"},
            {"label": "Prepare for hearing", "query": "What should I prepare for the next hearing?"},
        ],
        SubIntent.CASE_RISKS: [
            {"label": "Mitigation next steps", "query": "What should we do to address these weaknesses?"},
            {"label": "Evidence to strengthen case", "query": "What evidence is needed to counter these risks?"},
            {"label": "Hearing strategy", "query": "How should we handle these risks before the judge?"},
        ],
        SubIntent.CASE_TIMELINE: [
            {"label": "Key case facts", "query": "What are the established facts in this case?"},
            {"label": "Check contradictions", "query": "Are there date or sequence contradictions in the record?"},
            {"label": "Prepare for hearing", "query": "What should I prepare for the upcoming hearing?"},
        ],
        SubIntent.CASE_NEXT_STEPS: [
            {"label": "Review hearing focus", "query": "What should I prepare for the next hearing?"},
            {"label": "Check evidence gaps", "query": "What documents do we need to request?"},
            {"label": "Draft document", "query": "Draft a notice for this matter."},
        ],
        SubIntent.HEARING_PREPARATION: [
            {"label": "Review key issues", "query": "What are the main issues to focus on?"},
            {"label": "Check evidence gaps", "query": "What evidence are we missing before the hearing?"},
            {"label": "Draft hearing document", "query": "Draft an affidavit for this case."},
        ],
        SubIntent.CASE_DRAFTING: [
            {"label": "Review key facts", "query": "What are the key facts to include in the draft?"},
            {"label": "Check required evidence", "query": "What evidence supports the claims in this draft?"},
            {"label": "Prepare next steps", "query": "What are the procedural next steps after filing?"},
        ],
        SubIntent.EXACT_STATUTORY_PROVISION: [
            {"label": "Check punishment", "query": "What is the punishment prescribed under this section?"},
            {"label": "Bail & Cognizability", "query": "Is this offence cognizable and bailable?"},
            {"label": "Related procedural rules", "query": "What procedure applies for investigating this offence?"},
        ],
        SubIntent.LEGAL_CONCEPT: [
            {"label": "Statutory provisions", "query": "Which sections of BNS or relevant statutes apply to this?"},
            {"label": "Leading case law", "query": "What are the essential ingredients required to prove this?"},
            {"label": "Procedural remedies", "query": "What legal remedy or relief is available?"},
        ],
        SubIntent.SYSTEM_SPECIFICATION: [
            {"label": "How Legal RAG works", "query": "Explain how LegalAI retrieves statutory provisions."},
            {"label": "Supported Acts & Corpus", "query": "What legal statutes and corpuses are supported?"},
            {"label": "Case isolation guarantee", "query": "How does LegalAI maintain case document privacy?"},
        ],
        SubIntent.TECHNICAL_CONCEPT: [
            {"label": "Explain RAG in LegalAI", "query": "Explain retrieval augmented generation in LegalAI."},
            {"label": "Base model vs LoRA", "query": "What is the difference between Qwen base model and LoRA adapters?"},
            {"label": "Vector search vs BM25", "query": "How does hybrid search combine vector and lexical retrieval?"},
        ],
        SubIntent.PORTFOLIO_WORKLOAD: [
            {"label": "Most urgent matter", "query": "What is my most urgent case?"},
            {"label": "Hearings this week", "query": "What hearings are scheduled this week?"},
            {"label": "Deadlines overview", "query": "Which cases have upcoming deadlines?"},
        ],
    }

    @classmethod
    def generate_suggestions(
        cls,
        sub_intent: SubIntent,
        case_id: Optional[str] = None,
        case_metadata: Optional[Dict[str, Any]] = None,
        max_suggestions: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generates 2-3 focused suggestions.
        Ensures suggestions are contextually relevant to the active case if present.
        """
        if isinstance(sub_intent, str):
            try:
                sub_intent = SubIntent(sub_intent)
            except ValueError:
                pass
        candidates = cls.DEFAULT_SUGGESTIONS.get(sub_intent, [])
        if not candidates:
            if case_id:
                return [
                    {"label": "Review key points", "query": "What are the key points in this case?"},
                    {"label": "Check evidence", "query": "What evidence do we have in this case?"},
                    {"label": "Prepare for hearing", "query": "What should I prepare for the next hearing?"}
                ][:max_suggestions]
            return []

        # If we have case metadata with hearing within 7 days, prioritize hearing prep
        results = list(candidates)
        if case_metadata and case_id:
            countdown = case_metadata.get("hearingCountdownDays")
            if countdown is not None and countdown <= 7:
                # Prioritize hearing prep if not already first
                hearing_items = [c for c in results if "hearing" in c["label"].lower()]
                other_items = [c for c in results if "hearing" not in c["label"].lower()]
                results = hearing_items + other_items

        return results[:max_suggestions]
