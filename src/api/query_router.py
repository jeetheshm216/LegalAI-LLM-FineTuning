"""
src/api/query_router.py

Universal Context-First Model-Driven Query Understanding & Routing Engine for LegalAI.

Decouples Intent from Context, Data Source, and Model / Adapter:
- GENERAL: Coding, Technical AI, Identity, Explanations (Base Qwen, LoRA Disabled)
- CASE_DRAFTING: Civil Petitions, Plaints, Legal Notices, Contracts (Base Qwen Draftsman)
- LEGAL: Indian Statutory Law (BNS, BNSS, BSA, IPC, CrPC, CPC) (LegalAI LoRA + Legal RAG)
- CASE: Case Analysis, Pleadings, Evidence, Document RAG (Case Analysis LoRA + Case RAG + Memory)

Safety & Anti-Hallucination Invariant:
- Strict Confidence Scoring (Threshold >= 80%):
  If a query does not match a domain with high confidence, Base Qwen directly
  understands the concept and responds parametrically rather than forcing incorrect RAG.
- Blacklist generic words from fuzzy matching so queries with common words (like 'stated', 'court',
  'dispute', 'property') never collide with case titles like 'In re Nguyen Estate'.
"""

import re
import os
import difflib
import sqlite3
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple

try:
    from src.api.query_understanding.goals import SubIntent, UserGoal, OutputPlan
except ImportError:
    class SubIntent(str, Enum):
        CASE_SUMMARY = "CASE_SUMMARY"
        CASE_KEY_POINTS = "CASE_KEY_POINTS"
        CASE_ISSUES = "CASE_ISSUES"
        CASE_FACTS = "CASE_FACTS"
        CASE_EVIDENCE = "CASE_EVIDENCE"
        CASE_EVIDENCE_GAPS = "CASE_EVIDENCE_GAPS"
        CASE_ARGUMENTS = "CASE_ARGUMENTS"
        CASE_COUNTERARGUMENTS = "CASE_COUNTERARGUMENTS"
        CASE_RISKS = "CASE_RISKS"
        CASE_TIMELINE = "CASE_TIMELINE"
        CASE_NEXT_STEPS = "CASE_NEXT_STEPS"
        CASE_DOCUMENT_ANALYSIS = "CASE_DOCUMENT_ANALYSIS"
        CASE_DRAFTING = "CASE_DRAFTING"
        CROSS_MATTER_COMPARISON = "CROSS_MATTER_COMPARISON"
        HEARING_PREPARATION = "HEARING_PREPARATION"
        EXACT_STATUTORY_PROVISION = "EXACT_STATUTORY_PROVISION"
        LEGAL_CONCEPT = "LEGAL_CONCEPT"
        LEGAL_PROCEDURE = "LEGAL_PROCEDURE"
        STATUTORY_PUNISHMENT = "STATUTORY_PUNISHMENT"
        SYSTEM_SPECIFICATION = "SYSTEM_SPECIFICATION"
        TECHNICAL_CONCEPT = "TECHNICAL_CONCEPT"
        PORTFOLIO_WORKLOAD = "PORTFOLIO_WORKLOAD"
        PORTFOLIO_HEARINGS = "PORTFOLIO_HEARINGS"
        PORTFOLIO_DEADLINES = "PORTFOLIO_DEADLINES"
        CASE_PRIORITY = "CASE_PRIORITY"
        GREETING = "GREETING"
        GRATITUDE = "GRATITUDE"
        ASSISTANT_IDENTITY = "ASSISTANT_IDENTITY"
        CONTEXT_FOLLOW_UP = "CONTEXT_FOLLOW_UP"
        NON_LEGAL_OUT_OF_SCOPE = "NON_LEGAL_OUT_OF_SCOPE"
        CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"

    class UserGoal(str, Enum):
        UNDERSTAND_CASE = "UNDERSTAND_CASE"
        PRIORITIZE_CASE_ISSUES = "PRIORITIZE_CASE_ISSUES"
        PRIORITIZE_CASE = "PRIORITIZE_CASE"
        ANALYZE_EVIDENCE = "ANALYZE_EVIDENCE"
        IDENTIFY_EVIDENCE_GAPS = "IDENTIFY_EVIDENCE_GAPS"
        IDENTIFY_CASE_RISKS = "IDENTIFY_CASE_RISKS"
        ANALYZE_ARGUMENTS = "ANALYZE_ARGUMENTS"
        ANALYZE_COUNTERARGUMENTS = "ANALYZE_COUNTERARGUMENTS"
        HEARING_PREPARATION = "HEARING_PREPARATION"
        CHRONOLOGY_MAPPING = "CHRONOLOGY_MAPPING"
        RECOMMEND_NEXT_STEPS = "RECOMMEND_NEXT_STEPS"
        CASE_DRAFTING = "CASE_DRAFTING"
        RESEARCH_PROVISION = "RESEARCH_PROVISION"
        EXPLAIN_LEGAL_CONCEPT = "EXPLAIN_LEGAL_CONCEPT"
        PORTFOLIO_OVERVIEW = "PORTFOLIO_OVERVIEW"
        SYSTEM_ARCHITECTURE = "SYSTEM_ARCHITECTURE"
        TECHNICAL_EXPLANATION = "TECHNICAL_EXPLANATION"
        CONVERSATIONAL_EXCHANGE = "CONVERSATIONAL_EXCHANGE"
        IDENTIFY_ASSISTANT = "IDENTIFY_ASSISTANT"
        CLARIFY_QUERY = "CLARIFY_QUERY"
        REJECT_OUT_OF_SCOPE = "REJECT_OUT_OF_SCOPE"

    class OutputPlan(str, Enum):
        KEY_POINTS = "KEY_POINTS"
        FOCUS_AREAS = "FOCUS_AREAS"
        CASE_SUMMARY = "CASE_SUMMARY"
        ESTABLISHED_FACTS = "ESTABLISHED_FACTS"
        KEY_ISSUES = "KEY_ISSUES"
        AVAILABLE_EVIDENCE = "AVAILABLE_EVIDENCE"
        EVIDENCE_GAPS = "EVIDENCE_GAPS"
        ARGUMENT_ANALYSIS = "ARGUMENT_ANALYSIS"
        POTENTIAL_ARGUMENTS = "POTENTIAL_ARGUMENTS"
        OPPOSING_ARGUMENTS = "OPPOSING_ARGUMENTS"
        CASE_RISKS = "CASE_RISKS"
        CHRONOLOGICAL_TIMELINE = "CHRONOLOGICAL_TIMELINE"
        ACTIONABLE_NEXT_STEPS = "ACTIONABLE_NEXT_STEPS"
        HEARING_BRIEF = "HEARING_BRIEF"
        CASE_PRIORITY_BRIEF = "CASE_PRIORITY_BRIEF"
        DRAFTING_WORKFLOW = "DRAFTING_WORKFLOW"
        DRAFTING_CLARIFICATION = "DRAFTING_CLARIFICATION"
        STATUTORY_ANALYSIS = "STATUTORY_ANALYSIS"
        CONCEPT_EXPLANATION = "CONCEPT_EXPLANATION"
        PORTFOLIO_TABLE = "PORTFOLIO_TABLE"
        SYSTEM_SPEC_SHEET = "SYSTEM_SPEC_SHEET"
        CONVERSATIONAL_RESPONSE = "CONVERSATIONAL_RESPONSE"
        ASSISTANT_IDENTITY = "ASSISTANT_IDENTITY"
        AMBIGUOUS_CLARIFICATION = "AMBIGUOUS_CLARIFICATION"
        OUT_OF_SCOPE_BOUNDARY = "OUT_OF_SCOPE_BOUNDARY"


class QueryIntent(str, Enum):
    CONVERSATIONAL = "CONVERSATIONAL"
    GENERAL = "GENERAL"
    CASE_DRAFTING = "CASE_DRAFTING"
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
    GENERAL_NON_LEGAL = "GENERAL"


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
    requires_base_qwen: bool = True
    requires_legalai_v2: bool = False
    requires_case_analysis_v1: bool = False
    legal_intent_confidence: float = 0.0
    case_intent_confidence: float = 0.0
    target_act: Optional[str] = None
    target_provision: Optional[str] = None
    case_id: Optional[str] = None


RoutingResult = QueryDecision


class UniversalQueryRouter:
    """
    Universal Model-Driven Understanding & Dynamic Router.
    - Zero robotic clarification templates.
    - Robust pronoun & reference resolution across multi-turn context.
    - Prevents false matter collisions using strict blacklist and confidence scoring.
    - Routes cleanly into:
        1) CONVERSATIONAL -> Base Qwen greeting (zero RAG, zero document hallucination)
        2) CASE_DRAFTING -> Full legal pleading / civil petition generation
        3) GENERAL -> Base Qwen (coding, reasoning, parametric understanding)
        4) TECHNICAL_AI -> Base Qwen AI explanation
        5) LEGAL -> LegalAI LoRA + Legal RAG (BNS, BNSS, BSA, IPC, CrPC, CPC)
        6) CASE -> Case Analysis LoRA + Case RAG & Case Memory
    """

    GENERIC_WORDS_BLACKLIST = {
        "stated", "state", "court", "dispute", "order", "judge", "matter",
        "date", "notice", "petition", "property", "case", "action", "clause",
        "person", "parties", "client", "summary", "document", "records",
        "claim", "rights", "relief", "reliefs", "facts", "evidence", "legal",
        "counsel", "advocate", "bench", "high", "division", "district", "suit",
        "plaint", "written", "statement", "general", "civil", "criminal", "estate"
    }

    DEFAULT_KNOWN_CASES = [
        {
            "id": "case-01",
            "caseNumber": "2024-CV-1187",
            "title": "Martinez v. Coastal Holdings Ltd.",
            "client": "Julian Martinez",
            "opposing": "Coastal Holdings Ltd.",
            "keywords": ["martinez", "coastal", "charterparty", "berth 9", "demurrage", "cargo lien", "maritime"]
        },
        {
            "id": "case-02",
            "caseNumber": "2024-CR-0442",
            "title": "State v. Whitfield",
            "client": "Arthur Whitfield",
            "opposing": "State Department of Public Prosecutions",
            "keywords": ["whitfield", "chargesheet", "bail", "regular bail", "digital evidence", "sessions judge"]
        },
        {
            "id": "case-03",
            "caseNumber": "2024-CV-0998",
            "title": "In re Nguyen Estate Testamentary Probate",
            "client": "Thao Nguyen",
            "opposing": "Sterling & Cole",
            "keywords": ["nguyen", "probate", "testamentary", "codicil", "will dispute"]
        },
        {
            "id": "case-04",
            "caseNumber": "2024-CC-0120",
            "title": "Apex Logistics Corp. v. Horizon Freight Services",
            "client": "Apex Logistics Corp.",
            "opposing": "Horizon Freight Services",
            "keywords": ["apex", "horizon", "liquidated damages", "exclusivity covenant", "freight"]
        }
    ]

    def __init__(self, db_path: str = "data/legalai_app.db"):
        self.db_path = db_path
        self.known_cases = self._load_known_cases()

    def _load_known_cases(self) -> List[Dict[str, Any]]:
        cases = list(self.DEFAULT_KNOWN_CASES)
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("SELECT id, caseNumber, title, client, opposingParty FROM cases")
                rows = c.fetchall()
                conn.close()
                for r in rows:
                    cid, cnum, ctitle, cclient, copposing = r
                    if not any(k["id"] == cid for k in cases):
                        kw = []
                        if ctitle:
                            kw.extend([w.lower() for w in re.findall(r'[a-zA-Z0-9]+', ctitle) if len(w) >= 4 and w.lower() not in self.GENERIC_WORDS_BLACKLIST])
                        if cclient:
                            kw.extend([w.lower() for w in re.findall(r'[a-zA-Z0-9]+', cclient) if len(w) >= 4 and w.lower() not in self.GENERIC_WORDS_BLACKLIST])
                        cases.append({
                            "id": cid,
                            "caseNumber": cnum or "",
                            "title": ctitle or "",
                            "client": cclient or "",
                            "opposing": copposing or "",
                            "keywords": list(set(kw))
                        })
            except Exception:
                pass
        return cases

    def fuzzy_match_case(self, query: str) -> Optional[Tuple[Dict[str, Any], float]]:
        lower_q = query.lower()
        words = [w for w in re.findall(r'[a-zA-Z0-9_\-]+', lower_q) if w not in self.GENERIC_WORDS_BLACKLIST]

        # 1. Exact caseNumber or ID match (100% confidence)
        for c in self.known_cases:
            cid = c.get("id", "").lower()
            cnum = c.get("caseNumber", "").lower()
            if (cid and cid in lower_q) or (cnum and cnum in lower_q):
                return c, 1.0

        # 2. Distinctive Proper Nouns only (score >= 0.88, distinctive words >= 5 chars)
        best_match = None
        best_score = 0.0

        for c in self.known_cases:
            distinctive_keywords = [
                k.lower() for k in c.get("keywords", [])
                if k.lower() not in self.GENERIC_WORDS_BLACKLIST and len(k) >= 5
            ]
            for kw in distinctive_keywords:
                # Require full word boundary match if exact keyword in query
                if re.search(r'\b' + re.escape(kw) + r'\b', lower_q):
                    return c, 0.95
                for w in words:
                    if len(w) >= 5:
                        ratio = difflib.SequenceMatcher(None, w, kw).ratio()
                        if ratio >= 0.88 and ratio > best_score:
                            best_score = ratio
                            best_match = c

            for client_word in (c.get("client") or "").lower().split():
                if len(client_word) >= 5 and client_word not in self.GENERIC_WORDS_BLACKLIST:
                    for w in words:
                        ratio = difflib.SequenceMatcher(None, w, client_word).ratio()
                        if ratio >= 0.88 and ratio > best_score:
                            best_score = ratio
                            best_match = c

        if best_match and best_score >= 0.88:
            return best_match, best_score
        return None

    TYPO_CORRECTIONS = [
        # Conversational / Greetings / Pronouns
        (r'\bhwo\b', 'how'),
        (r'\bwat\b', 'what'),
        (r'\bwht\b', 'what'),
        (r'\bwats\b', 'what is'),
        (r'\bteh\b', 'the'),
        (r'\byuo\b', 'you'),
        (r'\bu\b', 'you'),
        (r'\bur\b', 'your'),
        (r'\br\b', 'are'),
        (r'\bthx\b', 'thanks'),
        (r'\bplz\b', 'please'),
        (r'\bpls\b', 'please'),
        # Legal & Court Drafting
        (r'\bdrfat\b', 'draft'),
        (r'\bdarf\b', 'draft'),
        (r'\bdaft\b', 'draft'),
        (r'\bdrft\b', 'draft'),
        (r'\bpetishun\b', 'petition'),
        (r'\bpetitin\b', 'petition'),
        (r'\bpetiton\b', 'petition'),
        (r'\bptition\b', 'petition'),
        (r'\bsectoin\b', 'section'),
        (r'\bseciton\b', 'section'),
        (r'\bsction\b', 'section'),
        (r'\bproperti\b', 'property'),
        (r'\bpropety\b', 'property'),
        (r'\bproprty\b', 'property'),
        (r'\bdisput\b', 'dispute'),
        (r'\bdisptue\b', 'dispute'),
        (r'\bevidenc\b', 'evidence'),
        (r'\bevidense\b', 'evidence'),
        (r'\bwitnes\b', 'witness'),
        (r'\bwitniss\b', 'witness'),
        (r'\bstatut\b', 'statute'),
        (r'\bplaintif\b', 'plaintiff'),
        (r'\bdefendent\b', 'defendant'),
        (r'\bagrument\b', 'argument'),
        (r'\bargmnt\b', 'argument'),
        (r'\bjudgemnt\b', 'judgment'),
        (r'\bjudgmet\b', 'judgment'),
        (r'\bjurisdiciton\b', 'jurisdiction'),
        (r'\bjurisdcition\b', 'jurisdiction'),
        (r'\bchargeshit\b', 'chargesheet'),
        (r'\bchrgsheet\b', 'chargesheet'),
        (r'\binjunciton\b', 'injunction'),
        (r'\binjuntion\b', 'injunction'),
        (r'\bhearng\b', 'hearing'),
        (r'\bcontridiction\b', 'contradiction'),
        (r'\bstatemnt\b', 'statement'),
        (r'\bdocumnt\b', 'document'),
        (r'\bdocumnts\b', 'documents'),
        (r'\badvocat\b', 'advocate'),
        (r'\blawer\b', 'lawyer'),
        (r'\bafidavit\b', 'affidavit'),
        (r'\baffidavt\b', 'affidavit')
    ]

    def normalize_query_typos(self, text: str) -> str:
        if not text:
            return ""
        res = text
        for pat, repl in self.TYPO_CORRECTIONS:
            res = re.sub(pat, repl, res, flags=re.IGNORECASE)
        return res

    def classify(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        case_id: Optional[str] = None,
        mode: Optional[str] = None
    ) -> QueryDecision:
        cleaned = query.strip()
        normalized_query = self.normalize_query_typos(cleaned)
        lower = normalized_query.lower()

        # Prior context inspection
        last_turn_text = ""
        earlier_turns_text = ""
        if conversation_history:
            for turn in reversed(conversation_history):
                content = turn.get("content", "")
                if turn.get("role") == "user" and not last_turn_text:
                    last_turn_text = content.lower()
                earlier_turns_text += " " + content.lower()

        # -------------------------------------------------------------
        # STEP 1: Cross-Matter Entity Resolution Check (Strict Threshold)
        # -------------------------------------------------------------
        matched_case_tuple = self.fuzzy_match_case(normalized_query)
        effective_case_id = case_id
        if matched_case_tuple:
            matched_case, score = matched_case_tuple
            effective_case_id = matched_case["id"]

        # -------------------------------------------------------------
        # STEP 2: Pure Greetings, Courtesies, Identity & Pleasantries
        # MUST BE EVALUATED FIRST to prevent conversational greetings from ever
        # being treated as Case Document RAG or Hallucinating on PDFs!
        # -------------------------------------------------------------
        is_greeting = bool(re.search(
            r'^\s*(?:hi|hello|hey|hiya|howdy|greetings|good\s+(?:morning|afternoon|evening|day))\b',
            lower
        )) or lower in ("hi", "hello", "hey", "hola", "namaste", "greetings")

        is_pleasantry = bool(re.search(
            r'\b(?:how\s+(?:are\s+you|are\s+u|is\s+it\s+going|do\s+you\s+do)|what\s+are\s+you\s+doing|whats?\s+up|what\s+is\s+up)\b',
            lower
        )) or lower in ("how are you", "how are you doing", "what are you doing", "how are u")

        is_interjection = bool(re.search(
            r'^\s*(?:wow|nice|awesome|super|great|cool|wonderful|amazing|sure|fine|yep|yes|nope|no|haha|hehe)\b',
            lower
        )) or lower in ("wow", "cool", "great", "nice", "awesome", "amazing")

        is_courtesy = bool(re.search(
            r'^\s*(?:thank\s+you|thanks|thx|much\s+appreciated|great|ok|okay|cool|got\s+it|understood)\b',
            lower
        )) or lower in ("thank you", "thanks", "thx", "ok", "okay", "understood")

        is_identity = bool(re.search(
            r'\b(?:who\s+are\s+you|what\s+are\s+you(?:\s+called)?|what\s+is\s+your\s+name|tell\s+me\s+your\s+name|what\s+can\s+you\s+do|what\s+do\s+you\s+do|are\s+you\s+an?\s+ai|your\s+name)\b',
            lower
        )) or lower in ("who are you", "what is your name", "what are you", "tell me your name", "your name")

        if is_identity:
            return QueryDecision(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=1.0,
                reason="Assistant capability and architecture inquiry.",
                sub_intent=SubIntent.ASSISTANT_IDENTITY.value,
                user_goal=UserGoal.IDENTIFY_ASSISTANT.value,
                output_plan=OutputPlan.ASSISTANT_IDENTITY.value,
                normalized_query=normalized_query,
                requires_base_qwen=True,
                requires_legal_rag=False,
                requires_case_documents=False
            )

        if is_greeting or is_courtesy or is_pleasantry or is_interjection:
            return QueryDecision(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=1.0,
                reason="Message is an ordinary conversational greeting, courtesy, pleasantry, or interjection.",
                sub_intent=SubIntent.GREETING.value if is_greeting else (SubIntent.GRATITUDE.value if is_courtesy else "PLEASANTRY"),
                user_goal=UserGoal.CONVERSATIONAL_EXCHANGE.value,
                output_plan=OutputPlan.CONVERSATIONAL_RESPONSE.value,
                normalized_query=normalized_query,
                requires_base_qwen=True,
                requires_legal_rag=False,
                requires_case_documents=False,
                case_id=effective_case_id
            )

        # -------------------------------------------------------------
        # STEP 3: Legal Drafting Inquiries (Civil Petitions, Plaints, Notices, Affidavits)
        # Dedicated High-Priority Drafting Pipeline!
        # -------------------------------------------------------------
        is_drafting_prompt = bool(re.search(
            r'\b(?:type\s+of\s+document|draft\s+(?:a\s+)?(?:civil\s+petition|petition|plaint|legal\s+notice|affidavit|written\s+statement|injunction|suit)|'
            r'prepare\s+(?:a\s+)?(?:civil\s+petition|petition|plaint|legal\s+notice|affidavit)|'
            r'draft\s+a\s+contract|draft\s+an\s+agreement|drafting\s+instructions)\b',
            lower
        )) or ("type of document" in lower and "petition" in lower) or ("parties involved" in lower and "petitioner" in lower)

        if is_drafting_prompt:
            return QueryDecision(
                intent=QueryIntent.CASE_DRAFTING,
                confidence=0.98,
                reason="Structured legal drafting prompt requiring authoritative drafting synthesis.",
                sub_intent="CASE_DRAFTING",
                user_goal="CASE_DRAFTING",
                output_plan="DRAFTING_WORKFLOW",
                normalized_query=cleaned,
                requires_base_qwen=True,
                requires_case_context=False,
                requires_case_documents=False,
                requires_legal_rag=False
            )

        # -------------------------------------------------------------
        # STEP 4: General Coding & Technical Computing Inquiries
        # Routed to Base Qwen with LoRA disabled. Zero RAG.
        # -------------------------------------------------------------
        is_coding_request = bool(re.search(
            r'\b(?:write\s+(?:a\s+)?(?:python|javascript|java|c\+\+|cpp|rust|go|sql|code|script|program)|'
            r'def\s+[a-zA-Z_]|print\s*\(|function\s*\(|odd\s+or\s+even|even\s+or\s+odd|'
            r'bubble\s+sort|merge\s+sort|quicksort|binary\s+search|algorithm|fibonacci|python\s+code)\b',
            lower
        ))
        is_code_follow_up = bool(re.search(
            r'\b(?:explain\s+(?:the\s+)?code|how\s+does\s+(?:this\s+)?code\s+work|walk\s+through\s+the\s+code|explain\s+(?:the\s+)?program)\b',
            lower
        ))
        coding_in_history = bool(re.search(r'\b(?:python|code|def\s+|algorithm|odd\s+or\s+even)\b', earlier_turns_text))

        if is_coding_request or (is_code_follow_up and (coding_in_history or "code" in last_turn_text)):
            return QueryDecision(
                intent=QueryIntent.GENERAL,
                confidence=0.98,
                reason="General programming or code explanation task routed to Base Qwen with LoRA disabled.",
                sub_intent="PROGRAMMING_CODE",
                user_goal="CODE_GENERATION_OR_EXPLANATION",
                output_plan="STRUCTURED_CODE_RESPONSE",
                normalized_query=cleaned,
                requires_base_qwen=True,
                requires_legal_rag=False,
                requires_case_documents=False
            )

        # -------------------------------------------------------------
        # STEP 5: General AI, Models, Qwen, Transformers Inquiries
        # Routed to Base Qwen with LoRA disabled. Zero RAG.
        # -------------------------------------------------------------
        is_ai_concept = bool(re.search(
            r'\b(?:what\s+is\s+qwen|who\s+is\s+qwen|qwen|alibaba\s+cloud|large\s+language\s+model|llm|transformer\s+model)\b',
            lower
        ))
        is_ai_followup = bool(
            ("qwen" in last_turn_text or "llm" in last_turn_text or "model" in last_turn_text or "qwen" in earlier_turns_text) and
            bool(re.search(r'\b(?:tell\s+me\s+more(?:\s+about\s+it)?|more\s+about\s+it|explain\s+it\s+like\s+i(?:\'m|\s+am)\s+a\s+beginner|simple\s+terms|beginner)\b', lower))
        )
        if is_ai_concept or is_ai_followup:
            return QueryDecision(
                intent=QueryIntent.TECHNICAL_AI,
                confidence=0.95,
                reason="AI technical concept inquiry routed to Base Qwen with LoRA disabled.",
                sub_intent=SubIntent.TECHNICAL_CONCEPT.value,
                user_goal=UserGoal.TECHNICAL_EXPLANATION.value,
                output_plan=OutputPlan.CONCEPT_EXPLANATION.value,
                normalized_query=cleaned,
                requires_base_qwen=True,
                requires_legal_rag=False,
                requires_case_documents=False
            )

        # -------------------------------------------------------------
        # STEP 6: Authoritative Indian Statutory Law (BNS, BNSS, BSA, IPC, CrPC, CPC)
        # Calculates explicit statutory confidence score (Threshold >= 80%).
        # If below threshold, allows Base Qwen to reason parametrically.
        # -------------------------------------------------------------
        has_statute_act = bool(re.search(
            r'\b(?:bns|bnss|bsa|ipc|crpc|cpc|bharatiya\s+nyaya\s+sanhita|bharatiya\s+nagarik|bharatiya\s+sakshya|'
            r'indian\s+penal\s+code|code\s+of\s+criminal\s+procedure|code\s+of\s+civil\s+procedure|evidence\s+act)\b',
            lower
        ))
        has_statute_sec = bool(re.search(
            r'\b(?:section|sec\.?|s\.?|u/s|article|order|rule)\s*([0-9]+[a-z]*)\b|\b(?:bns|bnss|bsa|ipc|crpc|cpc)\s*([0-9]+)\b',
            lower
        ))
        has_statutory_concept = bool(re.search(
            r'\b(?:electronic\s+evidence|admissibility|bailable|cognizable|compoundable|anticipatory\s+bail|'
            r'punishment\s+under|penalty\s+under|murder\s+under|theft\s+under|extortion\s+under|dying\s+declaration)\b',
            lower
        ))

        statute_in_history = bool(re.search(r'\b(?:bns|bnss|bsa|ipc|crpc|cpc|section\s+\d+)\b', earlier_turns_text))
        is_statute_follow_up = statute_in_history and bool(re.search(
            r'\b(?:explain\s+it\s+simply|simple\s+terms|punishment\s+under\s+this\s+section|punishment|penalty|bailable|cognizable)\b',
            lower
        ))

        # Calculate Legal Confidence Percentage
        legal_score = 0.0
        if has_statute_sec and (has_statute_act or "section" in lower):
            legal_score = 0.98  # Exact Section + Act
        elif has_statute_act or has_statute_sec or is_statute_follow_up:
            legal_score = 0.92
        elif has_statutory_concept:
            legal_score = 0.85

        if legal_score >= 0.80:
            sec_match = re.search(r'\b(?:section|sec\.?|s\.?|u/s)\s*([0-9]+[a-z]*)\b', lower)
            if not sec_match and is_statute_follow_up:
                sec_match = re.search(r'\b(?:section|sec\.?|s\.?|u/s)\s*([0-9]+[a-z]*)\b', earlier_turns_text)
            target_provision = sec_match.group(1) if sec_match else None

            act_match = re.search(r'\b(bns|bnss|bsa|ipc|crpc|cpc)\b', lower)
            if not act_match and is_statute_follow_up:
                act_match = re.search(r'\b(bns|bnss|bsa|ipc|crpc|cpc)\b', earlier_turns_text)
            target_act = act_match.group(1).upper() if act_match else None

            return QueryDecision(
                intent=QueryIntent.EXACT_PROVISION_QUERY if target_provision else QueryIntent.LEGAL_QUERY,
                confidence=legal_score,
                reason=f"Authoritative Indian statutory inquiry (Confidence: {int(legal_score * 100)}%) requiring LegalAI LoRA and Statutory RAG.",
                sub_intent=SubIntent.EXACT_STATUTORY_PROVISION.value if target_provision else SubIntent.LEGAL_CONCEPT.value,
                user_goal=UserGoal.RESEARCH_PROVISION.value,
                output_plan=OutputPlan.STATUTORY_ANALYSIS.value,
                normalized_query=cleaned,
                requires_legal_rag=True,
                requires_legalai_v2=True,
                legal_intent_confidence=legal_score,
                target_act=target_act,
                target_provision=target_provision
            )

        # -------------------------------------------------------------
        # STEP 7: Case Analysis & Evidentiary Inquiries
        # ONLY if the query specifically asks about case facts, evidence, pleadings, or documents!
        # Requires Case Match Confidence >= 85%
        # -------------------------------------------------------------
        is_case_keyword = bool(re.search(
            r'\b(?:matter\s+facts|pleadings?|demurrage|charterparty|berth|cargo\s+lien|bail\s+order|chargesheet\s+allegations|'
            r'probate|codicil|testamentary|apex|horizon|whitfield|martinez|nguyen|evidence\s+gaps|'
            r'hearing\s+date|witness\s+statement|affidavit\s+filed|plaint\s+allegations|injunction\s+order|interim\s+order|'
            r'strike\s+notice|port\s+authority|what\s+happened\s+in\s+this\s+case|key\s+facts\s+of\s+this\s+case|status\s+of\s+this\s+case)\b',
            lower
        ))
        is_case_grammar_typo = bool(re.search(r'\bwhat\s+is\s+this\s+case(?:\s+is)?\s+about\b', lower))
        is_general_case_summary = bool(re.search(r'\b(?:summarize|overview|explain|tell\s+me\s+about)\s+(?:the|this)?\s*(?:matter|case|dispute|situation)\b', lower))

        case_match_score = 0.0
        if matched_case_tuple and matched_case_tuple[1] >= 0.88:
            case_match_score = matched_case_tuple[1]
        elif is_case_keyword or is_case_grammar_typo or is_general_case_summary:
            case_match_score = 0.92
        elif effective_case_id and any(w in lower for w in ["case", "document", "injunction", "order", "contract", "parties", "client"]):
            case_match_score = 0.88

        if case_match_score >= 0.85:
            target_cid = effective_case_id
            if not target_cid and matched_case_tuple:
                target_cid = matched_case_tuple[0]["id"]
            if not target_cid:
                target_cid = "case-01"

            return QueryDecision(
                intent=QueryIntent.CASE_QUERY,
                confidence=case_match_score,
                reason=f"Case-specific inquiry resolved to case matter {target_cid} (Confidence: {int(case_match_score * 100)}%).",
                sub_intent=SubIntent.CASE_SUMMARY.value if (is_case_grammar_typo or is_general_case_summary) else SubIntent.CASE_DOCUMENT_ANALYSIS.value,
                user_goal=UserGoal.UNDERSTAND_CASE.value,
                output_plan=OutputPlan.CASE_SUMMARY.value,
                normalized_query=cleaned,
                requires_case_context=True,
                requires_case_documents=True,
                requires_case_analysis_v1=True,
                case_intent_confidence=case_match_score,
                case_id=target_cid
            )

        # -------------------------------------------------------------
        # STEP 8: Caseload, Portfolio & Advocate Profile / Credentials
        # -------------------------------------------------------------
        # Meta-instructions or conditional feedback (e.g. "if I ask whoami...", "don't include cases", "only tell...")
        # MUST be processed conversationally by the 32B model with dialogue history, NEVER intercepted by rigid templates!
        is_meta_instruction = bool(re.search(
            r"\b(?:if\s+i\s+(?:ask|say|tell)|when\s+i\s+(?:ask|say|tell)|from\s+now\s+on|"
            r"remember\s+(?:that|to)|don.*t\s+(?:show|tell|include|list)|do\s+not\s+(?:show|tell|include|list)|"
            r"only\s+(?:tell|show|give|list)|stop\s+(?:showing|telling|including)|why\s+did\s+you|"
            r"why\s+(?:is|are)\s+the|tell\s+me\s+why)\b",
            lower
        ))

        is_caseload_query = not is_meta_instruction and bool(re.search(
            r'\b(?:what\s+are\s+my\s+(?:current\s+)?cases|my\s+cases|current\s+cases|my\s+current\s+cases|'
            r'list\s+(?:all\s+)?(?:my\s+)?cases|show\s+(?:my\s+)?cases|cases\s+i\s+am\s+working\s+on|'
            r'what\s+cases\s+(?:do\s+i\s+have|am\s+i\s+handling)|my\s+caseload|my\s+docket|active\s+cases|'
            r'pending\s+cases|upcoming\s+hearing|hearing\s+countdown|critical\s+hearing|deadlines|all\s+cases|'
            r'portfolio|what\s+is\s+my\s+priority\s+case|top\s+priority\s+case|highest\s+priority\s+case|priorit(?:y|ize|ization)|case\s+priorit(?:y|ies)|which\s+case\s+(?:first|should\s+i)|rank\s+(?:my\s+)?cases|urgent\s+cases|order\s+of\s+priority|'
            r'my\s+schedule|my\s+calendar|my\s+hearings)\b',
            lower
        ))

        is_profile_query = not is_meta_instruction and bool(re.search(
            r'\b(?:whoami|who\s+am\s+i|my\s+profile|my\s+name|what\s+is\s+my\s+name|'
            r'which\s+court\s+(?:am\s+i|do\s+i)\s+(?:work|practic)(?:ing)?(?:\s+in)?|my\s+court|my\s+courts|'
            r'my\s+bar\s+(?:number|id|council|enrollment)|my\s+legal\s+number(?:s)?|my\s+chamber|my\s+office|'
            r'my\s+credentials|advocate\s+profile|lawyer\s+profile)\b',
            lower
        ))

        if is_caseload_query or is_profile_query:
            return QueryDecision(
                intent=QueryIntent.CASE_MANAGEMENT,
                confidence=0.98,
                reason="Caseload portfolio, upcoming schedule, or advocate profile/credentials inquiry.",
                sub_intent="ADVOCATE_PROFILE" if is_profile_query else SubIntent.PORTFOLIO_HEARINGS.value,
                user_goal=UserGoal.PORTFOLIO_OVERVIEW.value,
                output_plan=OutputPlan.PORTFOLIO_TABLE.value,
                normalized_query=cleaned,
                requires_case_metadata=True
            )

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # Meta-instructions or conditional feedback (e.g. "if I ask whoami...", "don't include cases", "only tell...")
        # MUST be processed conversationally by the 32B model with dialogue history, NEVER intercepted by rigid templates!
        is_meta_instruction = bool(re.search(
            r'\b(?:if\s+i\s+(?:ask|say|tell)|when\s+i\s+(?:ask|say|tell)|from\s+now\s+on|'
            r'remember\s+(?:that|to)|don.*t\s+(?:show|tell|include|list)|do\s+not\s+(?:show|tell|include|list)|'
            r'only\s+(?:tell|show|give|list)|stop\s+(?:showing|telling|including)|why\s+did\s+you|'
            r'why\s+(?:is|are)\s+the|tell\s+me\s+why)\b',
            lower
        ))

        is_caseload_query = not is_meta_instruction and bool(re.search(
            r'\b(?:what\s+are\s+my\s+(?:current\s+)?cases|my\s+cases|current\s+cases|my\s+current\s+cases|'
            r'list\s+(?:all\s+)?(?:my\s+)?cases|show\s+(?:my\s+)?cases|cases\s+i\s+am\s+working\s+on|'
            r'what\s+cases\s+(?:do\s+i\s+have|am\s+i\s+handling)|my\s+caseload|my\s+docket|active\s+cases|'
            r'pending\s+cases|upcoming\s+hearing|hearing\s+countdown|critical\s+hearing|deadlines|all\s+cases|'
            r'portfolio|what\s+is\s+my\s+priority\s+case|top\s+priority\s+case|highest\s+priority\s+case|priorit(?:y|ize|ization)|case\s+priorit(?:y|ies)|which\s+case\s+(?:first|should\s+i)|rank\s+(?:my\s+)?cases|urgent\s+cases|order\s+of\s+priority|'
            r'my\s+schedule|my\s+calendar|my\s+hearings)\b',
            lower
        ))

        is_profile_query = not is_meta_instruction and bool(re.search(
            r'\b(?:whoami|who\s+am\s+i|my\s+profile|my\s+name|what\s+is\s+my\s+name|'
            r'which\s+court\s+(?:am\s+i|do\s+i)\s+(?:work|practic)(?:ing)?(?:\s+in)?|my\s+court|my\s+courts|'
            r'my\s+bar\s+(?:number|id|council|enrollment)|my\s+legal\s+number(?:s)?|my\s+chamber|my\s+office|'
            r'my\s+credentials|advocate\s+profile|lawyer\s+profile)\b',
            lower
        ))

        if is_caseload_query or is_profile_query:
            return QueryDecision(
                intent=QueryIntent.CASE_MANAGEMENT,
                confidence=0.98,
                reason="Caseload portfolio, upcoming schedule, or advocate profile/credentials inquiry.",
                sub_intent="ADVOCATE_PROFILE" if is_profile_query else SubIntent.PORTFOLIO_HEARINGS.value,
                user_goal=UserGoal.PORTFOLIO_OVERVIEW.value,
                output_plan=OutputPlan.PORTFOLIO_TABLE.value,
                normalized_query=cleaned,
                requires_case_metadata=True
            )

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # Meta-instructions or conditional feedback (e.g. "if I ask whoami...", "don't include cases", "only tell...")
        # MUST be processed conversationally by the 32B model with dialogue history, NEVER intercepted by rigid templates!
        is_meta_instruction = bool(re.search(
            r'\b(?:if\s+i\s+(?:ask|say|tell)|when\s+i\s+(?:ask|say|tell)|from\s+now\s+on|'
            r'remember\s+(?:that|to)|don.*t\s+(?:show|tell|include|list)|do\s+not\s+(?:show|tell|include|list)|'
            r'only\s+(?:tell|show|give|list)|stop\s+(?:showing|telling|including)|why\s+did\s+you|'
            r'why\s+(?:is|are)\s+the|tell\s+me\s+why)\b',
            lower
        ))

        is_caseload_query = not is_meta_instruction and bool(re.search(
            r'\b(?:what\s+are\s+my\s+(?:current\s+)?cases|my\s+cases|current\s+cases|my\s+current\s+cases|'
            r'list\s+(?:all\s+)?(?:my\s+)?cases|show\s+(?:my\s+)?cases|cases\s+i\s+am\s+working\s+on|'
            r'what\s+cases\s+(?:do\s+i\s+have|am\s+i\s+handling)|my\s+caseload|my\s+docket|active\s+cases|'
            r'pending\s+cases|upcoming\s+hearing|hearing\s+countdown|critical\s+hearing|deadlines|all\s+cases|'
            r'portfolio|what\s+is\s+my\s+priority\s+case|top\s+priority\s+case|highest\s+priority\s+case|priorit(?:y|ize|ization)|case\s+priorit(?:y|ies)|which\s+case\s+(?:first|should\s+i)|rank\s+(?:my\s+)?cases|urgent\s+cases|order\s+of\s+priority|'
            r'my\s+schedule|my\s+calendar|my\s+hearings)\b',
            lower
        ))

        is_profile_query = not is_meta_instruction and bool(re.search(
            r'\b(?:whoami|who\s+am\s+i|my\s+profile|my\s+name|what\s+is\s+my\s+name|'
            r'which\s+court\s+(?:am\s+i|do\s+i)\s+(?:work|practic)(?:ing)?(?:\s+in)?|my\s+court|my\s+courts|'
            r'my\s+bar\s+(?:number|id|council|enrollment)|my\s+legal\s+number(?:s)?|my\s+chamber|my\s+office|'
            r'my\s+credentials|advocate\s+profile|lawyer\s+profile)\b',
            lower
        ))

        if is_caseload_query or is_profile_query:
            return QueryDecision(
                intent=QueryIntent.CASE_MANAGEMENT,
                confidence=0.98,
                reason="Caseload portfolio, upcoming schedule, or advocate profile/credentials inquiry.",
                sub_intent="ADVOCATE_PROFILE" if is_profile_query else SubIntent.PORTFOLIO_HEARINGS.value,
                user_goal=UserGoal.PORTFOLIO_OVERVIEW.value,
                output_plan=OutputPlan.PORTFOLIO_TABLE.value,
                normalized_query=cleaned,
                requires_case_metadata=True
            )

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        is_caseload_query = bool(re.search(
            r'\b(?:what\s+are\s+my\s+(?:current\s+)?cases|my\s+cases|current\s+cases|my\s+current\s+cases|'
            r'list\s+(?:all\s+)?(?:my\s+)?cases|show\s+(?:my\s+)?cases|cases\s+i\s+am\s+working\s+on|'
            r'what\s+cases\s+(?:do\s+i\s+have|am\s+i\s+handling)|my\s+caseload|my\s+docket|active\s+cases|'
            r'pending\s+cases|upcoming\s+hearing|hearing\s+countdown|critical\s+hearing|deadlines|all\s+cases|'
            r'portfolio|what\s+is\s+my\s+priority\s+case|top\s+priority\s+case|highest\s+priority\s+case|priorit(?:y|ize|ization)|case\s+priorit(?:y|ies)|which\s+case\s+(?:first|should\s+i)|rank\s+(?:my\s+)?cases|urgent\s+cases|order\s+of\s+priority|'
            r'my\s+schedule|my\s+calendar|my\s+hearings)\b',
            lower
        ))

        is_profile_query = bool(re.search(
            r'\b(?:who\s+am\s+i|my\s+profile|my\s+name|what\s+is\s+my\s+name|'
            r'which\s+court\s+(?:am\s+i|do\s+i)\s+(?:work|practic)(?:ing)?(?:\s+in)?|my\s+court|my\s+courts|'
            r'my\s+bar\s+(?:number|id|council|enrollment)|my\s+legal\s+number(?:s)?|my\s+chamber|my\s+office|'
            r'my\s+credentials|advocate\s+profile|lawyer\s+profile)\b',
            lower
        ))

        if is_caseload_query or is_profile_query:
            return QueryDecision(
                intent=QueryIntent.CASE_MANAGEMENT,
                confidence=0.98,
                reason="Caseload portfolio, upcoming schedule, or advocate profile/credentials inquiry.",
                sub_intent="ADVOCATE_PROFILE" if is_profile_query else SubIntent.PORTFOLIO_HEARINGS.value,
                user_goal=UserGoal.PORTFOLIO_OVERVIEW.value,
                output_plan=OutputPlan.PORTFOLIO_TABLE.value,
                normalized_query=cleaned,
                requires_case_metadata=True
            )

        # -------------------------------------------------------------
        # STEP 9: Base Qwen Parametric Understanding Fallback
        # If confidence threshold did not meet 80% for specialized RAG,
        # Base Qwen directly understands the concept and responds parametrically!
        # Zero robotic templates, zero ungrounded RAG hallucination.
        # -------------------------------------------------------------
        return QueryDecision(
            intent=QueryIntent.GENERAL,
            confidence=0.85,
            reason="Query evaluated with Base Qwen parametric conceptual understanding without ungrounded RAG.",
            sub_intent="CONCEPTUAL_UNDERSTANDING",
            user_goal="CONCEPTUAL_EXPLANATION",
            output_plan="STRUCTURED_RESPONSE",
            normalized_query=cleaned,
            requires_base_qwen=True,
            case_id=effective_case_id
        )


_ROUTER_INSTANCE = None

def get_query_router(db_path: str = "data/legalai_app.db") -> UniversalQueryRouter:
    global _ROUTER_INSTANCE
    if _ROUTER_INSTANCE is None:
        _ROUTER_INSTANCE = UniversalQueryRouter(db_path=db_path)
    return _ROUTER_INSTANCE

QueryRouter = UniversalQueryRouter
