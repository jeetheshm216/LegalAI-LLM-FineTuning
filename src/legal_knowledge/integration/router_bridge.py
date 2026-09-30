"""Router bridge connecting conversational classification to Indian Legal Knowledge RAG."""

import re
from typing import Dict, Any, Optional, Tuple
from ..retrieval.pipeline import GeneralIndianLegalKnowledgePipeline


class IndianLegalRouterBridge:
    """Bridges query routing decisions to the General Indian Legal Knowledge engine, enforcing India-only scope."""

    # Foreign jurisdiction keywords to detect and politely redirect
    FOREIGN_LEGAL_TERMS = {
        "gdpr": {
            "topic": "data protection and privacy",
            "indian_framework": "the Digital Personal Data Protection Act, 2023 (DPDP Act) and the Information Technology Act, 2000 (Section 43A and SPDI Rules 2011)"
        },
        "us code": {
            "topic": "federal statutory law",
            "indian_framework": "applicable Indian Central Acts enacted by the Parliament of India"
        },
        "title 17": {
            "topic": "copyright law",
            "indian_framework": "the Indian Copyright Act, 1957"
        },
        "18 u.s.c": {
            "topic": "criminal offenses",
            "indian_framework": "the Bharatiya Nyaya Sanhita, 2023 (BNS) and the Indian Penal Code, 1860 (for pre-July 2024 matters)"
        },
        "us constitution": {
            "topic": "constitutional law",
            "indian_framework": "the Constitution of India, including Fundamental Rights under Part III and Writ Jurisdiction under Articles 32 and 226"
        },
        "uk human rights act": {
            "topic": "human rights law",
            "indian_framework": "Part III of the Constitution of India and the Protection of Human Rights Act, 1993"
        },
        "california consumer privacy act": {
            "topic": "consumer privacy",
            "indian_framework": "the Digital Personal Data Protection Act, 2023 (DPDP Act)"
        },
        "ccpa": {
            "topic": "consumer privacy",
            "indian_framework": "the Digital Personal Data Protection Act, 2023 (DPDP Act)"
        },
        "eur-lex": {
            "topic": "European Union law",
            "indian_framework": "the relevant Indian statutory and regulatory framework"
        }
    }

    def __init__(self, pipeline: Optional[GeneralIndianLegalKnowledgePipeline] = None):
        self.pipeline = pipeline or GeneralIndianLegalKnowledgePipeline()

    def check_foreign_law_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Checks if a user query is directed at foreign law, returning a polite Indian-law redirection response if so."""
        lower_q = query.lower()
        for term, info in self.FOREIGN_LEGAL_TERMS.items():
            # Use word boundary or exact match
            if re.search(r'\b' + re.escape(term) + r'\b', lower_q):
                redirect_msg = (
                    f"LegalAI currently focuses on Indian law. If you're looking for the Indian legal framework "
                    f"relevant to {info['topic']}, I can help with {info['indian_framework']}."
                )
                return True, redirect_msg
        return False, None

    def route_and_execute(
        self,
        query: str,
        intent: str = "LEGAL_QUERY",
        incident_date: Optional[str] = None,
        state: Optional[str] = None,
        court: Optional[str] = None
    ) -> Dict[str, Any]:
        """Routes query based on intent, intercepting foreign-law queries and delegating legal questions."""
        # 1. Check foreign law redirection
        is_foreign, redirect_response = self.check_foreign_law_query(query)
        if is_foreign:
            return {
                "answer": redirect_response,
                "sources": [],
                "intent": "OUT_OF_SCOPE_FOREIGN_LAW",
                "jurisdiction": "INDIA_FOCUSED_REDIRECT",
                "abstained": False
            }

        # 2. If legal query, query the Indian Legal Knowledge Pipeline
        if intent in ("LEGAL_QUERY", "AMBIGUOUS"):
            result = self.pipeline.query(
                question=query,
                incident_date=incident_date,
                state=state,
                court=court
            )
            result["intent"] = intent
            return result

        # 3. Non-legal intents handled upstream
        return {
            "answer": "This query was forwarded outside the Indian Legal Knowledge engine.",
            "sources": [],
            "intent": intent,
            "abstained": True
        }
