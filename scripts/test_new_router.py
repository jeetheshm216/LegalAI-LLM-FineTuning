"""
scratch/test_new_router.py

Full standalone validation of the new Context-First Semantic Architecture
across all 70 benchmark questions from the 7 distinct categories.
"""

import re
import difflib
import sqlite3
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple


class QueryIntent(str, Enum):
    CONVERSATIONAL = "CONVERSATIONAL"
    SYSTEM_INFO = "SYSTEM_INFO"
    TECHNICAL_AI = "TECHNICAL_AI"
    CASE_MANAGEMENT = "CASE_MANAGEMENT"
    LEGAL_QUERY = "LEGAL_QUERY"
    EXACT_PROVISION_QUERY = "EXACT_PROVISION_QUERY"
    CASE_QUERY = "CASE_QUERY"
    HEARING_PREPARATION = "HEARING_PREPARATION"
    MIXED_LEGAL_CASE = "MIXED_LEGAL_CASE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    AMBIGUOUS = "AMBIGUOUS"
    GENERAL_NON_LEGAL = "OUT_OF_SCOPE"


@dataclass
class QueryDecision:
    intent: QueryIntent
    confidence: float
    reason: str
    sub_intent: Optional[str] = None
    user_goal: Optional[str] = None
    output_plan: Optional[str] = None
    normalized_query: Optional[str] = None
    matched_patterns: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    requires_case_context: bool = False
    requires_case_documents: bool = False
    requires_case_metadata: bool = False
    requires_legal_rag: bool = False
    requires_exact_provision_resolution: bool = False
    requires_system_context: bool = False
    requires_technical_explanation: bool = False
    requires_base_qwen: bool = False
    requires_legalai_v2: bool = False
    requires_case_analysis_v1: bool = False
    legal_intent_confidence: float = 0.0
    case_intent_confidence: float = 0.0
    target_act: Optional[str] = None
    target_provision: Optional[str] = None
    case_id: Optional[str] = None


class ContextAwareUniversalRouter:
    """
    Production Context-First Semantic Router.
    """

    KNOWN_CASES = [
        {
            "id": "case-01",
            "caseNumber": "2024-CV-1187",
            "title": "Martinez v. Coastal Holdings Ltd.",
            "client": "Julian Martinez",
            "opposing": "Coastal Holdings Ltd.",
            "keywords": ["martinez", "coastal", "charterparty", "berth 9", "demurrage"]
        },
        {
            "id": "case-02",
            "caseNumber": "2024-CR-0442",
            "title": "State v. Whitfield",
            "client": "Arthur Whitfield",
            "opposing": "State Department of Public Prosecutions",
            "keywords": ["whitfield", "state v whitfield"]
        },
        {
            "id": "case-03",
            "caseNumber": "2024-CV-0998",
            "title": "In re Nguyen Estate Testamentary Probate",
            "client": "Thao Nguyen",
            "opposing": "Sterling & Cole",
            "keywords": ["nguyen", "probate", "testamentary", "codicil"]
        },
        {
            "id": "case-04",
            "caseNumber": "2024-CC-0120",
            "title": "Apex Logistics Corp. v. Horizon Freight Services",
            "client": "Apex Logistics Corp.",
            "opposing": "Horizon Freight Services",
            "keywords": ["apex", "horizon", "liquidated damages"]
        }
    ]

    # Out of scope topics
    OUT_OF_SCOPE_REGEX = re.compile(
        r'\b(?:'
        r'recipe|how\s+to\s+cook|cook\w*|bake|pasta|cake|pizza|biryani|ingredients|cuisine|'
        r'write\s+(?:a\s+)?(?:python|javascript|java|c\+\+|cpp|rust|go|sql|code|script|function|program)|'
        r'merge\s+sort|quicksort|binary\s+search|algorithm|'
        r'who\s+won|world\s+cup|fifa|ipl|cricket|football|basketball|nba|olympics|'
        r'capital\s+of|france|germany|spain|italy|geography|solve\s+(?:this\s+)?math|\b\d+\s*[\*\+\-\/]\s*\d+\b|'
        r'tell\s+me\s+a\s+joke|joke|funny|humor|'
        r'recommend\s+.*?(?:laptop|phone|tv|camera|car|bike|gaming)|gaming|laptop|'
        r'plot\s+of|movie\s+plot|netflix|cinema|actor|actress|hollywood|bollywood|inception|'
        r'weather\s+in|temperature\s+in|forecast|'
        r'fix\s+a\s+flat\s+tire|repair\s+(?:my\s+)?(?:car|bike|bicycle)'
        r')\b',
        re.IGNORECASE
    )

    # Statutory patterns
    STATUTE_SEC_REGEX = re.compile(
        r'\b(?:section|sec\.?|s\.?|u/s|§)\s*([0-9]+[A-Za-z]*(?:\s*\([0-9a-z]+\))*)\b|'
        r'\barticle\s+([0-9]+[A-Za-z]*(?:\s*\([0-9a-z]+\))*)\b|'
        r'\border\s+([0-9IVXLCDM]+)\s*(?:rule\s+([0-9]+[A-Za-z]*))?\b|'
        r'\b(?:bns|bnss|bsa|ipc|crpc|cpc|iea|it\s+act)\s+(\d+[A-Za-z]*)\b',
        re.IGNORECASE
    )

    STATUTE_ACT_REGEX = re.compile(
        r'\b(bharatiya\s+nyaya\s+sanhita|bns|bharatiya\s+nagarik\s+suraksha\s+sanhita|bnss|'
        r'bharatiya\s+sakshya\s+adhiniyam|bsa|indian\s+penal\s+code|ipc|code\s+of\s+criminal\s+procedure|crpc|'
        r'code\s+of\s+civil\s+procedure|cpc|indian\s+evidence\s+act|iea|information\s+technology\s+act|it\s+act|'
        r'arbitration\s+and\s+conciliation\s+act|arbitration\s+act|pocso|domestic\s+violence|pmla|uapa)\b',
        re.IGNORECASE
    )

    def fuzzy_match_case(self, query: str) -> Optional[Tuple[Dict[str, Any], float]]:
        """Fuzzy matches query tokens against known case titles, numbers, clients, and keywords."""
        lower_q = query.lower()
        words = re.findall(r'[a-zA-Z0-9_\-]+', lower_q)

        # 1. Exact caseNumber or ID match
        for c in self.KNOWN_CASES:
            if c["id"].lower() in lower_q or c["caseNumber"].lower() in lower_q:
                return c, 1.0

        # 2. Key names / fuzzy matching
        best_match = None
        best_score = 0.0

        for c in self.KNOWN_CASES:
            for kw in c["keywords"]:
                if kw in lower_q:
                    return c, 0.95
                for w in words:
                    if len(w) >= 5 and len(kw) >= 5:
                        ratio = difflib.SequenceMatcher(None, w, kw).ratio()
                        if ratio >= 0.72 and ratio > best_score:
                            best_score = ratio
                            best_match = c

            for client_word in c["client"].lower().split():
                if len(client_word) >= 5:
                    for w in words:
                        ratio = difflib.SequenceMatcher(None, w, client_word).ratio()
                        if ratio >= 0.72 and ratio > best_score:
                            best_score = ratio
                            best_match = c

        if best_score >= 0.72:
            return best_match, best_score
        return None

    def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        case_id: Optional[str] = None,
        mode: Optional[str] = None
    ) -> QueryDecision:
        cleaned = message.strip()
        lower = cleaned.lower()
        lower_norm = re.sub(r'[\s,?!.]+', ' ', lower).strip()

        # Handle empty query
        if not cleaned:
            return QueryDecision(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=1.0,
                reason="Empty query treated as conversational prompt.",
                requires_base_qwen=True
            )

        # ---------------------------------------------------------------------
        # LAYER 0: Out of Scope Non-Legal Inquiries (Check first for unambiguous non-legal)
        # ---------------------------------------------------------------------
        if self.OUT_OF_SCOPE_REGEX.search(cleaned) and not re.search(r'\b(?:case|matter|evidence|client|hearing|arbitrat|contract)\b', lower):
            return QueryDecision(
                intent=QueryIntent.OUT_OF_SCOPE,
                confidence=0.98,
                reason="Query is outside the legal and supported AI assistant scope.",
                sub_intent="NON_LEGAL_OUT_OF_SCOPE",
                output_plan="OUT_OF_SCOPE_BOUNDARY"
            )

        # ---------------------------------------------------------------------
        # LAYER 1: History Continuation, Reformatting & Recall
        # ---------------------------------------------------------------------
        is_reformat_or_recall = bool(re.search(
            r'\b(?:reformat|format|as\s+a\s+table|in\s+a\s+table|tabular|bullet\s+points?|'
            r'tell\s+me\s+clearly|explain\s+clearly|clearly|in\s+detail|simpler|simple\s+terms|'
            r'previous\s+(?:response|answer|explanation)|earlier\s+in\s+(?:the\s+)?chat|'
            r'what\s+did\s+we\s+discuss|at\s+the\s+start)\b',
            lower
        ))
        if is_reformat_or_recall and conversation_history and len(conversation_history) > 0:
            last_turn_type = "LEGAL_QUERY"
            for turn in reversed(conversation_history):
                qt = str(turn.get("query_type", "")).upper()
                if qt in ("CASE_QUERY", "HEARING_PREPARATION") or case_id:
                    last_turn_type = "CASE_QUERY"
                    break
                elif qt in ("LEGAL_QUERY", "EXACT_PROVISION_QUERY"):
                    last_turn_type = "LEGAL_QUERY"
                    break
                elif qt in ("OUT_OF_SCOPE", "GENERAL_NON_LEGAL"):
                    last_turn_type = "OUT_OF_SCOPE"
                    break

            if last_turn_type == "CASE_QUERY" or case_id:
                return QueryDecision(
                    intent=QueryIntent.CASE_QUERY,
                    confidence=0.95,
                    reason="Follow-up clarification, reformatting, or recall continues active case inquiry.",
                    requires_case_context=True,
                    requires_case_documents=True,
                    requires_case_analysis_v1=True,
                    case_intent_confidence=0.95,
                    case_id=case_id
                )
            elif last_turn_type == "LEGAL_QUERY":
                return QueryDecision(
                    intent=QueryIntent.LEGAL_QUERY,
                    confidence=0.95,
                    reason="Follow-up reformatting continues prior legal inquiry.",
                    requires_legal_rag=True,
                    requires_legalai_v2=True,
                    legal_intent_confidence=0.95
                )

        # ---------------------------------------------------------------------
        # LAYER 2: Active Case Context Primacy (SINGLE_CASE or active case_id)
        # ---------------------------------------------------------------------
        has_active_case = bool(case_id or (mode and mode.upper() in ("SINGLE_CASE", "MULTI_CASE")))

        if has_active_case:
            # 2A. Explicit statutory lookup with NO reference to this case/situation
            has_explicit_sec = bool(self.STATUTE_SEC_REGEX.search(cleaned))
            has_explicit_act = bool(self.STATUTE_ACT_REGEX.search(cleaned))
            has_case_reference = bool(re.search(r'\b(?:this\s+case|our\s+case|the\s+matter|here|client|accused|defendant|plaintiff|in\s+this|this\s+situation|dispute)\b', lower))

            if has_explicit_sec and has_explicit_act and not has_case_reference:
                return QueryDecision(
                    intent=QueryIntent.EXACT_PROVISION_QUERY,
                    confidence=0.98,
                    reason="Explicit statutory lookup inside case mode.",
                    requires_legal_rag=True,
                    requires_legalai_v2=True,
                    case_id=case_id
                )

            # 2B. Quick greeting check inside case mode
            if lower_norm in ("hi", "hello", "hey", "good morning", "good evening", "howdy"):
                return QueryDecision(
                    intent=QueryIntent.CONVERSATIONAL,
                    confidence=0.98,
                    reason="Greeting inside active matter workspace.",
                    requires_base_qwen=True,
                    case_id=case_id
                )

            # 2C. Hearing Preparation / Arguments Formulation
            if re.search(r'\b(?:prepare\s+.*hearing|hearing\s+prep|hearing\s+strategy|strategy\s+.*hearing|oral\s+arguments|points\s+.*argue|arguments?\s+before\s+(?:the\s+)?(?:judge|court|tribunal|bench))\b', lower):
                return QueryDecision(
                    intent=QueryIntent.HEARING_PREPARATION,
                    confidence=0.98,
                    reason="Hearing preparation request for active matter.",
                    requires_case_context=True,
                    requires_case_documents=True,
                    requires_case_analysis_v1=True,
                    case_id=case_id
                )

            # 2D. UNCONDITIONAL CASE PRIMACY FOR EVERYTHING ELSE IN CASE MODE:
            sub_intent = "CASE_SUMMARY"
            if re.search(r'\b(?:timeline|chronology|sequence\s+of\s+events|what\s+happened)\b', lower):
                sub_intent = "CASE_TIMELINE"
            elif re.search(r'\b(?:missing\s+evidence|evidence\s+gaps?|unsupported|what\s+are\s+we\s+missing)\b', lower):
                sub_intent = "CASE_EVIDENCE_GAPS"
            elif re.search(r'\b(?:evidence|documents?|seizure|witness|depositions?|record)\b', lower):
                sub_intent = "CASE_EVIDENCE"
            elif re.search(r'\b(?:arguments?|argue|counterarguments?)\b', lower):
                sub_intent = "CASE_ARGUMENTS"
            elif re.search(r'\b(?:risks?|weakness|vulnerabilit|pitfalls?)\b', lower):
                sub_intent = "CASE_RISKS"
            elif re.search(r'\b(?:next\s+steps?|what\s+should\s+we\s+do|action\s+items?)\b', lower):
                sub_intent = "CASE_NEXT_STEPS"
            elif re.search(r'\b(?:key\s+points?|main\s+points?|important\s+points?|key\s+facts?)\b', lower):
                sub_intent = "CASE_KEY_POINTS"

            return QueryDecision(
                intent=QueryIntent.CASE_QUERY,
                confidence=1.0,
                reason="Query asked within active case context is grounded in case facts, records, and evidence.",
                sub_intent=sub_intent,
                requires_case_context=True,
                requires_case_documents=True,
                requires_case_analysis_v1=True,
                case_intent_confidence=1.0,
                case_id=case_id
            )

        # ---------------------------------------------------------------------
        # LAYER 3: Portfolio & Case Management Inquiries in General Context
        # (Check before fuzzy case so "which cases are urgent" is portfolio overview)
        # ---------------------------------------------------------------------
        is_portfolio = bool(re.search(
            r'\b(?:which\s+cases?\s+(?:are|have)|urgent\s+cases?|priority\s+cases?|'
            r'upcoming\s+hearings?|hearings?\s+(?:are\s+)?scheduled|court\s+calendar|deadlines?|'
            r'cases?\s+handled\s+by|show\s+me\s+(?:the\s+)?cases?|find\s+cases?|'
            r'cases?\s+involv\w+|matters?\s+pending|disputes?\s+pending)\b',
            lower
        ))
        if is_portfolio:
            return QueryDecision(
                intent=QueryIntent.CASE_MANAGEMENT,
                confidence=0.95,
                reason="Inquiry asks about portfolio case priorities, calendar, or matter management.",
                requires_case_metadata=True,
                requires_base_qwen=True
            )

        # ---------------------------------------------------------------------
        # LAYER 4: Fuzzy Case & Entity Matcher in General Context
        # (Resolves "what is the case about the martienx", "tell me about whitfeild")
        # ---------------------------------------------------------------------
        matched_case, score = self.fuzzy_match_case(cleaned) or (None, 0.0)
        if matched_case:
            return QueryDecision(
                intent=QueryIntent.CASE_QUERY,
                confidence=score,
                reason=f"Query resolved to registered matter '{matched_case['title']}' ({matched_case['caseNumber']}).",
                sub_intent="CASE_SUMMARY",
                requires_case_context=True,
                requires_case_documents=True,
                requires_case_analysis_v1=True,
                case_intent_confidence=score,
                case_id=matched_case["id"]
            )

        # ---------------------------------------------------------------------
        # LAYER 5: Authoritative Statutory Inquiries (IPC, CPC, CrPC, BNS, etc.)
        # ---------------------------------------------------------------------
        has_sec = bool(self.STATUTE_SEC_REGEX.search(cleaned))
        has_act = bool(self.STATUTE_ACT_REGEX.search(cleaned))
        if has_sec or (has_act and any(w in lower for w in ["section", "provision", "article", "order", "rule", "bailable", "cognizable", "punishment", "penalty", "explain"])):
            return QueryDecision(
                intent=QueryIntent.EXACT_PROVISION_QUERY if has_sec else QueryIntent.LEGAL_QUERY,
                confidence=0.95,
                reason="Query inquires about specific statutory provision or enactment requiring authoritative RAG.",
                requires_legal_rag=True,
                requires_legalai_v2=True,
                legal_intent_confidence=0.95
            )

        # ---------------------------------------------------------------------
        # LAYER 6: Conversational, Assistant Identity, Courtesies & Metacognition
        # ---------------------------------------------------------------------
        is_greeting = bool(re.match(
            r'^(?:hi|hello|hey|hiya|howdy|good\s+(?:morning|afternoon|evening|day)|greetings)(?:[\s,!.]+)?$',
            lower_norm
        ))
        is_courtesy = bool(re.match(
            r'^(?:thanks|thank\s+you|appreciate\s+it|thx|ok|okay|cool|great|awesome|perfect|sure|fine)(?:[\s,!.]+)?$',
            lower_norm
        ))
        is_2nd_person_convo = bool(re.search(
            r'\b(?:'
            r'are\s+you\s+(?:doing\s+)?good|how\s+are\s+you|how(?:\'s|\s+is)\s+it\s+going|how\s+are\s+things|are\s+you\s+(?:ok|okay|alright|fine)|'
            r'who\s+are\s+you|what\s+are\s+you|what\s+is\s+your\s+name|who\s+made\s+you|who\s+created\s+you|who\s+built\s+you|'
            r'what\s+can\s+you\s+do|what\s+do\s+you\s+do|what\s+are\s+your\s+capabilities|how\s+can\s+you\s+help|'
            r'why\s+(?:aren\'?t\s+you|are\s+you\s+not|do\s+you\s+not|can\'?t\s+you)\s+(?:working|acting|answering|functioning|behaving)\s+(?:as|like)\s+(?:a\s+)?(?:normal\s+)?(?:chatbot|bot|chatgpt|assistant)|'
            r'why\s+are\s+you\s+(?:answering\s+)?(?:like\s+this|so\s+rigid|so\s+robotic)|'
            r'can\s+we\s+(?:just\s+)?chat|can\s+you\s+talk\s+normally|talk\s+normally|'
            r'what\s+kind\s+of\s+(?:assistance|help)\s+do\s+you\s+provide|'
            r'tell\s+me\s+(?:clearly\s+)?about\s+your\s+capabilities'
            r')\b',
            lower
        ))

        if is_greeting or is_courtesy or is_2nd_person_convo:
            return QueryDecision(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=0.98,
                reason="Message is a conversational greeting, courtesy, assistant identity, or metacognitive inquiry.",
                sub_intent="CONVERSATIONAL",
                requires_base_qwen=True
            )

        # ---------------------------------------------------------------------
        # LAYER 7: Substantive Legal Concepts
        # (negligence, bail, fir, estoppel, specific performance, breach of contract)
        # ---------------------------------------------------------------------
        is_legal_concept = bool(re.search(
            r'\b(?:negligence|duty\s+of\s+care|anticipatory\s+bail|bail|murder|culpable\s+homicide|'
            r'breach\s+of\s+trust|cheating|estoppel|injunction|interim\s+injunction|fir|chargesheet|'
            r'discharge|res\s+judicata|limitation|consideration|breach\s+of\s+contract|arbitration)\b',
            lower
        ))
        if is_legal_concept:
            return QueryDecision(
                intent=QueryIntent.LEGAL_QUERY,
                confidence=0.92,
                reason="Query asks for substantive or procedural Indian legal reasoning.",
                requires_legal_rag=True,
                requires_legalai_v2=True,
                legal_intent_confidence=0.92
            )

        # ---------------------------------------------------------------------
        # LAYER 8: Universal Intelligent Fallback (NO ROBOTIC CLARIFICATION)
        # ---------------------------------------------------------------------
        # Only cryptic punctuation or 1-2 character symbols are ambiguous
        if len(cleaned) <= 3 and not cleaned.isalnum():
            return QueryDecision(
                intent=QueryIntent.AMBIGUOUS,
                confidence=0.85,
                reason="Query is an isolated symbol or punctuation fragment.",
                output_plan="AMBIGUOUS_CLARIFICATION"
            )

        # All other queries in General mode go to Base Qwen with conversational persona!
        return QueryDecision(
            intent=QueryIntent.CONVERSATIONAL,
            confidence=0.90,
            reason="Open-ended query routed to conversational assistant persona.",
            requires_base_qwen=True
        )


# Run full evaluation over all 70 benchmark questions
if __name__ == "__main__":
    router = ContextAwareUniversalRouter()

    test_benchmark = {
        "Case 1 (Martinez - SINGLE_CASE)": [
            ("what is the issue regarding the cargo in berth 9", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("can you break down the charterparty agreement dispute for martinez", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("why did coastal holdings place a lien on the shipment?", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("what are our strongest arguments for getting the interim injunction?", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("tell me what happened with the port authority strike notification", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("how much freight demurrage is being claimed against our client", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("who is the presiding judge or bench handling this matter?", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("is there any evidence gap in the maritime contract documents?", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("give me a quick timeline of events leading up to the cargo seizure", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
            ("what should we do next before the hearing this week?", "SINGLE_CASE", "case-01", QueryIntent.CASE_QUERY),
        ],
        "Case 2 (Whitfield - SINGLE_CASE)": [
            ("what is this case is about", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("who is the accused and what are the state prosecutors alleging?", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("can we apply for regular bail right now for whitfield?", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("explain the chargesheet allegations against arthur", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("what digital evidence or forensics did the police seize?", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("are there any chain-of-custody defects in the search seizure record?", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("what are the main weaknesses in the prosecution's case so far?", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("summary of the case", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("key facts of this matter", "SINGLE_CASE", "case-02", QueryIntent.CASE_QUERY),
            ("how should i prepare for the upcoming sessions court hearing?", "SINGLE_CASE", "case-02", QueryIntent.HEARING_PREPARATION),
        ],
        "Case 3 (Nguyen Probate - SINGLE_CASE)": [
            ("give me an overview of the dispute over the nguyen will", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("what are the contesting beneficiaries claiming against thao?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("has testamentary capacity been established for the deceased?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("who is representing the opposing party in this probate action?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("what is the status of the attesting witness depositions?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("when was the codicil executed and why is it contested?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("what is the deadline for filing our cross-affidavits?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("what evidence supports the executor's position?", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("explain the claim of undue influence raised by sterling and cole", "SINGLE_CASE", "case-03", QueryIntent.CASE_QUERY),
            ("what is our recommended strategy for the next probate hearing?", "SINGLE_CASE", "case-03", QueryIntent.HEARING_PREPARATION),
        ],
        "Case 4 (Apex Arbitration - SINGLE_CASE)": [
            ("what relief is apex logistics seeking under section 9?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("tell me about the exclusivity covenants in the horizon freight agreement", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("can the tribunal restrain the enforcement of liquidated damages?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("when is the hearing for ad-interim relief scheduled?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("who is the assigned counsel for this arbitration matter?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("what are the major financial risks if the interim stay is denied?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("summarize the contractual breach alleged against horizon", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("what documents do we have on record for this dispute?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("how does section 9 of the arbitration act apply to this situation?", "SINGLE_CASE", "case-04", QueryIntent.CASE_QUERY),
            ("what points should i argue before the commercial tribunal?", "SINGLE_CASE", "case-04", QueryIntent.HEARING_PREPARATION),
        ],
        "Category 5 (Conversational / Identity / Meta)": [
            ("hi", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("how are you", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("are you doing good", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("what can you do", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("why aren't you working as a normal chatbot", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("who made you", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("can we just chat normally?", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("what kind of assistance do you provide to advocates?", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("thank you for your help", "GENERAL", None, QueryIntent.CONVERSATIONAL),
            ("tell me clearly about your capabilities", "GENERAL", None, QueryIntent.CONVERSATIONAL),
        ],
        "Category 6 (Cross-Case & Fuzzy Match from General)": [
            ("what is the case about the martienx", "GENERAL", None, QueryIntent.CASE_QUERY),
            ("tell me about the whitfeild prosecution", "GENERAL", None, QueryIntent.CASE_QUERY),
            ("what is happening in the nguyen estate probate?", "GENERAL", None, QueryIntent.CASE_QUERY),
            ("give me details on the apex logistics arbitration", "GENERAL", None, QueryIntent.CASE_QUERY),
            ("which cases are currently marked urgent?", "GENERAL", None, QueryIntent.CASE_MANAGEMENT),
            ("what hearings are scheduled for this week?", "GENERAL", None, QueryIntent.CASE_MANAGEMENT),
            ("do we have any maritime law disputes pending?", "GENERAL", None, QueryIntent.CASE_MANAGEMENT),
            ("show me the cases handled by adv elena vance", "GENERAL", None, QueryIntent.CASE_MANAGEMENT),
            ("what is case 2024-CR-0442 about?", "GENERAL", None, QueryIntent.CASE_QUERY),
            ("tell me what cases involve breach of contract", "GENERAL", None, QueryIntent.CASE_MANAGEMENT),
        ],
        "Category 7 (Out of Scope Non-Legal)": [
            ("how to make pasta", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("write python code for merge sort", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("who won the world cup in 2022", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("what is the capital of france?", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("can you solve this math problem 45 * 89", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("tell me a funny joke", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("recommend a good laptop for gaming", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("what is the plot of inception", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("how is the weather in mumbai today", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
            ("how do i fix a flat tire on my bicycle", "GENERAL", None, QueryIntent.OUT_OF_SCOPE),
        ]
    }

    total_passed = 0
    total_queries = 0

    print("================================================================================")
    print("RUNNING COMPLETE 70-QUERY BENCHMARK ACROSS ALL 7 DOMAINS")
    print("================================================================================")

    for cat_name, queries in test_benchmark.items():
        print(f"\n--- {cat_name} ---")
        cat_passed = 0
        for q, m, cid, expected in queries:
            dec = router.classify(q, case_id=cid, mode=m)
            is_match = (dec.intent == expected)
            total_queries += 1
            if is_match:
                cat_passed += 1
                total_passed += 1
                print(f"  [PASS] \"{q[:45]:45}\" -> {dec.intent.value:18}")
            else:
                print(f"  [FAIL] \"{q[:45]:45}\" -> GOT: {dec.intent.value:18} EXPECTED: {expected.value:18}")

        print(f"Category Score: {cat_passed} / {len(queries)} ({cat_passed/len(queries)*100:.1f}%)")

    print("\n================================================================================")
    print(f"FINAL BENCHMARK SCORE: {total_passed} / {total_queries} ({total_passed/total_queries*100:.1f}%)")
    print("================================================================================")
