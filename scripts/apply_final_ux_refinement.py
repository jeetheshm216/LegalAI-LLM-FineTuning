import os
import re

BASE_DIR = "/home/sece2026-student07/legalai-finetuning"

# -----------------------------------------------------------------------------
# 1. Update src/api/query_router.py
# -----------------------------------------------------------------------------
qr_path = os.path.join(BASE_DIR, "src/api/query_router.py")
with open(qr_path, "r", encoding="utf-8") as f:
    qr_code = f.read()

# Add OUT_OF_SCOPE_PATTERNS
out_of_scope_patterns = """    # -------------------------------------------------------------------------
    # OUT_OF_SCOPE_PATTERNS
    # Clear non-legal requests (entertainment, travel, shopping, sports, etc.)
    # Must be politely bounded with LegalAI scope message without Legal RAG.
    # -------------------------------------------------------------------------
    OUT_OF_SCOPE_PATTERNS = [
        r'\\b(?:recommend|suggest|give\\s+me)\\s+.*?\\b(?:movie|movies|film|films|series|shows?|songs?|music|album|anime|books?|novels?)\\b',
        r'\\b(?:best|good)\\s+(?:movies?|films?|songs?|shows?|places?\\s+to\\s+visit)\\b',
        r'\\b(?:travel\\s+plan|plan\\s+a\\s+trip|vacation|itinerary|hotel|flight|tourism)\\b',
        r'\\b(?:shopping|buy\\s+a\\s+phone|best\\s+laptop|clothes|fashion)\\b',
        r'\\b(?:recipe|recipes|cook|cooking|baking|restaurant|diet\\s+plan)\\b',
        r'\\b(?:cricket|football|soccer|nba|ipl|world\\s+cup|match\\s+score)\\b',
        r'\\b(?:dating\\s+advice|relationship\\s+advice|horoscope|astrology)\\b',
    ]

"""

if "OUT_OF_SCOPE_PATTERNS" not in qr_code:
    # Insert right before __init__
    qr_code = qr_code.replace("    def __init__(self):", out_of_scope_patterns + "    def __init__(self):", 1)
    print("Added OUT_OF_SCOPE_PATTERNS to QueryRouter")

# Update __init__ to compile out_of_scope_regexes
init_target = "        self._general_regexes = [\n            re.compile(p, re.IGNORECASE) for p in self.GENERAL_NON_LEGAL_PATTERNS\n        ]"
init_repl = """        self._general_regexes = [
            re.compile(p, re.IGNORECASE) for p in self.GENERAL_NON_LEGAL_PATTERNS
        ]
        self._out_of_scope_regexes = [
            re.compile(p, re.IGNORECASE) for p in self.OUT_OF_SCOPE_PATTERNS
        ]"""

if "_out_of_scope_regexes" not in qr_code and init_target in qr_code:
    qr_code = qr_code.replace(init_target, init_repl, 1)
    print("Updated __init__ with _out_of_scope_regexes")

# Add _extract_recent_context and updated classify
extract_context_method = """    def _extract_recent_context(self, history: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        \"\"\"Extracts lightweight metadata from the most recent 1-2 turns.\"\"\"
        if not history or len(history) == 0:
            return {}

        last_user_msg = None
        last_asst_msg = None
        for m in reversed(history):
            if not last_user_msg and m.get("role") == "user":
                last_user_msg = m
            if not last_asst_msg and m.get("role") == "assistant":
                last_asst_msg = m
            if last_user_msg and last_asst_msg:
                break

        user_content = str(last_user_msg.get("content", "")).lower() if last_user_msg else ""
        asst_content = str(last_asst_msg.get("content", "")).lower() if last_asst_msg else ""
        last_intent = (
            (last_asst_msg.get("query_type") or last_asst_msg.get("intent") or "") if last_asst_msg else ""
        ) or (
            (last_user_msg.get("query_type") or last_user_msg.get("intent") or "") if last_user_msg else ""
        )

        is_coding_context = any(w in user_content or w in asst_content for w in [
            "python", "code", "program", "script", "function", "java", "coding", "algorithm",
            "odd or even", "sort", "machine learning"
        ])

        is_legal_context = any(w in user_content or w in asst_content for w in [
            "section", "bns", "bnss", "bsa", "ipc", "crpc", "act", "offence", "bail", "statute", "punishment"
        ])

        is_case_context = any(w in user_content or w in asst_content for w in [
            "case", "fir", "witness", "hearing", "evidence", "petition", "chargesheet"
        ])

        return {
            "last_user_content": user_content,
            "last_asst_content": asst_content,
            "last_intent": str(last_intent).upper(),
            "is_coding_context": is_coding_context,
            "is_legal_context": is_legal_context,
            "is_case_context": is_case_context
        }

    def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> RoutingResult:"""

# Replace def classify
old_classify_start = "    def classify(\n        self,\n        message: str,\n        conversation_history: Optional[List[Dict[str, Any]]] = None\n    ) -> RoutingResult:"

if "def _extract_recent_context" not in qr_code and old_classify_start in qr_code:
    qr_code = qr_code.replace(old_classify_start, extract_context_method, 1)
    print("Added _extract_recent_context to QueryRouter")

# Now update the body of classify to handle OUT_OF_SCOPE and Priority 6 follow-up context
classify_body_target = """        # ---------------------------------------------------------------------
        # PRIORITY 4: GENERAL_NON_LEGAL
        # Coding, math, science, technology, general office writing, casual inquiries.
        # MUST NOT invoke Legal RAG, BNS/BNSS/BSA, or legal abstention.
        # ---------------------------------------------------------------------
        matched_general = []
        for r in self._general_regexes:
            m = r.search(cleaned)
            if m:
                matched_general.append(m.group(0))

        if matched_general:
            return RoutingResult(
                intent=QueryIntent.GENERAL_NON_LEGAL,
                confidence=0.95,
                reason="Query is a general technical, mathematical, or non-legal request.",
                matched_patterns=matched_general
            )

        # ---------------------------------------------------------------------
        # PRIORITY 5: CONVERSATION CONTEXT FOLLOW-UP
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
        # PRIORITY 6: SAFE GENERAL FALLBACK -> GENERAL_NON_LEGAL
        # Legal RAG must NEVER be the fallback for unclassified or non-legal queries.
        # Safe default routes to general assistant without statutory retrieval or abstention.
        # ---------------------------------------------------------------------
        return RoutingResult(
            intent=QueryIntent.GENERAL_NON_LEGAL,
            confidence=0.75,
            reason="Non-legal or unclassified inquiry safely routed without legal RAG.",
            matched_patterns=["SAFE_GENERAL_FALLBACK"]
        )"""

classify_body_repl = """        # ---------------------------------------------------------------------
        # PRIORITY 4: OUT_OF_SCOPE NON-LEGAL
        # Travel, movies, shopping, sports, general life advice.
        # Must be politely bounded with LegalAI scope message without Legal RAG.
        # ---------------------------------------------------------------------
        matched_out_of_scope = []
        for r in self._out_of_scope_regexes:
            m = r.search(cleaned)
            if m:
                matched_out_of_scope.append(m.group(0))

        if matched_out_of_scope:
            return RoutingResult(
                intent=QueryIntent.GENERAL_NON_LEGAL,
                confidence=0.95,
                reason="Out-of-scope non-legal inquiry (movies, travel, sports, shopping).",
                matched_patterns=["OUT_OF_SCOPE"] + matched_out_of_scope
            )

        # ---------------------------------------------------------------------
        # PRIORITY 5: GENERAL_NON_LEGAL (Explicit patterns)
        # Coding, math, science, tech, office tasks.
        # ---------------------------------------------------------------------
        matched_general = []
        for r in self._general_regexes:
            m = r.search(cleaned)
            if m:
                matched_general.append(m.group(0))

        if matched_general:
            return RoutingResult(
                intent=QueryIntent.GENERAL_NON_LEGAL,
                confidence=0.95,
                reason="Query is a general technical, mathematical, or non-legal request.",
                matched_patterns=matched_general
            )

        # ---------------------------------------------------------------------
        # PRIORITY 6: SHORT FOLLOW-UP CONTEXT RULE
        # Follow-ups (e.g. "for odd or even", "what about the penalty?") inherit
        # recent turn intent when no new domain keyword is introduced.
        # ---------------------------------------------------------------------
        ctx = self._extract_recent_context(conversation_history)
        if ctx:
            words = cleaned.split()
            if len(words) <= 15:
                # 1. Inherit GENERAL_NON_LEGAL / Coding context
                if ctx["is_coding_context"] or ctx["last_intent"] == QueryIntent.GENERAL_NON_LEGAL.value:
                    return RoutingResult(
                        intent=QueryIntent.GENERAL_NON_LEGAL,
                        confidence=0.92,
                        reason="Short follow-up inherits previous general coding/technical context.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_GENERAL"]
                    )
                # 2. Inherit LEGAL_QUERY context
                if ctx["is_legal_context"] or ctx["last_intent"] == QueryIntent.LEGAL_QUERY.value:
                    return RoutingResult(
                        intent=QueryIntent.LEGAL_QUERY,
                        confidence=0.90,
                        reason="Short follow-up inherits previous statutory legal context.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_LEGAL"]
                    )
                # 3. Inherit CASE_QUERY context
                if ctx["is_case_context"] or ctx["last_intent"] == QueryIntent.CASE_QUERY.value:
                    return RoutingResult(
                        intent=QueryIntent.CASE_QUERY,
                        confidence=0.90,
                        reason="Short follow-up inherits previous case context.",
                        matched_patterns=["CONTEXT_FOLLOW_UP_CASE"]
                    )

        # ---------------------------------------------------------------------
        # PRIORITY 7: SAFE GENERAL FALLBACK -> GENERAL_NON_LEGAL
        # Legal RAG must NEVER be the fallback for unclassified or non-legal queries.
        # Safe default routes to general assistant without statutory retrieval or abstention.
        # ---------------------------------------------------------------------
        return RoutingResult(
            intent=QueryIntent.GENERAL_NON_LEGAL,
            confidence=0.75,
            reason="Non-legal or unclassified inquiry safely routed without legal RAG.",
            matched_patterns=["SAFE_GENERAL_FALLBACK"]
        )"""

if classify_body_target in qr_code:
    qr_code = qr_code.replace(classify_body_target, classify_body_repl, 1)
    print("Updated classify body with OUT_OF_SCOPE and follow-up context in query_router.py")

with open(qr_path, "w", encoding="utf-8") as f:
    f.write(qr_code)
print("Finished saving query_router.py")

# -----------------------------------------------------------------------------
# 2. Update src/api/server.py
# -----------------------------------------------------------------------------
server_path = os.path.join(BASE_DIR, "src/api/server.py")
with open(server_path, "r", encoding="utf-8") as f:
    server_code = f.read()

# Define refined response constants and conversational response handler
server_conv_repl = """OUT_OF_SCOPE_RESPONSE = \"\"\"I’m mainly designed to help legal professionals, so that’s outside my main area. ⚖️

I can help you with:
• Case analysis
• Legal research
• Document analysis
• Evidence evaluation
• Hearing preparation
• Legal drafting
• BNS / BNSS / BSA research

What would you like to work on?\"\"\"

ABUSIVE_RESPONSE = (
    "I’m here to help. 🙂 If something went wrong, tell me what you need and I’ll do my best to help."
)

ODD_EVEN_PYTHON_RESPONSE = \"\"\"Sure! 😊 Here's a simple Python program to check whether a number is odd or even:

```python
number = int(input("Enter a number: "))

if number % 2 == 0:
    print("Even")
else:
    print("Odd")
```\"\"\"

GREETING_RESPONSES = {
    "hi": "Hey! 👋 How are you doing today?",
    "hey": "Hey! 😊 What are we working on today?",
    "hello": "Hello! 👋 How can I help you today?",
    "how are you": "I'm doing great and ready to help! 😊 What are you working on today?",
}

GREETING_VARIATIONS = [
    "Hey! 👋 What are we working on today?",
    "Hey there! 😊 How can I help you today?",
    "Hello! 👋 Ready when you are. What would you like to explore?",
    "Hi! 😊 What legal matter are we diving into today?",
]


def has_greeting_prefix(text: str) -> bool:
    \"\"\"Checks if a query begins with an introductory greeting.\"\"\"
    cleaned = text.strip().lower()
    return bool(re.match(r'^(?:hey|hi|hello|good\\s+(?:morning|afternoon|evening|day)|greetings)[,\\s!]+', cleaned))


def generate_conversational_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    intent: QueryIntent = QueryIntent.CONVERSATIONAL,
    history: Optional[List[Dict[str, Any]]] = None,
    max_new_tokens: int = 256
) -> str:
    \"\"\"Generates a natural conversational or general non-legal response with context awareness.\"\"\"
    cleaned = message.strip()
    lower = cleaned.lower()
    lower_norm = re.sub(r'[\\s,?!.]+', ' ', lower).strip()

    # 1. Abusive language check
    if re.search(r'\\b(?:fuck\\s+(?:you|off)|you\\s+are\\s+(?:stupid|idiot|dumb|useless)|shut\\s+up|bitch|bastard|asshole)\\b', lower):
        return ABUSIVE_RESPONSE

    # 2. Out-of-scope non-legal check (entertainment, travel, shopping, sports, general life advice)
    if re.search(r'\\b(?:recommend|suggest|give\\s+me)\\s+.*?\\b(?:movie|movies|film|films|series|shows?|songs?|music|album|anime|books?|novels?)\\b|\\b(?:best|good)\\s+(?:movies?|films?|songs?|shows?)\\b|\\b(?:travel\\s+plan|plan\\s+a\\s+trip|vacation|itinerary|hotel|flight|tourism)\\b|\\b(?:shopping|buy\\s+a\\s+phone|best\\s+laptop|clothes|fashion)\\b|\\b(?:recipe|recipes|cook|cooking|baking|restaurant)\\b|\\b(?:cricket|football|soccer|nba|ipl|world\\s+cup|match\\s+score)\\b|\\b(?:dating\\s+advice|relationship\\s+advice|horoscope|astrology)\\b', lower):
        return OUT_OF_SCOPE_RESPONSE

    # 3. Dedicated Conversational Handling
    if intent == QueryIntent.CONVERSATIONAL:
        # Check for "how are you"
        if re.search(r"\\bhow\\s+are\\s+you\\b|\\bhow\'?s\\s+it\\s+going\\b|\\bhow\\s+do\\s+you\\s+do\\b", lower):
            return "I'm doing great and ready to help! 😊 What are you working on today?"

        # Check for gratitude
        if re.match(r'^(?:thanks|thank\\s+you|thx|many\\s+thanks|appreciate\\s+it)(?:[\\s,!.]+)?$', lower_norm):
            return "You're very welcome! 😊 Let me know if you need anything else for your legal research or case analysis."

        # Exact greeting matches
        if lower_norm in GREETING_RESPONSES:
            return GREETING_RESPONSES[lower_norm]

        if re.match(r'^(?:hi|hey|hello|hey\\s+hi|hi\\s+hey|hello\\s+hi|hey\\s+there|hiya|greetings)(?:[\\s,!.]+)?$', lower_norm):
            return random.choice(GREETING_VARIATIONS)

        if re.match(r'^(?:good\\s+morning)(?:[\\s,!.]+)?$', lower_norm):
            return "Good morning! 👋 Ready when you are. What legal matter or research are we working on today?"

        if re.match(r'^(?:good\\s+evening)(?:[\\s,!.]+)?$', lower_norm):
            return "Good evening! 👋 How can I assist you with your legal matters or research today?"

        if re.match(r'^(?:good\\s+afternoon)(?:[\\s,!.]+)?$', lower_norm):
            return "Good afternoon! 👋 What legal matter or research can I assist you with today?"

    # 4. Dedicated General Non-Legal Handling
    if intent == QueryIntent.GENERAL_NON_LEGAL:
        # Check follow-up odd or even python code request
        if re.search(r'\\b(?:odd\\s+(?:or|and)\\s+even|even\\s+(?:or|and)\\s+odd)\\b', lower):
            return ODD_EVEN_PYTHON_RESPONSE

        # Open-ended coding request
        if re.match(r'^(?:write|give\\s+me|generate|show\\s+me)\\s+(?:a\\s+)?(?:python\\s+code|python\\s+program|code|program)(?:[\\s,?!.]+)?$', lower_norm) or lower_norm in ("write python code", "write a python code", "give me a python program", "python code"):
            return "Absolutely! 😊 What Python program would you like to build?"

        # Factual query: "what is python"
        if re.match(r'^(?:what\\s+is\\s+python)(?:[\\s,?!.]+)?$', lower_norm):
            return "Python is a popular programming language known for its simple syntax and wide range of uses, from automation and web development to AI and data science. 🐍\\n\\nIf you'd like, I can also help you get back to your legal research."

        # Calculations
        calc_match = re.match(r'^(?:calculate\\s+|compute\\s+|what\\s+is\\s+)?([0-9]+(?:\\.[0-9]+)?\\s*[\\+\\-\\*/]\\s*[0-9]+(?:\\.[0-9]+)?)(?:[\\s,?!.]+)?$', lower)
        if calc_match:
            expr = calc_match.group(1).replace(' ', '')
            try:
                if re.match(r'^[0-9\\+\\-\\*/\\.]+$', expr):
                    result = eval(expr, {"__builtins__": None}, {})
                    return f"The result of {calc_match.group(1)} is **{result}**. 😊 Let me know if you'd like help with anything else!"
            except Exception:
                pass

    # 5. Model Generation Fallback with Conversational History Context
    sys_prompt = GENERAL_NON_LEGAL_SYSTEM_PROMPT if intent == QueryIntent.GENERAL_NON_LEGAL else CONVERSATIONAL_SYSTEM_PROMPT
    messages = [{"role": "system", "content": sys_prompt}]
    
    # Include recent turn history (up to 4 turns) for context continuity
    if history and len(history) > 0:
        for h in history[-4:]:
            role = h.get("role")
            content_str = str(h.get("content", "")).strip()
            if role in ("user", "assistant") and content_str:
                messages.append({"role": role, "content": content_str})

    messages.append({"role": "user", "content": message})

    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    with torch.inference_mode():
        output_ids = pipeline.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=pipeline.tokenizer.pad_token_id,
            eos_token_id=pipeline.tokenizer.eos_token_id,
        )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()"""

# Replace in server_code from GREETING_VARIATIONS to end of generate_conversational_response
old_gen_regex = r'GREETING_VARIATIONS\s*=\s*\[.*?def generate_case_guidance'
match = re.search(old_gen_regex, server_code, re.DOTALL)
if match:
    server_code = server_code[:match.start()] + server_conv_repl + "\n\n\ndef generate_case_guidance" + server_code[match.end():]
    print("Replaced generate_conversational_response in server.py")
else:
    print("Could not match old generate_conversational_response in server.py")

# Update ai_chat and ai_chat_stream to pass history
server_code = server_code.replace(
    "intent=route_result.intent,\n            max_new_tokens=256 if is_conv else 512",
    "intent=route_result.intent,\n            history=req.history,\n            max_new_tokens=256 if is_conv else 512"
)

with open(server_path, "w", encoding="utf-8") as f:
    f.write(server_code)
print("Finished updating server.py")
