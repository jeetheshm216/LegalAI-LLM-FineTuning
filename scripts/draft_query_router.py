"""
src/api/query_router.py

Universal Query Understanding & Adaptive Routing Engine for LegalAI.

Implements the 4-dimensional separation:
  QUERY INTENT ≠ AVAILABLE CONTEXT ≠ DATA SOURCE ≠ MODEL / ADAPTER

Taxonomy (11 Core Classes):
  1. CONVERSATIONAL: Pure greetings, gratitude, courteous banter, pleasantries.
  2. SYSTEM_INFO: Application architecture, foundation model, LoRA adapters,
                 supported corpus scope, system capabilities, technology stack.
  3. TECHNICAL_AI: Conceptual explanations of AI, ML, LLMs, RAG, LoRA,
                   fine-tuning, vector databases, embeddings.
  4. CASE_MANAGEMENT: Portfolio queries, case priority, urgency, focus,
                     upcoming court hearings, deadlines, court calendar.
  5. LEGAL_QUERY: Substantive and procedural legal concepts (negligence, bail,
                  FIR process, self-defence, consideration, limitation) without
                  requiring the literal word 'legal' or 'law'.
  6. EXACT_PROVISION_QUERY: Explicit statutory sections, articles, orders, rules
                           requiring authoritative statutory RAG retrieval.
  7. CASE_QUERY: Document-specific evidentiary inquiries (missing evidence,
                 contradictions, chargesheet allegations, pleadings).
  8. HEARING_PREPARATION: Case preparation points, judge arguments, strategic
                         points for an active matter.
  9. MIXED_LEGAL_CASE: Composed inquiries spanning legal authorities and case facts.
  10. OUT_OF_SCOPE: Programming requests, movies, sports, recipes, general trivia.
  11. AMBIGUOUS: Isolated cryptic tokens or unresolvable fragments requiring clarification.

Safety Invariant: Fail closed with safe clarification or qualified boundary.
Never guess, never fabricate, never route uncertain queries to random RAG.
"""

import re
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

    # Backward-compatibility alias
    GENERAL_NON_LEGAL = "OUT_OF_SCOPE"


@dataclass
class QueryDecision:
    intent: QueryIntent
    confidence: float
    reason: str
    sub_intent: Optional[str] = None
    matched_patterns: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)

    # Decoupled workflow flags
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

    # Metrics
    legal_intent_confidence: float = 0.0
    case_intent_confidence: float = 0.0
    target_act: Optional[str] = None
    target_provision: Optional[str] = None
    case_id: Optional[str] = None


# Backward-compatibility alias
RoutingResult = QueryDecision


class UniversalQueryRouter:
    """
    Universal Query Understanding & Adaptive Routing Engine.
    Evaluates semantic meaning, entities, context, and required data sources.
    """

    # -------------------------------------------------------------------------
    # 1. SYSTEM & PRODUCT PATTERNS
    # Questions about LegalAI, its underlying model, architecture, and technology.
    # -------------------------------------------------------------------------
    SYSTEM_PATTERNS = [
        r'\b(?:what|which)\s+(?:is\s+)?(?:the\s+)?(?:ai\s+)?model\s+(?:of|is|powers?|running|behind)\s+(?:legal\s*ai|the\s+assistant|this\s+app|this\s+system)\b',
        r'\b(?:what|which)\s+(?:ai\s+)?model\s+(?:are\s+you|is\s+legal\s*ai)\s+(?:using|powered\s+by|based\s+on)\b',
        r'\b(?:what|which)\s+(?:llm|foundation\s+model|neural\s+network|architecture)\s+(?:are\s+you|is\s+legal\s*ai)\s+(?:using|powered\s+by|based\s+on|running)\b',
        r'\bwhat\s+model\s+(?:powers?|runs?)\s+legal\s*ai\b',
        r'\bwhat\s+model\s+(?:are\s+you\s+using|do\s+you\s+use)\b',
        r'\bwhat\s+is\s+the\s+model\s+of\s+legal\s*ai\b',
        r'\bwhat\s+powers\s+(?:this\s+assistant|legal\s*ai|the\s+assistant)\b',
        r'\bhow\s+was\s+legal\s*ai\s+(?:built|trained|developed|created)\b',
        r'\bwhat\s+technolog(?:y|ies)\s+(?:does\s+legal\s*ai\s+use|powers?\s+this\s+system|is\s+behind\s+this)\b',
        r'\bhow\s+does\s+legal\s*ai\s+work\b',
        r'\bwhat\s+is\s+legal\s*ai\b',
        r'\btell\s+me\s+about\s+legal\s*ai\b',
        r'\bdoes\s+legal\s*ai\s+use\s+(?:rag|fine-?tuning|lora|qwen)\b',
        r'\bwhy\s+does\s+legal\s*ai\s+use\s+qwen\b',
        r'\bhow\s+does\s+the\s+legal\s+model\s+know\s+current\s+indian\s+law\b',
        r'\bcan\s+legal\s*ai\s+analyze\s+my\s+case\s+documents\b',
        r'\bwhat\s+(?:are\s+)?(?:the\s+)?(?:capabilities|features)\s+of\s+legal\s*ai\b',
        r'\bwhat\s+can\s+legal\s*ai\s+do\b',
        r'\bwhat\s+can\s+you\s+do(?:\s+for\s+me)?\b',
        r'\bwhat\s+are\s+your\s+capabilities\b',
        r'\bwhat\s+can\s+i\s+ask\s+you\b',
    ]

    # -------------------------------------------------------------------------
    # 2. TECHNICAL AI & ML KNOWLEDGE PATTERNS
    # Questions asking for conceptual explanations of AI/ML/LLM technologies.
    # -------------------------------------------------------------------------
    TECHNICAL_AI_PATTERNS = [
        r'\bwhat\s+is\s+(?:artificial\s+intelligence|ai)\b',
        r'\bwhat\s+is\s+(?:machine\s+learning|ml|deep\s+learning)\b',
        r'\bwhat\s+is\s+(?:an?\s+)?(?:llm|large\s+language\s+model)\b',
        r'\bwhat\s+is\s+(?:qwen|qwen2(?:\.5)?(?:-14b)?)\b',
        r'\bcan\s+you\s+explain\s+qwen\b',
        r'\b(?:what\s+is|explain)\s+(?:rag|retrieval\s+augmented\s+generation)\b',
        r'\bhow\s+does\s+(?:rag|retrieval\s+augmented\s+generation)\s+work\b',
        r'\b(?:what\s+is|explain|what\s+does\s+mean)\s+(?:a\s+)?(?:lora|peft|low[\s-]rank\s+adaptation)(?:\s+adapter)?\b',
        r'\b(?:what\s+is|explain|how\s+does)\s+(?:fine-?tuning|supervised\s+fine-?tuning|sft)(?:\s+work)?\b',
        r'\bwhy\s+(?:do\s+people\s+)?fine-?tune\s+(?:a\s+)?(?:language\s+model|llm)\b',
        r'\bwhat\s+is\s+the\s+difference\s+between\s+rag\s+and\s+fine-?tuning\b',
        r'\bhow\s+does\s+rag\s+differ\s+from\s+fine-?tuning\b',
        r'\bwhat\s+are\s+(?:vector\s+)?embeddings\b',
        r'\bwhat\s+is\s+a\s+vector\s+(?:database|store|index)\b',
        r'\bwhat\s+is\s+(?:a\s+)?(?:context\s+window|tokenization|tokens?)\b',
        r'\bwhat\s+is\s+prompt\s+engineering\b',
        r'\bhow\s+do\s+transformers\s+work\b',
    ]

    # -------------------------------------------------------------------------
    # 3. CASE MANAGEMENT & PORTFOLIO WORKLOAD PATTERNS
    # Queries about priorities, upcoming hearings, deadlines, court schedule.
    # -------------------------------------------------------------------------
    CASE_MANAGEMENT_PATTERNS = [
        r'\bwhat\s+(?:is\s+)?(?:the\s+)?important\s+thing\s+i\s+have\s+to\s+focus\s+on\b',
        r'\bwhat\s+should\s+i\s+focus\s+on\s+now\b',
        r'\bwhat\s+case\s+i\s+have\s+to\s+focus\s+more\b',
        r'\bwhich\s+case\s+should\s+i\s+focus\s+on\b',
        r'\bwhich\s+case\s+(?:has\s+the\s+highest\s+priority|is\s+highest\s+priority)\b',
        r'\bwhat\s+is\s+my\s+most\s+urgent\s+case\b',
        r'\bwhich\s+(?:cases?|matters?)\s+(?:are|is)\s+urgent\b',
        r'\bshow\s+(?:me\s+)?(?:my\s+)?urgent\s+(?:cases?|matters?)\b',
        r'\bwhich\s+(?:cases?|matters?)\s+need\s+attention\b',
        r'\bwhat\s+hearings?\s+are\s+(?:scheduled|coming\s+up)(?:\s+(?:for\s+)?this\s+week)?\b',
        r'\bwhat\s+hearings?\s+do\s+i\s+have\b',
        r'\bwhen\s+is\s+my\s+next\s+hearing\b',
        r'\bwhich\s+cases?\s+have\s+upcoming\s+(?:deadlines|hearings)\b',
        r'\bwhat\s+deadlines?\s+do\s+i\s+have\b',
        r'\bmy\s+court\s+calendar\b',
        r'\bportfolio\s+status\b',
        r'\blist\s+(?:my\s+)?cases\b',
    ]

    # -------------------------------------------------------------------------
    # 4. HEARING PREPARATION PATTERNS
    # Preparation for a court hearing on an active legal matter.
    # -------------------------------------------------------------------------
    HEARING_PREP_PATTERNS = [
        r'\bwhat\s+should\s+i\s+prepare\s+for\s+(?:the\s+)?(?:next\s+)?hearing\b',
        r'\bprepare\s+(?:me|us)\s+for\s+(?:the\s+)?(?:next\s+)?hearing\b',
        r'\bwhat\s+points\s+should\s+i\s+(?:tell|raise\s+before|argue\s+before)\s+the\s+judge\b',
        r'\bwhat\s+are\s+the\s+important\s+points\s+for\s+the\s+next\s+hearing\b',
        r'\bwhat\s+should\s+i\s+focus\s+on\s+before\s+the\s+hearing\b',
        r'\bhearing\s+strategy\b',
    ]

    # -------------------------------------------------------------------------
    # 5. CASE DOCUMENT & EVIDENCE INQUIRY PATTERNS
    # Evidentiary facts, contradictions, missing documents in uploaded case files.
    # -------------------------------------------------------------------------
    CASE_EVIDENCE_PATTERNS = [
        r'\b(?:what\s+)?evidence\s+(?:is\s+)?missing(?:\s+in\s+(?:my|this|the)\s+case)?\b',
        r'\bwhat\s+documents?\s+(?:are\s+)?missing\b',
        r'\bwhat\s+contradictions?\s+(?:exist|are\s+there|are\s+present)\b',
        r'\bcontradictions?\s+in\s+(?:the\s+)?(?:evidence|documents?|testimony|statements?|case)\b',
        r'\bwhat\s+are\s+the\s+key\s+facts\s+(?:in|of)\s+(?:this|my|the)\s+case\b',
        r'\bkey\s+facts\s+(?:in|of)\s+(?:this|my|the)\s+(?:case|matter)\b',
        r'\bwhat\s+documents?\s+support\s+(?:the\s+)?(?:client(?:\'?s)?\s+)?(?:claim|allegation|position)\b',
        r'\bevidence\s+supports\s+our\s+(?:position|case|argument)\b',
        r'\bweaknesses?\s+in\s+(?:this|the|my|our)\s+case\b',
        r'\bwhat\s+arguments?\s+can\s+the\s+opposing\s+counsel\s+make\b',
        r'\bwhat\s+allegations?\s+are\s+made\s+(?:in\s+the\s+(?:fir|complaint|petition))\b',
        r'\bsummarize\s+(?:this\s+case|the\s+uploaded\s+documents?|the\s+case\s+documents?)\b',
        r'\binconsistencies\s+in\s+(?:the\s+)?witness\b',
        r'\bwitness\s+statements?\b',
        r'\bwhat\s+happened\s+(?:at|in)\s+(?:the\s+last\s+hearing|my\s+case|this\s+case)\b',
    ]

    # -------------------------------------------------------------------------
    # 6. EXACT STATUTORY PROVISION PATTERNS
    # Cites a specific numbered section, article, order, or provision syntax.
    # -------------------------------------------------------------------------
    STATUTE_SECTION_PATTERNS = [
        r'\b(?:section|sec\.?|s\.?|u/s|\u00a7|provision)\s*[0-9]+[A-Za-z]*\b',
        r'\barticle\s+[0-9]+[A-Za-z]*\b',
        r'\border\s+[0-9IVXLCDM]+\s+(?:rule\s+[0-9]+)?\b',
        r'\bclause\s+[0-9]+(?:\([a-z0-9]+\))*\b',
        r'\bschedule\s+[0-9IVXLCDM]+\b',
        r'\bact\s+[0-9]+[A-Za-z]*\b',
    ]

    ACT_NAME_PATTERNS = [
        r'\b(?:bns|bnss|bsa)\b',
        r'\bbharatiya\s+nyaya\s+sanhita(?:\s*,?\s*2023)?\b',
        r'\bbharatiya\s+nagarik\s+suraksha\s+sanhita(?:\s*,?\s*2023)?\b',
        r'\bbharatiya\s+sakshya\s+adhiniyam(?:\s*,?\s*2023)?\b',
        r'\b(?:ipc|crpc|iea)\b',
        r'\bindian\s+penal\s+code\b',
        r'\bcode\s+of\s+criminal\s+procedure\b',
        r'\b(?:indian\s+)?evidence\s+act\b',
        r'\bconstitution\s+of\s+india\b',
        r'\bnegotiable\s+instruments?\s+(?:act)?\b',
        r'\bni\s+act\b',
        r'\brera\b',
        r'\bcompanies\s+act\b',
        r'\bcontract\s+act\b',
        r'\barbitration\s+(?:and\s+conciliation\s+)?act\b',
        r'\btransfer\s+of\s+property\s+act\b',
        r'\blimitation\s+act\b',
        r'\bconsumer\s+protection\s+act\b',
        r'\bmotor\s+vehicles?\s+act\b',
        r'\binformation\s+technology\s+act(?:\s*,?\s*2000)?\b',
        r'\bit\s+act(?:\s*,?\s*2000)?\b',
        r'\bita(?:\s*,?\s*2000)?\b',
        r'\bright\s+to\s+information(?:\s+act)?(?:\s*,?\s*2005)?\b',
        r'\brti(?:\s+act)?(?:\s*,?\s*2005)?\b',
        r'\bpocso(?:\s+act)?\b',
        r'\bndps(?:\s+act)?\b',
        r'\bpmla(?:\s+act)?\b',
        r'\buapa(?:\s+act)?\b',
        r'\bposh\s+act\b',
        r'\bsarfaesi(?:\s+act)?\b',
        r'\bibc\b',
        r'\binsolvency\s+and\s+bankruptcy(?:\s+code)?\b',
        r'\bcivil\s+procedure\s+code\b',
        r'\bcpc\b',
        r'\b(?!(?:act\s+of\s+god|caught\s+in\s+the\s+act|act\s+as|act\s+upon|to\s+act|second\s+act|final\s+act)\b)(?:[A-Z][a-zA-Z0-9\s,\-\'\&]{1,60}?)\s+Act(?:\s*,?\s*(?:18|19|20)[0-9]{2})?\b',
        r'\b[A-Za-z\s]+(?:Sanhita|Adhiniyam|Ordinance)(?:\s*,?\s*(?:18|19|20)[0-9]{2})?\b',
    ]

    # -------------------------------------------------------------------------
    # 7. GENERAL LEGAL CONCEPTS (WITHOUT REQUIRING WORD "LEGAL" OR "LAW")
    # Substantive doctrines, penal offences, civil doctrines, procedural remedies.
    # -------------------------------------------------------------------------
    LEGAL_CONCEPT_PATTERNS = [
        r'\b(?:what\s+is\s+)?negligence\b',
        r'\b(?:what\s+is\s+)?(?:anticipatory\s+)?bail\b',
        r'\b(?:what\s+is\s+)?defamation\b',
        r'\b(?:what\s+is\s+)?self[\s-]defen[sc]e\b',
        r'\bwhat\s+happens\s+after\s+(?:an?\s+)?fir\b',
        r'\b(?:what\s+is\s+)?consideration(?:\s+in\s+contract)?\b',
        r'\b(?:what\s+is\s+the\s+)?punishment\s+for\s+[a-z\s]+\b',
        r'\b(?:what\s+is\s+)?cheating\b',
        r'\b(?:what\s+is\s+)?murder\b',
        r'\bculpable\s+homicide\b',
        r'\btheft\b',
        r'\brobbery\b',
        r'\bdacoity\b',
        r'\bextortion\b',
        r'\bfraud\b',
        r'\bforgery\b',
        r'\bcriminal\s+(?:breach\s+of\s+trust|conspiracy|intimidation|trespass)\b',
        r'\bcheque\s+(?:bounce|dishonou?r)\b',
        r'\bquashing(?:\s+of\s+fir)?\b',
        r'\bcognizance\b',
        r'\bdischarge\b',
        r'\bremand\b',
        r'\bpolice\s+custody\b',
        r'\bjudicial\s+custody\b',
        r'\barrest\b',
        r'\bcognizable\b',
        r'\bnon-cognizable\b',
        r'\bbailable\b',
        r'\bnon-bailable\b',
        r'\blimitation\s+period\b',
        r'\bperiod\s+of\s+limitation\b',
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
        r'\bappeal\b',
        r'\brevision\b',
        r'\bspecial\s+leave\s+petition\b',
        r'\bslp\b',
        r'\bwrit\s+petition\b',
        r'\bhabeas\s+corpus\b',
        r'\bmandamus\b',
        r'\binjunction\b',
        r'\bstay\s+order\b',
        r'\bmens\s+rea\b',
        r'\bactus\s+reus\b',
        r'\bres\s+judicata\b',
        r'\bpromissory\s+estoppel\b',
        r'\bspecific\s+performance\b',
        r'\bvicarious\s+liability\b',
        r'\bstrict\s+liability\b',
        r'\babsolute\s+liability\b',
        r'\blegal\s+(?:notice|remedy|heir|rights?|advice)\b',
    ]

    # -------------------------------------------------------------------------
    # 8. OUT-OF-SCOPE (NON-LEGAL, NON-AI, NON-CASE) PATTERNS
    # Strictly programming, entertainment, sports, cooking, consumer shopping.
    # -------------------------------------------------------------------------
    OUT_OF_SCOPE_PATTERNS = [
        # Coding & programming requests
        r'\b(?:write|create|generate|show\s+me|build)(?:\s+me)?\s+(?:a\s+)?(?:python|c\+\+|java|javascript|php|ruby|rust|golang|sql|html|css)?\s*(?:code|program|script|function|class|file|game|app)\b',
        r'\b(?:python|c\+\+|java|javascript|php|ruby|rust|golang)\s+(?:code|game|program|script|developer)\b',
        r'\b(?:sort\s+a\s+list|fibonacci|binary\s+search|bubble\s+sort|merge\s+sort|palindrome\s+function)\b',
        r'\b(?:print\s+hello\s+world|hello\s+world\s+program)\b',
        # Entertainment & pop culture
        r'\b(?:last|latest|new)\s+(?:vijay|ajith|rajini|kamal|shah\s*rukh|salman)\s+(?:movie|film)\b',
        r'\b(?:recommend|suggest)\s+(?:a\s+)?(?:movie|film|song|series|anime|book|novel)\b',
        r'\btell\s+me\s+a\s+movie\s+(?:plot|story)\b',
        # Sports & athletics
        r'\bwho\s+won\s+.*?\b(?:match|game|tournament|cup|trophy)\b',
        r'\b(?:cricket\s+score|match\s+result|football\s+score|fifa|ipl\s+score)\b',
        r'\b(?:virat\s+kohli|rohit\s+sharma|dhoni|messi|ronaldo)\b',
        # Cooking & food
        r'\bhow\s+do\s+i\s+cook\b',
        r'\b(?:recipe\s+for|recipes?|biryani|pizza|burger|pasta|curry|cook|cooking|bake)\b',
        # Consumer tech shopping & gadget recommendations
        r'\b(?:what|which)\s+laptop\s+should\s+i\s+buy\b',
        r'\b(?:recommend|suggest|best)\s+(?:a\s+)?(?:laptop|phone|smartphone|camera|headphones|car|bike|television|tv)\b',
        # General non-legal trivia & weather
        r'\bwhat\s+is\s+the\s+capital\s+of\b',
        r'\b(?:weather\s+in|weather\s+today|temperature\s+in)\b',
        r'\btell\s+me\s+a\s+joke\b',
    ]

    # -------------------------------------------------------------------------
    # 9. CONVERSATIONAL PATTERNS
    # -------------------------------------------------------------------------
    CONVERSATIONAL_PATTERNS = [
        r'^(?:hi|hello|hey|hiya|howdy|good\s+(?:morning|afternoon|evening|day)|greetings)(?:[\s,!.]+)?$',
        r'^(?:hey|hi|hello)\s+(?:hi|hey|hello|there|legalai|assistant|again)(?:[\s,!.]+)?$',
        r'^(?:hi|hello|hey|hiya|howdy)[,\s!]+.*?(?:how\s+are\s+you|how\'s\s+it\s+going|what\'s\s+up|how\s+are\s+you\s+doing(?:\s+today)?|how\s+do\s+you\s+do)(?:[\s,?!.]+)?$',
        r'^(?:how\s+are\s+you|how\s+are\s+you\s+doing(?:\s+today)?|how\'s\s+it\s+going(?:\s+today)?|how\s+do\s+you\s+do)(?:[\s,?!.]+)?$',
        r'^(?:thanks|thank\s+you|thank\s+you\s+(?:so\s+much|very\s+much)|many\s+thanks|appreciate\s+it|thx)(?:[\s,!.]+)?$',
        r'^(?:thanks|thank\s+you)(?:\s+so\s+much|\s+very\s+much)?[,\s]+(?:legalai|for\s+(?:your\s+help|the\s+help|helping|explaining|the\s+clarification|clarifying|this|that))(?:[\s,!.]+)?$',
        r'^(?:ok\s+thanks|okay\s+thanks|great\s+thanks|thanks\s+for\s+helping)(?:[\s,!.]+)?$',
        r'^(?:who\s+are\s+you|what\s+are\s+you|what\s+is\s+your\s+name|are\s+you\s+an?\s+ai)(?:[\s,?!.]+)?$',
        r'^(?:nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)(?:[\s,!.]+)?$',
        r'^(?:ok|okay|got\s+it|understood|cool|great|awesome|perfect|sure|alright|fine)(?:[\s,!.]+)?$',
        r'^(?:bye|goodbye|see\s+you|have\s+a\s+(?:nice|good)\s+day)(?:[\s,!.]+)?$',
    ]

    # -------------------------------------------------------------------------
    # 10. ANAPHORIC CONTEXT PATTERNS (GENUINE CONTINUATION)
    # Only when the user uses demonstratives referring back to the previous turn.
    # -------------------------------------------------------------------------
    ANAPHORIC_PATTERNS = [
        r'^(?:what\s+about\s+(?:that|it|this|the\s+former|the\s+latter)|explain\s+(?:that|it|this\s+further|more)|can\s+you\s+elaborate(?:\s+on\s+that)?|why\s+is\s+that|and\s+then\s+what)(?:[\s,?!.]+)?$',
        r'^(?:for\s+odd\s+or\s+even|can\s+you\s+make\s+it\s+shorter\??|what\s+about\s+the\s+previous\s+one\??)(?:[\s,?!.]+)?$',
        r'^(?:what\s+punishment\s+applies\??|what\s+is\s+the\s+penalty\??)$',
    ]

    def __init__(self):
        self._system_regexes = [re.compile(p, re.IGNORECASE) for p in self.SYSTEM_PATTERNS]
        self._tech_ai_regexes = [re.compile(p, re.IGNORECASE) for p in self.TECHNICAL_AI_PATTERNS]
        self._case_mgmt_regexes = [re.compile(p, re.IGNORECASE) for p in self.CASE_MANAGEMENT_PATTERNS]
        self._hearing_prep_regexes = [re.compile(p, re.IGNORECASE) for p in self.HEARING_PREP_PATTERNS]
        self._case_evidence_regexes = [re.compile(p, re.IGNORECASE) for p in self.CASE_EVIDENCE_PATTERNS]
        self._statute_sec_regexes = [re.compile(p, re.IGNORECASE) for p in self.STATUTE_SECTION_PATTERNS]
        self._act_name_regexes = [re.compile(p, re.IGNORECASE) for p in self.ACT_NAME_PATTERNS]
        self._legal_concept_regexes = [re.compile(p, re.IGNORECASE) for p in self.LEGAL_CONCEPT_PATTERNS]
        self._out_of_scope_regexes = [re.compile(p, re.IGNORECASE) for p in self.OUT_OF_SCOPE_PATTERNS]
        self._conversational_regexes = [re.compile(p, re.IGNORECASE) for p in self.CONVERSATIONAL_PATTERNS]
        self._anaphoric_regexes = [re.compile(p, re.IGNORECASE) for p in self.ANAPHORIC_PATTERNS]

    def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        case_id: Optional[str] = None,
        mode: Optional[str] = None
    ) -> QueryDecision:
        """
        Universal Query Understanding & Adaptive Decision.
        Decouples Intent from Context, Data Source, and Model/Adapter.
        """
        cleaned = message.strip()
        if not cleaned:
            return QueryDecision(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=1.0,
                reason="Empty query treated as conversational prompt.",
                matched_patterns=["EMPTY_QUERY"],
                sub_intent="GREETING"
            )

        # ---------------------------------------------------------------------
        # STEP 1: Scan for substantive anchors and entities
        # ---------------------------------------------------------------------
        matched_statute_provisions = [m.group(0) for r in self._statute_sec_regexes if (m := r.search(cleaned))]
        matched_statute_acts = [m.group(0) for r in self._act_name_regexes if (m := r.search(cleaned))]
        matched_legal_concepts = [m.group(0) for r in self._legal_concept_regexes if (m := r.search(cleaned))]
        
        matched_system = [m.group(0) for r in self._system_regexes if (m := r.search(cleaned))]
        matched_tech_ai = [m.group(0) for r in self._tech_ai_regexes if (m := r.search(cleaned))]
        matched_case_mgmt = [m.group(0) for r in self._case_mgmt_regexes if (m := r.search(cleaned))]
        matched_hearing_prep = [m.group(0) for r in self._hearing_prep_regexes if (m := r.search(cleaned))]
        matched_case_evidence = [m.group(0) for r in self._case_evidence_regexes if (m := r.search(cleaned))]
        matched_out_of_scope = [m.group(0) for r in self._out_of_scope_regexes if (m := r.search(cleaned))]
        matched_conv = [m.group(0) for r in self._conversational_regexes if (m := r.match(cleaned))]

        has_exact_provision = bool(matched_statute_provisions and (matched_statute_acts or "section" in cleaned.lower() or "article" in cleaned.lower()))
        has_legal_concept = bool(matched_statute_acts or matched_legal_concepts)
        
        # Entity bundle
        entities = {
            "provisions": matched_statute_provisions,
            "acts": matched_statute_acts,
            "legal_concepts": matched_legal_concepts,
            "system_entities": matched_system,
            "tech_ai_entities": matched_tech_ai,
            "case_mgmt_entities": matched_case_mgmt,
            "available_case_id": case_id
        }

        # ---------------------------------------------------------------------
        # STEP 2: Handle Explicit System / Product Inquiries
        # Questions asking what model powers LegalAI, how it works, capabilities.
        # Strict Rule: Must NEVER enter Case RAG or Legal RAG.
        # ---------------------------------------------------------------------
        if matched_system and not (has_exact_provision and not any("legalai" in cleaned.lower() for _ in [1])):
            return QueryDecision(
                intent=QueryIntent.SYSTEM_INFO,
                confidence=0.98,
                reason="Query inquires about LegalAI system architecture, foundation model, or product specifications.",
                sub_intent="SYSTEM_SPECIFICATION",
                matched_patterns=matched_system,
                entities=entities,
                requires_case_context=False,
                requires_case_documents=False,
                requires_case_metadata=False,
                requires_legal_rag=False,
                requires_system_context=True,
                requires_base_qwen=True,
                requires_legalai_v2=False,
                requires_case_analysis_v1=False
            )

        # ---------------------------------------------------------------------
        # STEP 3: Handle Technical AI / ML Knowledge Inquiries
        # Explaining AI, ML, LLMs, RAG, LoRA, fine-tuning, vector databases.
        # Strict Rule: Base Qwen handles these conceptually. Zero RAG retrieval.
        # ---------------------------------------------------------------------
        if matched_tech_ai and not (matched_case_evidence or has_exact_provision):
            return QueryDecision(
                intent=QueryIntent.TECHNICAL_AI,
                confidence=0.98,
                reason="Query asks for a technical explanation of artificial intelligence or LLM concept.",
                sub_intent="TECHNICAL_CONCEPT",
                matched_patterns=matched_tech_ai,
                entities=entities,
                requires_case_context=False,
                requires_case_documents=False,
                requires_case_metadata=False,
                requires_legal_rag=False,
                requires_technical_explanation=True,
                requires_base_qwen=True,
                requires_legalai_v2=False,
                requires_case_analysis_v1=False
            )

        # ---------------------------------------------------------------------
        # STEP 4: Handle Case Management & Portfolio Workload Inquiries
        # Questions about priority, urgency, focus, hearings this week, deadlines.
        # Strict Rule: Queries SQLite application database metadata; ZERO Case Document RAG.
        # ---------------------------------------------------------------------
        if matched_case_mgmt:
            return QueryDecision(
                intent=QueryIntent.CASE_MANAGEMENT,
                confidence=0.98,
                reason="Query asks about case priority, urgency, task focus, or upcoming court schedule across matters.",
                sub_intent="PORTFOLIO_WORKLOAD",
                matched_patterns=matched_case_mgmt,
                entities=entities,
                requires_case_context=bool(case_id),
                requires_case_documents=False,
                requires_case_metadata=True,
                requires_legal_rag=False,
                requires_base_qwen=True,
                requires_legalai_v2=False,
                requires_case_analysis_v1=False,
                case_intent_confidence=0.95
            )

        # ---------------------------------------------------------------------
        # STEP 5: Handle Hearing Preparation for Active Matter
        # Strategic preparation for next hearing, judge arguments.
        # ---------------------------------------------------------------------
        if matched_hearing_prep:
            return QueryDecision(
                intent=QueryIntent.HEARING_PREPARATION,
                confidence=0.98,
                reason="Query asks for strategic hearing preparation and key argument formulation for a matter.",
                sub_intent="HEARING_PREPARATION",
                matched_patterns=matched_hearing_prep,
                entities=entities,
                requires_case_context=True,
                requires_case_documents=True,
                requires_case_metadata=True,
                requires_legal_rag=False,
                requires_case_analysis_v1=True,
                case_intent_confidence=0.98,
                case_id=case_id
            )

        # ---------------------------------------------------------------------
        # STEP 6: Handle Case Document / Evidence Queries
        # Specific evidentiary inquiries: missing documents, contradictions, key facts.
        # ---------------------------------------------------------------------
        if matched_case_evidence:
            return QueryDecision(
                intent=QueryIntent.CASE_QUERY,
                confidence=0.98,
                reason="Query addresses specific case documents, missing evidence, contradictions, or chargesheet facts.",
                sub_intent="CASE_DOCUMENT_ANALYSIS",
                matched_patterns=matched_case_evidence,
                entities=entities,
                requires_case_context=True,
                requires_case_documents=True,
                requires_case_metadata=False,
                requires_legal_rag=False,
                requires_case_analysis_v1=True,
                case_intent_confidence=0.98,
                case_id=case_id
            )

        # ---------------------------------------------------------------------
        # STEP 7: Handle Exact Statutory Provisions (EXACT_PROVISION_QUERY)
        # Specific section, article, order, rule in an enactment.
        # Strict Rule: Requires authoritative statutory RAG + LegalAI V2 LoRA.
        # ---------------------------------------------------------------------
        if matched_statute_provisions or (matched_statute_acts and any(kw in cleaned.lower() for kw in ["section", "article", "order", "rule", "clause"])):
            all_matches = matched_statute_provisions + matched_statute_acts
            return QueryDecision(
                intent=QueryIntent.EXACT_PROVISION_QUERY,
                confidence=0.98,
                reason="Query contains specific statutory provision identifier requiring authoritative RAG retrieval.",
                sub_intent="EXACT_STATUTORY_PROVISION",
                matched_patterns=all_matches,
                entities=entities,
                requires_case_context=False,
                requires_case_documents=False,
                requires_case_metadata=False,
                requires_legal_rag=True,
                requires_exact_provision_resolution=True,
                requires_legalai_v2=True,
                legal_intent_confidence=0.98,
                target_act=matched_statute_acts[0] if matched_statute_acts else None,
                target_provision=matched_statute_provisions[0] if matched_statute_provisions else None
            )

        # ---------------------------------------------------------------------
        # STEP 8: Handle General Legal Concepts (LEGAL_QUERY)
        # Substantive offences, procedural remedies, civil rights (negligence, bail, etc.)
        # Even without the literal word 'legal' or 'law'.
        # ---------------------------------------------------------------------
        if has_legal_concept:
            all_matches = matched_statute_acts + matched_legal_concepts
            return QueryDecision(
                intent=QueryIntent.LEGAL_QUERY,
                confidence=0.95,
                reason="Query addresses a substantive legal concept or procedural remedy under Indian law.",
                sub_intent="LEGAL_CONCEPT",
                matched_patterns=all_matches,
                entities=entities,
                requires_case_context=False,
                requires_case_documents=False,
                requires_case_metadata=False,
                requires_legal_rag=True,
                requires_legalai_v2=True,
                legal_intent_confidence=0.95
            )

        # ---------------------------------------------------------------------
        # STEP 9: Clearly Out of Scope Non-Legal Inquiries
        # Coding, sports, movies, recipes, shopping, general trivia.
        # Strict Rule: Never send to Legal RAG, never send to Case RAG.
        # ---------------------------------------------------------------------
        if matched_out_of_scope:
            return QueryDecision(
                intent=QueryIntent.OUT_OF_SCOPE,
                confidence=0.98,
                reason="Query is outside the legal and supported AI assistant scope (coding, sports, entertainment, recipes).",
                sub_intent="NON_LEGAL_OUT_OF_SCOPE",
                matched_patterns=matched_out_of_scope,
                entities=entities,
                requires_case_context=False,
                requires_case_documents=False,
                requires_case_metadata=False,
                requires_legal_rag=False,
                requires_base_qwen=False
            )

        # ---------------------------------------------------------------------
        # STEP 10: Pure Conversational Greetings & Courtesies
        # ---------------------------------------------------------------------
        if matched_conv:
            return QueryDecision(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=0.98,
                reason="Message is an ordinary conversational greeting, courtesy, gratitude, or pleasantry.",
                sub_intent="GREETING",
                matched_patterns=matched_conv,
                entities=entities,
                requires_case_context=False,
                requires_case_documents=False,
                requires_case_metadata=False,
                requires_legal_rag=False,
                requires_base_qwen=False
            )

        # ---------------------------------------------------------------------
        # STEP 11: Anaphoric Context History Resolution
        # ONLY consulted when the query contains an explicit anaphoric pointer
        # (e.g. "what about that?", "for odd or even", "what about the previous one?", "can you make it shorter?")
        # AND lacks an independent substantive entity.
        # ---------------------------------------------------------------------
        is_anaphoric = any(r.match(cleaned) for r in self._anaphoric_regexes)
        if is_anaphoric and conversation_history and len(conversation_history) > 0:
            last_turn = None
            for turn in reversed(conversation_history):
                q_type = str(turn.get("query_type", "")).upper()
                if q_type:
                    last_turn = q_type
                    break
            
            if last_turn:
                if last_turn in ("OUT_OF_SCOPE", "GENERAL_NON_LEGAL"):
                    return QueryDecision(
                        intent=QueryIntent.OUT_OF_SCOPE,
                        confidence=0.95,
                        reason="Anaphoric follow-up continues previous out-of-scope inquiry.",
                        sub_intent="CONTEXT_FOLLOW_UP",
                        matched_patterns=["ANAPHORIC_OUT_OF_SCOPE"],
                        entities=entities
                    )
                elif last_turn in ("EXACT_PROVISION_QUERY", "LEGAL_QUERY"):
                    return QueryDecision(
                        intent=QueryIntent.LEGAL_QUERY,
                        confidence=0.90,
                        reason="Anaphoric follow-up continues previous legal inquiry.",
                        sub_intent="CONTEXT_FOLLOW_UP",
                        matched_patterns=["ANAPHORIC_LEGAL"],
                        entities=entities,
                        requires_legal_rag=True,
                        requires_legalai_v2=True,
                        legal_intent_confidence=0.90
                    )
                elif last_turn in ("CASE_QUERY", "HEARING_PREPARATION"):
                    return QueryDecision(
                        intent=QueryIntent.CASE_QUERY,
                        confidence=0.90,
                        reason="Anaphoric follow-up continues previous case inquiry.",
                        sub_intent="CONTEXT_FOLLOW_UP",
                        matched_patterns=["ANAPHORIC_CASE"],
                        entities=entities,
                        requires_case_context=True,
                        requires_case_documents=True,
                        requires_case_analysis_v1=True,
                        case_intent_confidence=0.90,
                        case_id=case_id
                    )

        # ---------------------------------------------------------------------
        # STEP 12: Fail-Closed Ambiguous Fallback
        # If an inquiry has no identifiable anchors, is not anaphoric, and is not conversational:
        # Ask for clarification. NEVER blindly invoke General Legal RAG or Case RAG.
        # ---------------------------------------------------------------------
        return QueryDecision(
            intent=QueryIntent.AMBIGUOUS,
            confidence=0.85,
            reason="Query lacks identifiable legal, case, system, or technical anchors. Clarification requested.",
            sub_intent="CLARIFICATION_REQUIRED",
            matched_patterns=["AMBIGUOUS_NO_ANCHOR"],
            entities=entities,
            requires_case_context=False,
            requires_case_documents=False,
            requires_case_metadata=False,
            requires_legal_rag=False
        )


# Global singleton router instance
_GLOBAL_ROUTER: Optional[UniversalQueryRouter] = None


def get_query_router() -> UniversalQueryRouter:
    """Returns the singleton UniversalQueryRouter instance."""
    global _GLOBAL_ROUTER
    if _GLOBAL_ROUTER is None:
        _GLOBAL_ROUTER = UniversalQueryRouter()
    return _GLOBAL_ROUTER


# Backward-compatibility alias
QueryRouter = UniversalQueryRouter
