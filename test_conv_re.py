import re

CONVERSATIONAL_RE = re.compile(
    r'^\s*(?:hi|hello|hey|hiya|howdy|greetings|good\s+(?:morning|afternoon|evening|day)|'
    r'how\s+(?:are\s+you|are\s+u|is\s+it\s+going|do\s+you\s+do)|'
    r'what\s+are\s+you\s+doing|'
    r'wow|cool|awesome|super|great|nice|understood|ok|okay|got\s+it|thanks|thank\s+you|thx)\b',
    re.IGNORECASE
)

for q in ["how are you", "what are you doing", "wow", "ok", "thanks"]:
    print(q, bool(CONVERSATIONAL_RE.search(q)))
