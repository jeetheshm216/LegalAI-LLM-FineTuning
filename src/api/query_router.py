"""
src/api/query_router.py

Lightweight, deterministic query router for LegalAI.
Classifies user incoming messages into:
  - CONVERSATIONAL: greetings, gratitude, assistant identity, capabilities, general banter.
  - LEGAL_QUERY: statutory questions, legal definitions, offences, penalties, procedures,
                 including both in-corpus (BNS, BNSS, BSA) and out-of-corpus legal statutes
                 (Constitution, NI Act, RERA, IT Act, Companies Act, etc.).
  - CASE_QUERY: matter-specific inquiries, evidence analysis, judgment analysis, FIR review,
                case documents, client/opposing counsel questions.

CRITICAL SAFETY RULES:
1. The router is conservative: greetings or polite phrases NEVER override legal or case intent.
   (e.g., "Hi, what is Section 103 BNS?" -> LEGAL_QUERY; "Hello, analyze my FIR" -> CASE_QUERY).
2. Out-of-corpus legal queries must ALWAYS route to LEGAL_QUERY so they reach the existing
   RAG pipeline for verified abstention (OUT_OF_CORPUS / Requires verification).
3. If uncertain between conversational and legal, default to LEGAL_QUERY.
4. Uses conversation history context when available to maintain intent on short follow-ups.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class QueryIntent(str, Enum):
    CONVERSATIONAL = "CONVERSATIONAL"
    LEGAL_QUERY = "LEGAL_QUERY"
    CASE_QUERY = "CASE_QUERY"


@dataclass
class RoutingResult:
    intent: QueryIntent
    confidence: float
    reason: str
    matched_patterns: List[str]


class QueryRouter:
    """Deterministic, rule-based classifier for routing user queries."""

    # -------------------------------------------------------------------------
    # 1. CASE_QUERY PATTERNS
    # Specific legal matter, dispute, document, client, FIR, petition, judgment
    # -------------------------------------------------------------------------
    CASE_MATTER_PATTERNS = [
        # Explicit case / client references
        r'\b(?:my|our|this|the)\s+case\b',
        r'\b(?:my|our|this|the)?\s*client(?:\'?s)?\s+(?:case|position|argument|matter|defense|defence|claim|fir|petition|complaint)\b',
        r'\bclient(?:\'?s)?\s+(?:case|position|fir|petition|complaint|advocate|counsel)\b',
        r'\b(?:in|for)\s+this\s+matter\b',
        r'\b(?:analyze|analyse|summarize|summarise|review)\s+.*?(?:case|matter|fir|judgment|judgement|petition|order|contract|agreement)\b',
        r'\bstrongest\s+(?:arguments?|points?)\b',
        r'\bweaknesses?\s+in\s+(?:this|the|my|our)\s+case\b',
        r'\brisks?\s+of\s+pursuing\b',
        r'\barguments?\s+can\s+the\s+opposing\s+counsel\s+make\b',
        r'\bopposing\s+(?:counsel|party)\b',
        r'\bwitness\s+statements?\b',
        r'\binconsistencies\s+in\s+(?:the\s+)?witness\b',
        # Pleading / case document references
        r'\b(?:this|my|our|the|client(?:\'?s)?)\s+(?:petition|fir|complaint|chargesheet|charge\s*sheet|judgment|judgement|order|affidavit|pleadings?|written\s+statement)\b',
        r'\bwhat\s+should\s+we\s+challenge\s+in\s+this\s+(?:petition|fir|complaint|appeal)\b',
        r'\b(?:uploaded|attached)\s+(?:document|file|record|evidence)\b',
        r'\bdocuments?\s+(?:are\s+)?missing\b',
        r'\bwhat\s+documents?\s+are\s+missing\b',
        r'\b(?:last|next)\s+hearing\b',
        r'\bwhat\s+happened\s+(?:at|in)\s+(?:the\s+last\s+hearing|my\s+case|this\s+case)\b',
        r'\bkey\s+facts\s+(?:in|of)\s+(?:this|my|the)\s+(?:case|matter|judgment|judgement)\b',
        r'\bevidence\s+supports\s+our\s+(?:position|case|argument)\b',
        r'\bwhat\s+evidence\s+supports\b',
        r'\bwhat\s+can\s+you\s+do\s+with\s+this\s+(?:judgment|judgement|case|document|file)\b',
        # Evidence analysis, verification, gaps, contradictions & hearing prep
        r'\b(?:what\s+)?evidence\s+is\s+missing\b',
        r'\bevidence\s+gaps?\b',
        r'\bcontradictions?\s+(?:exist|between|in)\b',
        r'\bare\s+there\s+contradictions?\b',
        r'\bwhat\s+contradictions?\b',
        r'\bverify\s+before\s+submitting\b',
        r'\bverif(?:ied|ication)\s+before\s+submitting\b',
        r'\bis\s+this\s+evidence\s+ready\b',
        r'\bchain\s+of\s+custody\b',
        r'\bsupporting\s+documents?\s+(?:are\s+)?referred\s+to\b',
        r'\bstrengths?\s+and\s+weaknesses?\b',
        r'\bprepare\s+me\s+for\s+(?:the\s+)?(?:next\s+)?hearing\b',
        r'\bhearing\s+preparation\b',
        r'\barguments?\s+(?:can\s+we|to)\s+make\b',
        r'\bavailable\s+evidence\b',
    ]

    # -------------------------------------------------------------------------
    # 2. LEGAL_QUERY PATTERNS
    # Statutory sections, acts, penal provisions, procedural rights, legal terms
    # Covers BOTH in-corpus (BNS/BNSS/BSA) and out-of-corpus legal domains.
    # -------------------------------------------------------------------------
    STATUTE_SECTION_PATTERNS = [
        # Explicit section / article citations
        r'\b(?:section|sec\.?|u/s|§)\s*[0-9]+[A-Za-z]*\b',
        r'\barticle\s+[0-9]+[A-Za-z]*\b',
        r'\border\s+[0-9IVXLCDM]+\s+(?:rule\s+[0-9]+)?\b',
        r'\bclause\s+[0-9]+(?:\([a-z0-9]+\))*\b',
        r'\bschedule\s+[0-9IVXLCDM]+\b',
    ]

    ACT_NAME_PATTERNS = [
        # Core criminal enactments
        r'\b(?:bns|bnss|bsa)\b',
        r'\bbharatiya\s+nyaya\s+sanhita\b',
        r'\bbharatiya\s+nagarik\s+suraksha\s+sanhita\b',
        r'\bbharatiya\s+sakshya\s+adhiniyam\b',
        r'\b(?:ipc|crpc|iea)\b',
        r'\bindian\s+penal\s+code\b',
        r'\bcode\s+of\s+criminal\s+procedure\b',
        r'\b(?:indian\s+)?evidence\s+act\b',
        # Major statutory domains (out of corpus or general law)
        r'\bconstitution\s+of\s+india\b',
        r'\bconstitutional\s+law\b',
        r'\bnegotiable\s+instruments?\s+(?:act)?\b',
        r'\bni\s+act\b',
        r'\brera\b',
        r'\breal\s+estate\s+(?:regulation|regulatory)\b',
        r'\bcompanies\s+act\b',
        r'\bcontract\s+act\b',
        r'\barbitration\s+(?:and\s+conciliation\s+)?act\b',
        r'\btransfer\s+of\s+property\s+act\b',
        r'\blimitation\s+act\b',
        r'\bconsumer\s+protection\s+act\b',
        r'\bmotor\s+vehicles?\s+act\b',
        r'\bmva\b',
        r'\binformation\s+technology\s+act\b',
        r'\bit\s+act\b',
        r'\bpocso\b',
        r'\bndps\b',
        r'\bpmla\b',
        r'\buapa\b',
        r'\bposh\s+act\b',
        r'\bsarfaesi\b',
        r'\bibc\b',
        r'\binsolvency\s+and\s+bankruptcy\b',
        r'\bfamily\s+courts?\s+act\b',
        r'\bhindu\s+marriage\s+act\b',
        r'\bspecific\s+relief\s+act\b',
        r'\bgst\s+act\b',
        r'\bincome\s+tax\s+act\b',
        r'\blabour\s+laws?\b',
        r'\bcivil\s+procedure\s+code\b',
        r'\bcpc\b',
        r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Act,\s*(?:18|19|20)[0-9]{2}\b',
        r'\b[A-Za-z\s]+(?:Act|Code|Sanhita|Adhiniyam|Ordinance|Rules),\s*(?:18|19|20)[0-9]{2}\b',
    ]

    SUBSTANTIVE_LEGAL_TERMS = [
        # Offences & Penal Concepts
        r'\bmurder\b',
        r'\bculpable\s+homicide\b',
        r'\bpunishment\s+for\s+[a-z\s]+\b',
        r'\btheft\b',
        r'\brobbery\b',
        r'\bdacoity\b',
        r'\bextortion\b',
        r'\bcheating\b',
        r'\bfraud\b',
        r'\bforgery\b',
        r'\bcheque\s+(?:bounce|dishonour|dishonor)\b',
        r'\brape\b',
        r'\bsexual\s+assault\b',
        r'\bstalking\b',
        r'\bassault\b',
        r'\bcriminal\s+(?:breach\s+of\s+trust|misappropriation|force|intimidation|trespass|conspiracy)\b',
        r'\bgrievous\s+hurt\b',
        r'\bkidnapping\b',
        r'\babduction\b',
        r'\bdefamation\b',
        r'\bsedition\b',
        r'\bperjury\b',
        r'\babetment\b',
        r'\bcruelty\b',
        r'\bdowry\s+death\b',
        r'\bquashing\b',
        r'\bdischarge\b',
        r'\bcognizance\b',
        r'\bbail\b',
        r'\banticipatory\s+bail\b',
        r'\bregular\s+bail\b',
        r'\binterim\s+bail\b',
        r'\bdefault\s+bail\b',
        r'\bremand\b',
        r'\bpolice\s+custody\b',
        r'\bjudicial\s+custody\b',
        r'\barrest\b',
        r'\bfir\b',
        r'\bfirst\s+information\s+report\b',
        r'\bchargesheet\b',
        r'\bcharge\s+sheet\b',
        r'\bcognizable\b',
        r'\bnon-cognizable\b',
        r'\bbailable\b',
        r'\bnon-bailable\b',
        r'\bcompoundable\b',
        r'\blimitation\s+period\b',
        r'\bcondonation\s+of\s+delay\b',
        r'\bjurisdiction\b',
        r'\badmissibility\b',
        r'\belectronic\s+(?:records?|evidence)\b',
        r'\bsecondary\s+evidence\b',
        r'\bprimary\s+evidence\b',
        r'\bburden\s+of\s+proof\b',
        r'\bpresumption\b',
        r'\bconfession\b',
        r'\bdying\s+declaration\b',
        r'\bexpert\s+opinion\b',
        r'\bcross-examination\b',
        r'\bexamination-in-chief\b',
        r'\bappeal\b',
        r'\brevision\b',
        r'\bspecial\s+leave\s+petition\b',
        r'\bslp\b',
        r'\bwrit\s+petition\b',
        r'\bhabeas\s+corpus\b',
        r'\bmandamus\b',
        r'\binjunction\b',
        r'\bstay\s+order\b',
        r'\bdamages\b',
        r'\bmens\s+rea\b',
        r'\bactus\s+reus\b',
        r'\bretrospective\b',
        r'\bex\s+post\s+facto\b',
        r'\barticle\s+20(?:\(1\))?\b',
        r'\bfundamental\s+rights?\b',
        r'\bdirective\s+principles?\b',
        r'\bprosecution\b',
        r'\btrial\b',
        r'\bprocedure\s+for\s+(?:filing|appeal|bail|arrest|investigation)\b',
        r'\bwhich\s+law\s+applies\b',
        r'\bwhat\s+law\s+applies\b',
        r'\bwhat\s+is\s+the\s+(?:punishment|penalty|law|limitation)\b',
        r'\bis\s+(?:this|an|the)?\s*offence\s+bailable\b',
        r'\bcan\s+(?:an?\s+)?accused\b',
        r'\brights\s+of\s+(?:an?\s+)?accused\b',
        r'\bperiod\s+of\s+limitation\b',
    ]

    # -------------------------------------------------------------------------
    # 3. CONVERSATIONAL PATTERNS
    # Greetings, gratitude, assistant identity, capabilities, courteous chatter.
    # -------------------------------------------------------------------------
    CONVERSATIONAL_GREETINGS = [
        r'^(?:hi|hello|hey|hiya|howdy|good\s+(?:morning|afternoon|evening|day)|greetings)(?:[\s,!.]+)?$',
        r'^(?:hi|hello|hey)\s+(?:there|legalai|assistant|again)(?:[\s,!.]+)?$',
        r'^(?:hi|hello|hey)[,\s]+who\s+are\s+you(?:[\s,?!.]+)?$',
        r'^(?:hi|hello|hey)[,\s]+how\s+are\s+you(?:[\s,?!.]+)?$',
        r'^(?:hi|hello|hey)[,\s]+how\'s\s+it\s+going(?:[\s,?!.]+)?$',
        r'^(?:hi|hello|hey)[,\s]+how\s+can\s+you\s+help(?:\s+me)?(?:[\s,?!.]+)?$',
        r'^(?:hi|hello|hey)[,\s]+what\s+can\s+you\s+do(?:[\s,?!.]+)?$',
    ]

    CONVERSATIONAL_GRATITUDE = [
        r'^(?:thanks|thank\s+you|thank\s+you\s+(?:so\s+much|very\s+much)|many\s+thanks|appreciate\s+it|thx)(?:[\s,!.]+)?$',
        r'^(?:thanks|thank\s+you)[,\s]+(?:legalai|for\s+(?:your\s+help|the\s+help|explaining))(?:[\s,!.]+)?$',
        r'^(?:ok\s+thanks|okay\s+thanks|great\s+thanks)(?:[\s,!.]+)?$',
    ]

    CONVERSATIONAL_IDENTITY_CAPABILITY = [
        r'^(?:who\s+are\s+you|what\s+are\s+you|what\s+is\s+your\s+name|are\s+you\s+an?\s+ai)(?:[\s,?!.]+)?$',
        r'^(?:what\s+can\s+you\s+do|what\s+do\s+you\s+do|how\s+can\s+you\s+help(?:\s+me)?)(?:[\s,?!.]+)?$',
        r'^(?:what\s+are\s+your\s+(?:capabilities|features)|explain\s+your\s+capabilities)(?:[\s,?!.]+)?$',
        r'^(?:tell\s+me\s+about\s+(?:yourself|legalai)|introduce\s+yourself)(?:[\s,?!.]+)?$',
        r'^(?:help|help\s+me)(?:[\s,?!.]+)?$',
        r'^(?:tell\s+me\s+a\s+joke(?:\s+about\s+[a-z\s]+)?)(?:[\s,?!.]+)?$',
    ]

    CONVERSATIONAL_SMALLTALK = [
        r'^(?:how\s+are\s+you|how\s+are\s+you\s+doing|how\'s\s+it\s+going)(?:[\s,?!.]+)?$',
        r'^(?:nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)(?:[\s,!.]+)?$',
        r'^(?:ok|okay|got\s+it|understood|cool|great|awesome|perfect|sure|alright|fine)(?:[\s,!.]+)?$',
        r'^(?:bye|goodbye|see\s+you|have\s+a\s+(?:nice|good)\s+day)(?:[\s,!.]+)?$',
    ]

    def __init__(self):
        # Compile all regexes once for high-performance deterministic matching
        self._case_regexes = [re.compile(p, re.IGNORECASE) for p in self.CASE_MATTER_PATTERNS]
        self._statute_regexes = [re.compile(p, re.IGNORECASE) for p in self.STATUTE_SECTION_PATTERNS]
        self._act_regexes = [re.compile(p, re.IGNORECASE) for p in self.ACT_NAME_PATTERNS]
        self._legal_term_regexes = [re.compile(p, re.IGNORECASE) for p in self.SUBSTANTIVE_LEGAL_TERMS]

        self._conv_regexes = [
            re.compile(p, re.IGNORECASE) for p in (
                self.CONVERSATIONAL_GREETINGS +
                self.CONVERSATIONAL_GRATITUDE +
                self.CONVERSATIONAL_IDENTITY_CAPABILITY +
                self.CONVERSATIONAL_SMALLTALK
            )
        ]

    def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> RoutingResult:
        """
        Deterministically classifies incoming message into CONVERSATIONAL, LEGAL_QUERY, or CASE_QUERY.
        
        Strict Priority Order:
        1. Check for Case / Matter specific inquiry -> CASE_QUERY
        2. Check for Legal / Statutory terminology or queries -> LEGAL_QUERY
        3. Check for Conversational / Greeting intent -> CONVERSATIONAL
        4. Check conversation context if message is a short ambiguous follow-up
        5. Default safe fallback -> LEGAL_QUERY (ensures RAG grounding / verified abstention)
        """
        cleaned = message.strip()
        if not cleaned:
            return RoutingResult(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=1.0,
                reason="Empty or whitespace query treated as conversational prompt.",
                matched_patterns=["EMPTY_QUERY"]
            )

        matched_case = []
        for r in self._case_regexes:
            m = r.search(cleaned)
            if m:
                matched_case.append(m.group(0))

        matched_legal = []
        for r in self._statute_regexes:
            m = r.search(cleaned)
            if m:
                matched_legal.append(m.group(0))
        for r in self._act_regexes:
            m = r.search(cleaned)
            if m:
                matched_legal.append(m.group(0))
        for r in self._legal_term_regexes:
            m = r.search(cleaned)
            if m:
                matched_legal.append(m.group(0))

        # ---------------------------------------------------------------------
        # PRIORITY 1: CASE_QUERY
        # If matter-specific keywords matched (e.g. "my case", "analyze this FIR",
        # "witness inconsistencies", "documents missing", "last hearing")
        # ---------------------------------------------------------------------
        if matched_case:
            return RoutingResult(
                intent=QueryIntent.CASE_QUERY,
                confidence=0.95,
                reason="Query addresses specific case matter, client position, or evidentiary documents.",
                matched_patterns=matched_case
            )

        # ---------------------------------------------------------------------
        # PRIORITY 2: LEGAL_QUERY
        # If statutory sections, enactments, penal concepts, or procedural rights matched.
        # This ALWAYS overrides greetings (e.g. "Hi, what is Section 103 BNS?" -> LEGAL_QUERY).
        # Out-of-corpus acts (NI Act, RERA, Constitution) are strictly caught here.
        # ---------------------------------------------------------------------
        if matched_legal:
            return RoutingResult(
                intent=QueryIntent.LEGAL_QUERY,
                confidence=0.98,
                reason="Query contains explicit statutory citations, enactments, or substantive legal concepts.",
                matched_patterns=matched_legal
            )

        # ---------------------------------------------------------------------
        # PRIORITY 3: CONVERSATIONAL
        # Only reached if ZERO legal keywords and ZERO case patterns were found.
        # Checks against greetings, gratitude, assistant identity, capabilities.
        # ---------------------------------------------------------------------
        for r in self._conv_regexes:
            m = r.match(cleaned)
            if m:
                return RoutingResult(
                    intent=QueryIntent.CONVERSATIONAL,
                    confidence=0.95,
                    reason="Message is an ordinary conversational greeting, capability inquiry, or gratitude.",
                    matched_patterns=[m.group(0)]
                )

        # ---------------------------------------------------------------------
        # PRIORITY 4: CONVERSATION CONTEXT FOLLOW-UP
        # If message is a short query without explicit keywords (e.g. "What about punishment?",
        # "Can you explain further?", "What is the penalty?"), check previous turn.
        # ---------------------------------------------------------------------
        if conversation_history and len(conversation_history) > 0:
            last_msg = conversation_history[-1]
            last_content = str(last_msg.get("content", "")).lower()
            # If the user asks a short follow-up after a legal query:
            if any(term in last_content for term in ["section", "bns", "bnss", "bsa", "act", "offence", "bail", "law"]):
                if len(cleaned.split()) <= 8:
                    return RoutingResult(
                        intent=QueryIntent.LEGAL_QUERY,
                        confidence=0.85,
                        reason="Contextual follow-up to previous legal query.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_LEGAL"]
                    )

        # ---------------------------------------------------------------------
        # PRIORITY 5: CONSERVATIVE FALLBACK -> LEGAL_QUERY
        # If the intent cannot be confirmed as pure conversational, default to LEGAL_QUERY.
        # This prevents accidental bypassing of statutory RAG and legal safeguards.
        # ---------------------------------------------------------------------
        return RoutingResult(
            intent=QueryIntent.LEGAL_QUERY,
            confidence=0.70,
            reason="Uncertain intent conservatively defaulted to LEGAL_QUERY for authoritative grounding.",
            matched_patterns=["CONSERVATIVE_FALLBACK"]
        )


# Global singleton router instance
_GLOBAL_ROUTER: Optional[QueryRouter] = None


def get_query_router() -> QueryRouter:
    """Returns the singleton QueryRouter instance."""
    global _GLOBAL_ROUTER
    if _GLOBAL_ROUTER is None:
        _GLOBAL_ROUTER = QueryRouter()
    return _GLOBAL_ROUTER
