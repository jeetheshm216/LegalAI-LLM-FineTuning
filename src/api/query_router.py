"""
src/api/query_router.py

Lightweight, deterministic query router for LegalAI.
Classifies user incoming messages into:
  - CONVERSATIONAL: pure greetings, gratitude, assistant identity, capabilities, courteous banter.
  - LEGAL_QUERY: statutory questions, legal definitions, offences, penalties, procedures,
                 including both in-corpus (BNS, BNSS, BSA, IT Act, Companies Act, etc.) and
                 state/central or out-of-corpus legal statutes as well as legal practice.
  - CASE_QUERY: matter-specific inquiries, evidence analysis, judgment analysis, FIR review,
                case documents, client/opposing counsel questions.
  - OUT_OF_SCOPE: strictly non-legal knowledge questions (programming, movies, sports, recipes,
                  general trivia, tech shopping, etc.) that must receive a friendly scope boundary.
  - AMBIGUOUS: isolated cryptic tokens, fragments, or demonstrative queries without context.

CRITICAL SAFETY & ROUTING PRINCIPLES:
1. Explicit legal provisions and statutory intent ALWAYS override casual greeting prefixes.
   (e.g., "Hey, what is Section 103 BNS?" -> LEGAL_QUERY; "Hello, analyze my FIR" -> CASE_QUERY).
2. All Indian statutory queries (Central Acts, State Acts, unindexed Acts, cybercrime scenarios)
   must route to LEGAL_QUERY for authoritative corpus lookup or professional safe abstention.
   They must NEVER be rejected as OUT_OF_SCOPE merely because an Act is not locally indexed.
3. Conversational capability inquiries ("what can you do for me", "what are the things you can able to do fro me")
   must route strictly to CONVERSATIONAL with retrieval_mode=NONE and qwen_invoked=False.
4. Uncertain does NOT automatically mean LEGAL_QUERY. Positive evidence of legal intent (legal anchor)
   is required before General Legal RAG is invoked.
5. Inquiries lacking legal/case anchors that are not out-of-scope or conversational route to AMBIGUOUS.
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class QueryIntent(str, Enum):
    CONVERSATIONAL = "CONVERSATIONAL"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    GENERAL_NON_LEGAL = "OUT_OF_SCOPE"  # Backward-compatibility alias
    LEGAL_QUERY = "LEGAL_QUERY"
    CASE_QUERY = "CASE_QUERY"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass
class RoutingResult:
    intent: QueryIntent
    confidence: float
    reason: str
    matched_patterns: List[str]
    sub_intent: Optional[str] = None
    legal_intent_confidence: float = 0.0
    case_intent_confidence: float = 0.0


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
        r'\b(?:what\s+)?evidence\s+(?:is\s+)?missing(?:\s+in\s+my\s+case)?\b',
        r'\bwhat\s+evidence\s+do\s+we\s+have\b',
        r'\bwhat\s+contradictions\s+exist\b',
        r'\bprepare\s+(?:me|us)\s+for\s+(?:the\s+)?(?:next\s+)?hearing\b',
        r'\bwhat\s+should\s+i\s+prepare\s+for\s+(?:the\s+)?(?:next\s+)?hearing\b',
        r'\bwhat\s+documents\s+support\s+(?:the\s+)?allegation\b',
        r'\b(?:last|next)\s+hearing\b',
        r'\bwhat\s+happened\s+(?:at|in)\s+(?:the\s+last\s+hearing|my\s+case|this\s+case)\b',
        r'\bkey\s+facts\s+(?:in|of)\s+(?:this|my|the)\s+(?:case|matter|judgment|judgement)\b',
        r'\bwhat\s+are\s+the\s+key\s+points\s+in\s+this\s+case\b',
        r'\bevidence\s+supports\s+our\s+(?:position|case|argument)\b',
        r'\bwhat\s+evidence\s+supports\b',
        r'\bsummarize\s+this\s+case\b',
    ]

    # -------------------------------------------------------------------------
    # 2. LEGAL_QUERY PATTERNS (LEGAL ANCHORS)
    # Statutory sections, acts, penal provisions, procedural rights, legal terms,
    # cybercrime concepts, state and central enactments.
    # -------------------------------------------------------------------------
    STATUTE_SECTION_PATTERNS = [
        r'\b(?:section|sec\.?|s\.?|u/s|\u00a7|provision)\s*[0-9]+[A-Za-z]*\b',
        r'\barticle\s+[0-9]+[A-Za-z]*\b',
        r'\border\s+[0-9IVXLCDM]+\s+(?:rule\s+[0-9]+)?\b',
        r'\bclause\s+[0-9]+(?:\([a-z0-9]+\))*\b',
        r'\bschedule\s+[0-9IVXLCDM]+\b',
        r'\bact\s+[0-9]+[A-Za-z]*\b',  # Provision-like syntax such as 'act 49A'
    ]

    ACT_NAME_PATTERNS = [
        # Core criminal enactments
        r'\b(?:bns|bnss|bsa)\b',
        r'\bbharatiya\s+nyaya\s+sanhita(?:\s*,?\s*2023)?\b',
        r'\bbharatiya\s+nagarik\s+suraksha\s+sanhita(?:\s*,?\s*2023)?\b',
        r'\bbharatiya\s+sakshya\s+adhiniyam(?:\s*,?\s*2023)?\b',
        r'\b(?:ipc|crpc|iea)\b',
        r'\bindian\s+penal\s+code\b',
        r'\bcode\s+of\s+criminal\s+procedure\b',
        r'\b(?:indian\s+)?evidence\s+act\b',
        # Major statutory domains
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
        r'\bfamily\s+courts?\s+act\b',
        r'\bhindu\s+marriage\s+act\b',
        r'\bspecific\s+relief\s+act\b',
        r'\bgst\s+act\b',
        r'\bincome\s+tax\s+act\b',
        r'\blabour\s+laws?\b',
        r'\bcivil\s+procedure\s+code\b',
        r'\bcpc\b',
        # Structural statutory enactments (Central and State Acts, Codes, Rules, Ordinances)
        r'\b(?!(?:act\s+of\s+god|caught\s+in\s+the\s+act|act\s+as|act\s+upon|to\s+act|second\s+act|final\s+act)\b)(?:[A-Z][a-zA-Z0-9\s,\-\'\&]{1,60}?)\s+Act(?:\s*,?\s*(?:18|19|20)[0-9]{2})?\b',
        r'\b(?!(?:act\s+of\s+god|caught\s+in\s+the\s+act|act\s+as|act\s+upon|to\s+act)\b)(?:[a-zA-Z0-9\s,\-\'\&]{2,60}?)\s+Act,\s*(?:18|19|20)[0-9]{2}\b',
        r'\b[A-Za-z\s]+(?:Sanhita|Adhiniyam|Ordinance)(?:\s*,?\s*(?:18|19|20)[0-9]{2})?\b',
        r'\b(?:civil|criminal|penal|procedure|evidence|insolvency|arbitration|bankruptcy)\s+code\b',
        r'\b(?:what\s+is\s+an\s+act|what\s+is\s+the\s+act\s+number|act\s+number)\b',
        r'\bwhat\s+does\s+.*?provide\b',
        r'\bwhat\s+law\s+applies\b',
    ]

    SUBSTANTIVE_LEGAL_TERMS = [
        # Offences & Penal Concepts
        r'\bmurder\b',
        r'\bculpable\s+homicide\b',
        r'\bpunishment(?:\s+applies)?\b',
        r'\bpunishment\s+for\s+[a-z\s]+\b',
        r'\b(?:what\s+)?evidence\s+(?:is\s+)?(?:required|needed|relevant)\b',
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
        # Professional legal workflows
        r'\bbail\s+application\b',
        r'\blegal\s+notice\b',
        r'\bstructure\s+of\s+a\s+legal\s+notice\b',
        r'\bcivil\s+and\s+criminal\s+proceedings\b',
        r'\bpower\s+of\s+attorney\b',
        r'\bvakalatnama\b',
        r'\bwritten\s+statement\b',
        r'\baffidavit\b',
        r'\bpleadings?\b',
        r'\blegal\s+research\b',
        r'\bstatutory\s+provisions?\b',
        # Judicial precedents & court authorities
        r'\bsupreme\s+court\b',
        r'\bhigh\s+court\b',
        r'\bprecedent\b',
        r'\bjudicial\s+precedent\b',
        r'\bjudgments?\b',
        r'\bruling\b',
        r'\bratio\s+decidendi\b',
        r'\bobiter\s+dicta\b',
        r'\bcase\s+law\b',
        r'\barjun\s+panditrao\b',
        r'\bshreya\s+singhal\b',
        r'\b65b(?:\s+certificate)?\b',
        # Cybercrime, Digital & Financial Offences
        r'\b(?:upi|bhim|paytm|google\s*pay|phonepe|net\s*banking|debit\s*card|credit\s*card|pin|otp)\b',
        r'\b(?:credentials?|credentials?\s+stolen|stole(?:n)?(?:\s+my)?\s+credentials?)\b',
        r'\b(?:phishing|spoofing|cyber\s*(?:crime|fraud|attack|security|stalking|bullying)|identity\s+theft)\b',
        r'\b(?:unauthorized\s+transaction|financial\s+fraud|online\s+fraud|banking\s+fraud|wire\s+fraud)\b',
        r'\b(?:hacking|hacked|ransomware|malware|deepfake|sim\s+swap|trojan|data\s+breach)\b',
        r'\bwhat\s+(?:indian\s+)?legal\s+provisions?\s+(?:may\s+)?apply\b',
        r'\bwhat\s+provisions?\s+apply\b',
        r'\bwhat\s+law\s+applies\s+to\b',
        r'\blegal\s+provisions?\b',
        r'\bapplicable\s+laws?\b',
    ]

    # -------------------------------------------------------------------------
    # 3. OUT_OF_SCOPE PATTERNS
    # Non-legal queries: programming, movies, sports, tech shopping, recipes,
    # math, general science, trivia.
    # -------------------------------------------------------------------------
    OUT_OF_SCOPE_PATTERNS = [
        # Programming & software development
        r'\b(?:python|c\+\+|c#|java|javascript|typescript|ruby|golang|rust|html|css|sql|bash|powershell|php)\b',
        r'\b(?:write|give\s+me|generate|create|show)\s+(?:a\s+)?(?:python|c\+\+|java|javascript|c#|code|script|program|function|algorithm)\b',
        r'\b(?:c\+\+\s+code|python\s+code|write\s+code|code\s+for|odd\s+or\s+even|for\s+odd\s+or\s+even|odd\s+even)\b',
        r'\bwhat\s+is\s+(?:python|javascript|typescript|java|c\+\+|html|css|git|docker|kubernetes|linux)\b',
        r'\bhow\s+to\s+(?:code|program|compile|debug|install|deploy|run|build)\b',
        r'\b(?:sort\s+a\s+list|binary\s+search|linked\s+list|data\s+structure|recursion|bubble\s+sort|quick\s+sort)\b',
        r'\b(?:machine\s+learning|deep\s+learning|neural\s+network|artificial\s+intelligence|llm|nlp|data\s+science)\b',
        r'\bexplain\s+(?:recursion|polymorphism|pointers|sorting|algorithms?)\b',
        # Entertainment, movies, actors, cinema, music, celebrities
        r'\b(?:vijay|rajinikanth|ajith|kamal\s+haasan|shah\s+rukh|salman\s+khan|aamir\s+khan|deepika|alia\s+bhatt)\b',
        r'\b(?:last|latest|new|next|upcoming|recent)\s+(?:[a-z]+\s+)?(?:movie|film|cinema)\b',
        r'\b(?:movie|movies|film|films|cinema|trailer|box\s+office|song|songs|music|album|album\s+songs?)\b',
        r'\b(?:recommend|suggest)\s+.*?\b(?:movie|movies|film|films|series|show|shows|song|songs|music)\b',
        r'\b(?:actor|actress|bollywood|hollywood|kollywood|tollywood|director|hero|heroine|celebrity)\b',
        # Sports
        r'\b(?:cricket|football|soccer|ipl|fifa|tennis|badminton|chess|world\s+cup|match\s+score)\b',
        r'\bwho\s+won\s+.*?\b(?:match|game|tournament|cup|trophy)\b',
        r'\b(?:virat\s+kohli|rohit\s+sharma|dhoni|messi|ronaldo)\b',
        # Cooking, food, recipes
        r'\bhow\s+do\s+i\s+cook\b',
        r'\b(?:recipe|recipes|biryani|pizza|burger|pasta|curry|cook|cooking|bake|baking|restaurant)\b',
        # Shopping & consumer tech
        r'\b(?:what|which)\s+laptop\s+should\s+i\s+buy\b',
        r'\b(?:best|recommend)\s+(?:laptop|phone|smartphone|camera|headphones|car|bike)\b',
        r'\b(?:iphone|macbook|dell|lenovo|asus|samsung\s+galaxy)\b',
        # Math & calculations
        r'\b(?:calculate|compute|solve\s+math|equation)\b',
        r'^\s*[-+]?[0-9]+(?:\.[0-9]+)?\s*[\+\-\*\/\^]\s*[-+]?[0-9]+(?:\.[0-9]+)?(?:\s*[\+\-\*\/\^]\s*[-+]?[0-9]+(?:\.[0-9]+)?)*\s*$',
        # General world trivia / geography / science
        r'\bwhat\s+is\s+the\s+capital\s+of\b',
        r'\bwho\s+is\s+the\s+(?:president|prime\s+minister|king|queen)\s+of\b',
        r'\b(?:weather\s+in|weather\s+today|temperature\s+in)\b',
        r'\b(?:photosynthesis|quantum\s+physics|gravity|solar\s+system|speed\s+of\s+light)\b',
        r'\b(?:travel\s+to|trip\s+to|flight\s+to|hotel\s+in|vacation\s+in|tourism)\b',
        r'\btell\s+me\s+a\s+joke\b',
        r'\b(?:hello\s+world|c\+\+\s+hello\s+world)\b',
        r'\b(?:cricket\s+result|match\s+result|cricket\s+score)\b',
        r'\b(?:laptop\s+recommendation|recommend\s+(?:a\s+)?laptop)\b',
    ]

    # -------------------------------------------------------------------------
    # 4. CAPABILITY INQUIRY PATTERNS
    # System capabilities, user guidance, what questions can be asked, features.
    # Must route to CONVERSATIONAL with retrieval_mode=NONE and qwen_invoked=FALSE.
    # -------------------------------------------------------------------------
    CAPABILITY_PATTERNS = [
        # Natural capability inquiries with typo & variation tolerance
        r'\bwhat\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?(?:things\s+)?(?:you\s+can\s+(?:be\s+)?able\s+to\s+do|can\s+you\s+do|are\s+you\s+able\s+to\s+do|do\s+you\s+do)(?:\s+(?:for|fro)\s+me)?\b',
        r'\bwhat\s+are\s+the\s+things\s+you\s+can\s+.*?\b',
        r'\bwhat\s+can\s+you\s+do(?:\s+(?:for|fro)\s+me)?\b',
        r'\bwhat\s+are\s+you\s+able\s+to\s+do\b',
        r'\bwhat\s+are\s+you\s+capable\s+of\b',
        r'\bwhat\s+can\s+you\s+help\s+(?:me\s+)?with\b',
        r'\bhow\s+can\s+you\s+help(?:\s+me)?\b',
        r'\bwhat\s+can\s+i\s+ask(?:\s+you)?\b',
        r'\bwhat\s+kinds?\s+of\s+questions?\s+can\s+i\s+ask\b',
        r'\bwhat\s+services?\s+do\s+you\s+provide\b',
        r'\bwhat\s+are\s+your\s+(?:capabilities|features)\b',
        r'\btell\s+me\s+what\s+you\s+can\s+do\b',
        r'\bwhat\s+can\s+i\s+use\s+you\s+for\b',
        r'\bwhat\s+do\s+you\s+help\s+with\b',
        r'\bhow\s+can\s+i\s+use\s+(?:you|legalai)\b',
        r'\bwhat\s+can\s+legalai\s+do\b',
        r'\bwhat\s+does\s+legalai\s+do\b',
        r'\bwhat\s+all\s+can\s+you\s+do\b',
        r'\bwhat\s+are\s+you\s+doing\b',
        r'\bhow\s+to\s+use\s+(?:you|legalai)\b',
        r'\bexplain\s+your\s+capabilities\b',
    ]

    # -------------------------------------------------------------------------
    # 5. CONVERSATIONAL PATTERNS
    # Greetings, gratitude, assistant identity, courteous chatter, pleasantries.
    # -------------------------------------------------------------------------
    CONVERSATIONAL_GREETINGS = [
        r'^(?:hi|hello|hey|hiya|howdy|good\s+(?:morning|afternoon|evening|day)|greetings)(?:[\s,!.]+)?$',
        r'^(?:hey|hi|hello)\s+(?:hi|hey|hello|there|legalai|assistant|again)(?:[\s,!.]+)?$',
        r'^(?:hi|hello|hey|hiya|howdy)[,\s]+.*?(?:how\s+are\s+you|how\'s\s+it\s+going|what\'s\s+up|how\s+are\s+you\s+doing)(?:[\s,?!.]+)?$',
        r'^(?:good\s+(?:morning|afternoon|evening|day))[,\s]+(?:how\s+are\s+you(?:\s+doing)?|legalai|assistant|there)(?:[\s,?!.]+)?$',
    ]

    CONVERSATIONAL_GRATITUDE = [
        r'^(?:thanks|thank\s+you|thank\s+you\s+(?:so\s+much|very\s+much)|many\s+thanks|appreciate\s+it|thx)(?:[\s,!.]+)?$',
        r'^(?:thanks|thank\s+you)[,\s]+(?:legalai|for\s+(?:your\s+help|the\s+help|helping|explaining))(?:[\s,!.]+)?$',
        r'^(?:ok\s+thanks|okay\s+thanks|great\s+thanks|thanks\s+for\s+helping)(?:[\s,!.]+)?$',
    ]

    CONVERSATIONAL_IDENTITY = [
        r'^(?:who\s+are\s+you|what\s+are\s+you|what\s+is\s+your\s+name|are\s+you\s+an?\s+ai)(?:[\s,?!.]+)?$',
        r'^(?:tell\s+me\s+about\s+(?:yourself|legalai)|introduce\s+yourself)(?:[\s,?!.]+)?$',
        r'^(?:help|help\s+me|can\s+you\s+help\s+me|i\s+need\s+(?:some\s+)?help|hey\s+can\s+you\s+help\s+me)(?:[\s,?!.]+)?$',
    ]

    CONVERSATIONAL_SMALLTALK = [
        r'^(?:how\s+are\s+you|how\s+are\s+you\s+doing|how\'s\s+it\s+going(?:\s+today)?|how\s+do\s+you\s+do)(?:[\s,?!.]+)?$',
        r'^(?:nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)(?:[\s,!.]+)?$',
        r'^(?:ok|okay|got\s+it|understood|cool|great|awesome|perfect|sure|alright|fine|nice)(?:[\s,!.]+)?$',
        r'^(?:bye|goodbye|see\s+you|have\s+a\s+(?:nice|good)\s+day)(?:[\s,!.]+)?$',
    ]

    # Emotional, frustration, interpersonal messages (treated as CONVERSATIONAL social interaction)
    CONVERSATIONAL_INTERPERSONAL = [
        r'\b(?:fuck\s+(?:you|off)|fuck|screw\s+you|damn(?:\s+it)?|what\s+the\s+(?:hell|fuck)|you\s+(?:suck|are\s+useless|are\s+stupid|are\s+dumb|are\s+an?\s+idiot)|this\s+is\s+(?:stupid|dumb|useless|nonsense|crap|shit)|shut\s+up|bitch|bastard|asshole|idiot|you\'?re\s+(?:useless|stupid|dumb|annoying|terrible|bad|wrong))\b',
        r'^(?:fuck\s+you|screw\s+you|you\s+suck|you\'?re\s+useless|this\s+is\s+stupid|damn|what\s+the\s+hell)(?:[\s,?!.]+)?$',
    ]

    CONVERSATIONAL_TOKENS = {
        "hi", "hello", "hey", "hiya", "howdy", "greetings", "there",
        "morning", "afternoon", "evening", "day", "good", "today",
        "thanks", "thank", "you", "thx", "appreciate", "helping",
        "ok", "okay", "cool", "great", "awesome", "perfect", "sure", "alright", "fine", "nice",
        "yes", "no", "yep", "nope", "bye", "goodbye",
        "how", "are", "doing", "going", "do", "can", "help", "me", "what", "is", "your",
        "tell", "about", "yourself", "assist", "assistance", "please", "i", "need", "some", "a",
        "it", "its", "am", "well", "fine", "fro", "for", "things", "able", "capabilities",
        "features", "services", "provide"
    }

    # -------------------------------------------------------------------------
    # 6. AMBIGUOUS PATTERNS
    # Unclear, incomplete, isolated tokens or demonstratives lacking context
    # -------------------------------------------------------------------------
    AMBIGUOUS_PATTERNS = [
        r'^(?:what\s+about\s+(?:that|this|that\s+one|it)|explain\s+(?:that|this|it)|tell\s+me\s+(?:more\s+about\s+that|about\s+it)|and\s+(?:that|then)|how\s+about\s+that)(?:[\s,?!.]+)?$',
        r'^(?:tell\s+me\s+about\s+this|what\s+about\s+this\s+section|what\s+about\s+this\s+act|what\s+about\s+this)(?:[\s,?!.]+)?$',
        r'^(?:49p|xyz|abc|foo|bar|test|123|qwe|asdf)(?:[\s,?!.]+)?$',
    ]

    def __init__(self):
        self._case_regexes = [re.compile(p, re.IGNORECASE) for p in self.CASE_MATTER_PATTERNS]
        self._statute_regexes = [re.compile(p, re.IGNORECASE) for p in self.STATUTE_SECTION_PATTERNS]
        self._act_regexes = [re.compile(p, re.IGNORECASE) for p in self.ACT_NAME_PATTERNS]
        self._legal_term_regexes = [re.compile(p, re.IGNORECASE) for p in self.SUBSTANTIVE_LEGAL_TERMS]
        self._out_of_scope_regexes = [re.compile(p, re.IGNORECASE) for p in self.OUT_OF_SCOPE_PATTERNS]
        self._capability_regexes = [re.compile(p, re.IGNORECASE) for p in self.CAPABILITY_PATTERNS]
        self._ambiguous_regexes = [re.compile(p, re.IGNORECASE) for p in self.AMBIGUOUS_PATTERNS]

        self._conv_regexes = [
            re.compile(p, re.IGNORECASE) for p in (
                self.CONVERSATIONAL_GREETINGS +
                self.CONVERSATIONAL_GRATITUDE +
                self.CONVERSATIONAL_IDENTITY +
                self.CONVERSATIONAL_SMALLTALK +
                self.CONVERSATIONAL_INTERPERSONAL
            )
        ]

    def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> RoutingResult:
        """
        Deterministically classifies incoming message into:
        - CONVERSATIONAL
        - LEGAL_QUERY
        - CASE_QUERY
        - OUT_OF_SCOPE
        - AMBIGUOUS

        Strict Architectural Principles:
        1. Capability queries ("what are the things you can able to do fro me") route to CONVERSATIONAL.
        2. Legal anchors (provision identifiers, enactments, substantive penal/civil concepts)
           are REQUIRED before routing to LEGAL_QUERY. Generic words ("case", "law", "document", "issue")
           do NOT qualify as legal anchors alone.
        3. Explicit legal intent overrides casual conversational framing ("Hi, what is Section 66C?").
        4. Out-of-scope non-legal queries route to OUT_OF_SCOPE.
        5. Queries lacking legal anchors, case context, and conversational intent route to AMBIGUOUS.
           Uncertain does NOT mean LEGAL_QUERY.
        """
        cleaned = message.strip()
        if not cleaned:
            return RoutingResult(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=1.0,
                reason="Empty or whitespace query treated as conversational prompt.",
                matched_patterns=["EMPTY_QUERY"],
                sub_intent="GREETING",
                legal_intent_confidence=0.0,
                case_intent_confidence=0.0
            )

        # ---------------------------------------------------------------------
        # STEP 1: Scan for anchors
        # ---------------------------------------------------------------------
        matched_case = [m.group(0) for r in self._case_regexes if (m := r.search(cleaned))]
        
        matched_statute_provisions = [m.group(0) for r in self._statute_regexes if (m := r.search(cleaned))]
        matched_statute_acts = [m.group(0) for r in self._act_regexes if (m := r.search(cleaned))]
        matched_substantive_terms = [m.group(0) for r in self._legal_term_regexes if (m := r.search(cleaned))]
        
        has_legal_anchor = bool(matched_statute_provisions or matched_statute_acts or matched_substantive_terms)
        all_legal_matches = matched_statute_provisions + matched_statute_acts + matched_substantive_terms

        matched_capability = [m.group(0) for r in self._capability_regexes if (m := r.search(cleaned))]
        matched_out_of_scope = [m.group(0) for r in self._out_of_scope_regexes if (m := r.search(cleaned))]

        # Token-based capability fallback check (handles word salad and typo variations)
        is_capability = bool(matched_capability)
        if not is_capability:
            lower = cleaned.lower()
            if ("what" in lower or "how" in lower or "tell" in lower) and \
               ("you" in lower or "legalai" in lower) and \
               ("do" in lower or "help" in lower or "assist" in lower or "capabilities" in lower or "features" in lower or "able" in lower or "ask" in lower):
                is_capability = True
                matched_capability = ["CAPABILITY_TOKEN_COMBINATION"]

        # ---------------------------------------------------------------------
        # STEP 2: Handle Capability Inquiries
        # "What can you do for me", "what are the things you can able to do fro me"
        # Capability inquiry overrides generic words ("legalai", "law", "questions").
        # Only explicit statutory provisions or active case references override capability.
        # ---------------------------------------------------------------------
        if is_capability:
            # Check if there is an explicit provision or specific Act reference
            # e.g., "What can you do regarding Section 66C IT Act?" -> LEGAL_QUERY
            if matched_statute_provisions or (matched_statute_acts and not any(p in ("what is an act", "act number") for p in matched_statute_acts)):
                return RoutingResult(
                    intent=QueryIntent.LEGAL_QUERY,
                    confidence=0.95,
                    reason="Capability inquiry combined with explicit statutory provision or enactment.",
                    matched_patterns=all_legal_matches,
                    sub_intent="LEGAL_CAPABILITY",
                    legal_intent_confidence=0.95,
                    case_intent_confidence=0.0
                )
            # Check if there is a specific case anchor
            if matched_case:
                return RoutingResult(
                    intent=QueryIntent.CASE_QUERY,
                    confidence=0.95,
                    reason="Capability inquiry addressed to specific case matter or documents.",
                    matched_patterns=matched_case,
                    sub_intent="CASE_CAPABILITY",
                    legal_intent_confidence=0.0,
                    case_intent_confidence=0.95
                )
            # Pure capability inquiry -> CONVERSATIONAL with zero retrieval
            return RoutingResult(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=0.98,
                reason="Query is a natural capability inquiry asking what the assistant can do.",
                matched_patterns=matched_capability or ["CAPABILITY_INQUIRY"],
                sub_intent="CAPABILITY_INQUIRY",
                legal_intent_confidence=0.0,
                case_intent_confidence=0.0
            )

        # ---------------------------------------------------------------------
        # STEP 3: PRIORITY 1 — Specific Case / Matter Inquiry
        # ---------------------------------------------------------------------
        if matched_case:
            return RoutingResult(
                intent=QueryIntent.CASE_QUERY,
                confidence=0.98,
                reason="Query addresses specific case matter, client position, or evidentiary documents.",
                matched_patterns=matched_case,
                sub_intent="CASE_MATTER",
                legal_intent_confidence=0.0,
                case_intent_confidence=0.98
            )

        # ---------------------------------------------------------------------
        # STEP 4: PRIORITY 2 — Explicit Legal / Statutory Anchors
        # Requires verified legal anchor: section, Act, or substantive legal concept.
        # This strictly overrides general greetings (e.g. "Hi, what is Section 103 BNS?").
        # ---------------------------------------------------------------------
        if has_legal_anchor:
            sub_intent = "EXACT_PROVISION" if matched_statute_provisions else ("ACT_QUERY" if matched_statute_acts else "SUBSTANTIVE_LEGAL")
            return RoutingResult(
                intent=QueryIntent.LEGAL_QUERY,
                confidence=0.98,
                reason="Query contains verified legal anchors (statutory citations, enactments, or substantive legal concepts).",
                matched_patterns=all_legal_matches,
                sub_intent=sub_intent,
                legal_intent_confidence=0.98,
                case_intent_confidence=0.0
            )

        # ---------------------------------------------------------------------
        # STEP 5: PRIORITY 3 — Clearly Out of Scope Non-Legal Inquiries
        # Coding, movies, sports, tech shopping, recipes, general trivia
        # ---------------------------------------------------------------------
        if matched_out_of_scope:
            return RoutingResult(
                intent=QueryIntent.OUT_OF_SCOPE,
                confidence=0.98,
                reason="Query is outside the legal domain (programming, entertainment, sports, or general trivia).",
                matched_patterns=matched_out_of_scope,
                sub_intent="NON_LEGAL_OUT_OF_SCOPE",
                legal_intent_confidence=0.0,
                case_intent_confidence=0.0
            )

        # ---------------------------------------------------------------------
        # STEP 6: PRIORITY 4 — Pure Conversational Greetings & Courtesies
        # ---------------------------------------------------------------------
        for r in self._conv_regexes:
            m = r.match(cleaned)
            if m:
                return RoutingResult(
                    intent=QueryIntent.CONVERSATIONAL,
                    confidence=0.95,
                    reason="Message is an ordinary conversational greeting, capability inquiry, or gratitude.",
                    matched_patterns=[m.group(0)],
                    sub_intent="GREETING",
                    legal_intent_confidence=0.0,
                    case_intent_confidence=0.0
                )

        # Word-level conversational check for flexible greetings
        tokens = re.findall(r'[a-zA-Z]+', cleaned.lower())
        if tokens and len(tokens) <= 12 and all(t in self.CONVERSATIONAL_TOKENS for t in tokens):
            return RoutingResult(
                intent=QueryIntent.CONVERSATIONAL,
                confidence=0.95,
                reason="All tokens in message match conversational vocabulary.",
                matched_patterns=["CONVERSATIONAL_TOKENS"],
                sub_intent="CONVERSATIONAL_TOKENS",
                legal_intent_confidence=0.0,
                case_intent_confidence=0.0
            )

        # ---------------------------------------------------------------------
        # STEP 7: PRIORITY 5 — Conversation Context Follow-Up
        # ---------------------------------------------------------------------
        if conversation_history and len(conversation_history) > 0:
            last_substantive_intent = None
            for turn in reversed(conversation_history):
                content = str(turn.get("content", "")).lower()
                q_type = str(turn.get("query_type", "")).upper()
                if q_type in ("OUT_OF_SCOPE", "GENERAL_NON_LEGAL"):
                    last_substantive_intent = QueryIntent.OUT_OF_SCOPE
                    break
                elif q_type == "LEGAL_QUERY":
                    last_substantive_intent = QueryIntent.LEGAL_QUERY
                    break
                elif q_type == "CASE_QUERY":
                    last_substantive_intent = QueryIntent.CASE_QUERY
                    break
                elif turn.get("role") == "user":
                    if any(term in content for term in ["python", "code", "c++", "movie", "film", "vijay", "cricket", "recipe"]):
                        last_substantive_intent = QueryIntent.OUT_OF_SCOPE
                        break
                    elif any(term in content for term in ["section", "bns", "bnss", "bsa", "act", "offence", "bail", "law"]):
                        last_substantive_intent = QueryIntent.LEGAL_QUERY
                        break
                    elif any(term in content for term in ["case", "matter", "evidence", "witness", "fir", "hearing"]):
                        last_substantive_intent = QueryIntent.CASE_QUERY
                        break

            if len(cleaned.split()) <= 12 and last_substantive_intent:
                if last_substantive_intent == QueryIntent.OUT_OF_SCOPE:
                    return RoutingResult(
                        intent=QueryIntent.OUT_OF_SCOPE,
                        confidence=0.90,
                        reason="Contextual follow-up continues previous out-of-scope non-legal inquiry.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_OUT_OF_SCOPE"],
                        sub_intent="CONTEXT_FOLLOW_UP",
                        legal_intent_confidence=0.0,
                        case_intent_confidence=0.0
                    )
                elif last_substantive_intent == QueryIntent.LEGAL_QUERY:
                    return RoutingResult(
                        intent=QueryIntent.LEGAL_QUERY,
                        confidence=0.90,
                        reason="Contextual follow-up to previous statutory legal query.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_LEGAL"],
                        sub_intent="CONTEXT_FOLLOW_UP",
                        legal_intent_confidence=0.90,
                        case_intent_confidence=0.0
                    )
                elif last_substantive_intent == QueryIntent.CASE_QUERY:
                    return RoutingResult(
                        intent=QueryIntent.CASE_QUERY,
                        confidence=0.90,
                        reason="Contextual follow-up to previous case inquiry.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_CASE"],
                        sub_intent="CONTEXT_FOLLOW_UP",
                        legal_intent_confidence=0.0,
                        case_intent_confidence=0.90
                    )

        # ---------------------------------------------------------------------
        # STEP 8: PRIORITY 6 — Ambiguous Query Detection
        # Explicit ambiguous demonstratives: "tell me about this", "what about this section?", "explain this"
        # ---------------------------------------------------------------------
        for r in self._ambiguous_regexes:
            m = r.match(cleaned)
            if m:
                return RoutingResult(
                    intent=QueryIntent.AMBIGUOUS,
                    confidence=0.95,
                    reason="Query is demonstrative, cryptic, or incomplete without identifiable context.",
                    matched_patterns=[m.group(0)],
                    sub_intent="AMBIGUOUS_DEMONSTRATIVE",
                    legal_intent_confidence=0.0,
                    case_intent_confidence=0.0
                )

        words = cleaned.split()
        if len(words) <= 2 and len(cleaned) <= 15 and re.match(r'^[a-zA-Z0-9_\-\.\?]+$', cleaned):
            return RoutingResult(
                intent=QueryIntent.AMBIGUOUS,
                confidence=0.90,
                reason="Isolated cryptic token or abbreviation requires clarification.",
                matched_patterns=["SHORT_AMBIGUOUS_TOKEN"],
                sub_intent="CRYPTIC_TOKEN",
                legal_intent_confidence=0.0,
                case_intent_confidence=0.0
            )

        # ---------------------------------------------------------------------
        # STEP 9: PRIORITY 7 — Safe Ambiguous Fallback
        # CRITICAL PRINCIPLE: Uncertain does NOT automatically mean LEGAL_QUERY.
        # If an inquiry has NO legal anchor, NO case anchor, is NOT out-of-scope,
        # and is NOT conversational, it routes to AMBIGUOUS for clarification.
        # It NEVER blindly invokes General Legal RAG.
        # ---------------------------------------------------------------------
        return RoutingResult(
            intent=QueryIntent.AMBIGUOUS,
            confidence=0.85,
            reason="Query lacks identifiable legal anchors, statutory references, or case context. Clarification requested.",
            matched_patterns=["AMBIGUOUS_NO_LEGAL_ANCHOR"],
            sub_intent="CLARIFICATION_REQUIRED",
            legal_intent_confidence=0.0,
            case_intent_confidence=0.0
        )


# Global singleton router instance
_GLOBAL_ROUTER: Optional[QueryRouter] = None


def get_query_router() -> QueryRouter:
    """Returns the singleton QueryRouter instance."""
    global _GLOBAL_ROUTER
    if _GLOBAL_ROUTER is None:
        _GLOBAL_ROUTER = QueryRouter()
    return _GLOBAL_ROUTER
