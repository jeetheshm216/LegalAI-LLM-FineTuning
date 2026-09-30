"""
src/api/query_understanding/normalizer.py

Production-quality tolerant query normalizer for LegalAI.
Features:
1. Strict shielding for Legal Identifiers (Sections, Acts, case numbers, citations, party names, court names).
2. Never modifies words that are already valid standard English or legal terms.
3. Smart token-boundary and split-join repair (e.g. 'i syour' -> 'is your', 'wa ht' -> 'what', 'thiscase' -> 'this case').
4. General Damerau-Levenshtein edit-distance normalization against domain vocabulary for misspelled/unknown words.
5. Repeated-character compression and informal contraction normalization.
6. Guaranteed restoration of protected legal entities.
"""

import re
from typing import Tuple, Dict, List, Set, Optional


class QueryNormalizer:
    """
    Tolerant query normalizer that preserves legal identifiers while
    correcting natural lawyer typographical, conversational, and spelling variations.
    """

    # Comprehensive set of common valid English and legal words that must NEVER be altered
    VALID_WORDS: Set[str] = {
        # Common grammar & function words
        "a", "about", "above", "action", "actions", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "attention", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can", "cannot", "can't", "care", "case", "cases", "could",
        "couldn't", "deal", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
        "during", "each", "evidence", "evidences", "fact", "facts", "few", "first", "focus", "focused",
        "focusing", "for", "from", "further", "gap", "gaps", "give", "had", "hadn't", "happen", "happened",
        "has", "hasn't", "have", "haven't", "having", "he", "hearing", "hearings", "help", "her", "here",
        "hers", "herself", "him", "himself", "his", "how", "i", "identity", "if", "important", "importance",
        "in", "into", "is", "isn't", "issue", "issues", "it", "its", "itself", "key", "let's", "main",
        "major", "matter", "matters", "me", "missing", "more", "most", "mustn't", "my", "myself", "name",
        "names", "need", "next", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
        "ought", "our", "ours", "ourselves", "out", "over", "own", "point", "points", "prepare", "preparation",
        "prioritize", "priority", "priorities", "proof", "prove", "review", "risk", "risks", "same",
        "see", "shan't", "she", "should", "shouldn't", "show", "simple", "simply", "so", "some",
        "steps", "such", "summarize", "summary", "take", "tell", "than", "that", "the", "their", "theirs",
        "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "timeline",
        "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "were", "weren't", "what",
        "when", "where", "which", "while", "who", "whom", "why", "with", "won't", "would", "wouldn't",
        "you", "your", "yours", "yourself", "yourselves",
        # Primary legal and case terms
        "file", "files", "court", "courts", "judge", "judges", "bench", "counsel", "advocate", "lawyer", "client",
        "plaintiff", "defendant", "petitioner", "respondent", "accused", "victim",
        "claim", "claims", "allegation", "allegations", "pleading", "pleadings",
        "fir", "complaint", "chargesheet", "bail", "custody", "remand",
        "document", "documents", "witness", "witnesses",
        "statement", "statements", "contradiction", "contradictions", "testimony",
        "chronology", "arguments", "argument",
        "counterargument", "counterarguments",
        "weakness", "weaknesses", "strengths", "strength",
        "draft", "drafting", "notice", "petition", "reply", "affidavit",
        "order", "orders", "rule", "rules", "section", "sections", "act", "acts",
        "critical", "crucial", "essential", "primary",
        "last", "detail", "detailed", "analysis", "analyze", "analyse", "explain",
        "everything", "overall", "overview",
        "look", "law", "legal", "statute", "statutory", "provision", "provisions",
        "offence", "offenses", "crime", "punishment", "penalty", "liable",
        "liability", "support", "supports", "opposing", "side", "argue",
        "worry", "worried", "concern", "concerned", "actually", "really",
        "another", "other", "others", "into", "onto", "upon", "without", "within", "cannot",
        "along", "around", "behind", "beyond", "inside", "outside", "together",
        "someone", "something", "anyone", "anything", "nothing", "everyone", "everything",
        "similar", "difference", "compare", "comparison"
    }

    # Target domain vocabulary for fuzzy matching when a token is misspelled
    TARGET_DOMAIN_VOCABULARY: Set[str] = {
        "points", "point", "important", "importance", "matters", "matter", "issues", "issue",
        "evidence", "evidences", "document", "documents", "witness", "witnesses",
        "statement", "statements", "contradiction", "contradictions", "facts", "fact",
        "summary", "summarize", "summarise", "timeline", "chronology", "chronological",
        "arguments", "argument", "counterargument", "counterarguments",
        "weakness", "weaknesses", "strengths", "strength", "risks", "risk",
        "missing", "prove", "proof", "prepare", "preparation", "hearing", "hearings",
        "court", "judge", "bench", "draft", "drafting", "notice", "petition", "reply",
        "affidavit", "plaintiff", "defendant", "client", "allegation", "allegations",
        "claim", "claims", "focus", "attention", "critical", "crucial",
        "essential", "key", "main", "major", "primary", "about", "happen", "happened",
        "first", "next", "steps", "action", "detailed", "analysis",
        "analyze", "analyse", "explain", "simple", "simply", "everything",
        "overall", "overview", "review", "reviewing", "support", "supports",
        "opposing", "counsel", "chargesheet", "pleadings", "bail", "custody",
        "what", "which", "where", "when", "why", "how", "who", "case", "cases",
        "name", "names", "identity", "priority", "priorities", "prioritize", "deal", "your", "you"
    }

    # Common informal chat / contraction expansions
    INFORMAL_EXPANSIONS = {
        "r": "are",
        "u": "you",
        "ur": "your",
        "pls": "please",
        "plz": "please",
        "wat": "what",
        "wht": "what",
        "abt": "about",
        "bcoz": "because",
        "cuz": "because",
        "thx": "thanks",
        "ty": "thank you",
        "idk": "i do not know",
        "info": "information",
        "prep": "prepare",
        "docs": "documents",
        "evid": "evidence",
        "sec": "section",
        "secs": "sections",
        "art": "article",
        "arts": "articles",
    }

    # Strict regex patterns for legal and system identifiers that MUST NEVER be modified
    LEGAL_PROTECTION_PATTERNS = [
        # Sections, Articles, Orders, Rules
        r'\b(?:section|sec\.?|s\.?|u/s|§|provision)\s*[0-9]+[A-Za-z]*(?:\s*\([0-9a-z]+\))*\b',
        r'\barticle\s+[0-9]+[A-Za-z]*(?:\s*\([0-9a-z]+\))*\b',
        r'\border\s+[0-9IVXLCDM]+\s*(?:rule\s+[0-9]+[A-Za-z]*)?\b',
        r'\bclause\s+[0-9]+[A-Za-z]*(?:\s*\([0-9a-z]+\))*\b',
        r'\bschedule\s+[0-9IVXLCDM]+\b',
        # Known Indian Acts and Acronyms (with optional section/provision number)
        r'\b(?:bns|bnss|bsa|ipc|crpc|iea|cpc|it\s+act|ita|posh|pocso|ndps|pmla|uapa|rbi|sebi|rera|ibc)(?:\s+(?:section|sec\.?|s\.?)?\s*\d+[A-Za-z]*)?\b',
        r'\bbharatiya\s+nyaya\s+sanhita(?:\s*,?\s*2023)?\b',
        r'\bbharatiya\s+nagarik\s+suraksha\s+sanhita(?:\s*,?\s*2023)?\b',
        r'\bbharatiya\s+sakshya\s+adhiniyam(?:\s*,?\s*2023)?\b',
        r'\bindian\s+penal\s+code(?:\s*,?\s*1860)?\b',
        r'\bcode\s+of\s+criminal\s+procedure(?:\s*,?\s*1973)?\b',
        r'\b(?:indian\s+)?evidence\s+act(?:\s*,?\s*1872)?\b',
        r'\bconstitution\s+of\s+india\b',
        r'\bcompanies\s+act(?:\s*,?\s*2013)?\b',
        r'\bcontract\s+act(?:\s*,?\s*1872)?\b',
        r'\barbitration\s+(?:and\s+conciliation\s+)?act(?:\s*,?\s*1996)?\b',
        r'\blimitation\s+act(?:\s*,?\s*1963)?\b',
        r'\bnegotiable\s+instruments?\s+act(?:\s*,?\s*1881)?\b',
        r'\bni\s+act\b',
        r'\binformation\s+technology\s+act(?:\s*,?\s*2000)?\b',
        r'\b[A-Z][a-zA-Z\s]{2,40}\s+Act(?:\s*,?\s*(?:18|19|20)\d{2})?\b',
        # Case Numbers & IDs
        r'\b\d{4}-[A-Z]+-\d+\b',
        r'\bcase-\d+\b',
        r'\b[A-Z]+\s+No\.?\s+\d+\s+of\s+\d{4}\b',
        # Known Case Parties
        r'\b(?:martinez|coastal\s+holdings(?:\s+ltd\.?)?|whitfield|nguyen|apex\s+logistics|horizon\s+freight)\b',
        # Technical AI & System Architecture
        r'\b(?:qwen(?:2\.5)?(?:-14b(?:-instruct)?)?|lora|rag|legalai|peft|transformer|bert|llm)\b',
    ]

    def __init__(self):
        self._compiled_protections = [re.compile(p, re.IGNORECASE) for p in self.LEGAL_PROTECTION_PATTERNS]

    @staticmethod
    def damerau_levenshtein_distance(s1: str, s2: str) -> int:
        """Computes true Damerau-Levenshtein distance with adjacent transpositions."""
        d = {}
        len1, len2 = len(s1), len(s2)
        for i in range(-1, len1 + 1):
            d[(i, -1)] = i + 1
        for j in range(-1, len2 + 1):
            d[(-1, j)] = j + 1

        for i in range(len1):
            for j in range(len2):
                cost = 0 if s1[i] == s2[j] else 1
                d[(i, j)] = min(
                    d[(i - 1, j)] + 1,        # deletion
                    d[(i, j - 1)] + 1,        # insertion
                    d[(i - 1, j - 1)] + cost  # substitution
                )
                if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                    d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + 1)  # transposition

        return d[(len1 - 1, len2 - 1)]

    def protect_entities(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Finds and shields legal identifiers so typo correction never alters them."""
        protected: Dict[str, str] = {}
        counter = 0

        # Scan all protection regexes
        for rx in self._compiled_protections:
            for match in rx.finditer(text):
                val = match.group(0)
                if any(val == p_val for p_val in protected.values()):
                    continue
                placeholder = f"__LEGAL_PROT_{counter}__"
                protected[placeholder] = val
                counter += 1

        shielded = text
        for placeholder, original in sorted(protected.items(), key=lambda x: len(x[1]), reverse=True):
            pattern = re.escape(original)
            shielded = re.sub(rf'\b{pattern}\b', placeholder, shielded, flags=re.IGNORECASE)

        return shielded, protected

    def restore_entities(self, text: str, protected: Dict[str, str]) -> str:
        """Restores protected legal identifiers in place."""
        restored = text
        for placeholder, original in protected.items():
            restored = restored.replace(placeholder, original)
        return restored

    def compress_repeated_characters(self, word: str) -> str:
        """Reduces triple+ repeated characters (e.g., 'pooooints' -> 'points')."""
        return re.sub(r'(.)\1{2,}', r'\1', word)

    def find_best_vocabulary_match(self, token: str) -> Optional[str]:
        """
        General dynamic spell matching against the domain vocabulary.
        Only applied to words that are NOT already valid English/legal words.
        """
        lower = token.lower()
        # Invariant: If word is already valid, do not alter it!
        if lower in self.VALID_WORDS:
            return lower

        best_match = None
        min_dist = 99
        token_len = len(lower)

        for candidate in self.TARGET_DOMAIN_VOCABULARY:
            cand_len = len(candidate)
            if abs(token_len - cand_len) > 2:
                continue

            dist = self.damerau_levenshtein_distance(lower, candidate)
            max_allowed = 1 if token_len < 6 else 2

            if dist <= max_allowed and dist < min_dist:
                similarity = 1.0 - (dist / max(token_len, cand_len))
                if similarity >= 0.70:
                    min_dist = dist
                    best_match = candidate

        return best_match if min_dist <= 2 else None

    def repair_split_and_joined_tokens(self, tokens: List[str]) -> List[str]:
        """
        Repairs shifted spaces (e.g. 'i syour' -> 'is your', 'wha tis' -> 'what is'),
        split short words (e.g. 'wa ht' -> 'what'), and concatenated words ('thiscase' -> 'this case').
        """
        i = 0
        repaired: List[str] = []
        while i < len(tokens):
            if tokens[i].startswith("__LEGAL_PROT_"):
                repaired.append(tokens[i])
                i += 1
                continue

            if i + 1 < len(tokens) and not tokens[i+1].startswith("__LEGAL_PROT_"):
                t1, t2 = tokens[i].lower(), tokens[i+1].lower()

                # Shifted space right: 'i' + 'syour' -> 'is', 'your'
                # Only when t2 is NOT a valid word / expansion, but shifting yields 2 valid words
                if len(t1) <= 2 and len(t2) >= 3 and t2 not in self.VALID_WORDS and t2 not in self.INFORMAL_EXPANSIONS:
                    cand1 = t1 + t2[0]
                    cand2 = t2[1:]
                    if (cand1 in self.VALID_WORDS or cand1 in self.TARGET_DOMAIN_VOCABULARY) and \
                       (cand2 in self.VALID_WORDS or cand2 in self.TARGET_DOMAIN_VOCABULARY or cand2 in self.INFORMAL_EXPANSIONS):
                        repaired.append(cand1)
                        repaired.append(cand2)
                        i += 2
                        continue

                # Shifted space left: 'wha' + 'tis' -> 'what', 'is'
                # Only when t1 is NOT a valid word, but shifting yields 2 valid words
                if len(t1) >= 3 and len(t2) <= 2 and t1 not in self.VALID_WORDS and t1 not in self.TARGET_DOMAIN_VOCABULARY:
                    cand1 = t1[:-1]
                    cand2 = t1[-1] + t2
                    if (cand1 in self.VALID_WORDS or cand1 in self.TARGET_DOMAIN_VOCABULARY) and \
                       (cand2 in self.VALID_WORDS or cand2 in self.TARGET_DOMAIN_VOCABULARY):
                        repaired.append(cand1)
                        repaired.append(cand2)
                        i += 2
                        continue

                # Split word joined: 'wa' + 'ht' -> 'what'
                # Only when NEITHER t1 nor t2 is a valid word / expansion
                if t1 not in self.VALID_WORDS and t1 not in self.INFORMAL_EXPANSIONS and \
                   t2 not in self.VALID_WORDS and t2 not in self.INFORMAL_EXPANSIONS:
                    combined = t1 + t2
                    if combined in self.VALID_WORDS or combined in self.TARGET_DOMAIN_VOCABULARY:
                        repaired.append(combined)
                        i += 2
                        continue
                    matched_comb = self.find_best_vocabulary_match(combined)
                    if matched_comb:
                        repaired.append(matched_comb)
                        i += 2
                        continue

            # Check missing space inside single joined word: 'thiscase' -> 'this', 'case'
            t = tokens[i].lower()
            if t not in self.VALID_WORDS and t not in self.TARGET_DOMAIN_VOCABULARY and len(t) >= 6:
                split_found = False
                for k in range(2, len(t) - 2):
                    p1 = t[:k]
                    p2 = t[k:]
                    if (p1 in self.VALID_WORDS or p1 in self.TARGET_DOMAIN_VOCABULARY) and \
                       (p2 in self.VALID_WORDS or p2 in self.TARGET_DOMAIN_VOCABULARY):
                        repaired.append(p1)
                        repaired.append(p2)
                        split_found = True
                        break
                if split_found:
                    i += 1
                    continue

            repaired.append(tokens[i])
            i += 1

        return repaired

    def normalize(self, query: str) -> Tuple[str, Dict[str, str]]:
        """
        Main normalization method.
        Returns:
            (normalized_query, protected_entities_dict)
        """
        raw = query.strip()
        if not raw:
            return "", {}

        # 1. Protect legal and system entities
        shielded, protected = self.protect_entities(raw)

        # Pre-repair phonetic/collocation patterns like 'kay points' -> 'key points'
        shielded = re.sub(r'\bkay\s+(points?|facts?|issues?)\b', r'key \1', shielded, flags=re.IGNORECASE)

        # 2. Tokenize and repair split/joined tokens
        tokens = shielded.split()
        repaired_tokens = self.repair_split_and_joined_tokens(tokens)

        # 3. Normalize words outside protected placeholders
        normalized_tokens: List[str] = []

        for token in repaired_tokens:
            if token.startswith("__LEGAL_PROT_") and token.endswith("__"):
                normalized_tokens.append(token)
                continue

            m = re.match(r'^([^\w]*)([\w\'-]+)([^\w]*)$', token)
            if not m:
                normalized_tokens.append(token)
                continue

            prefix, word, suffix = m.groups()
            cleaned_word = self.compress_repeated_characters(word.lower())

            # Check informal expansion first
            if cleaned_word in self.INFORMAL_EXPANSIONS:
                expanded = self.INFORMAL_EXPANSIONS[cleaned_word]
                normalized_tokens.append(f"{prefix}{expanded}{suffix}")
                continue

            # If word is already valid, keep it
            if cleaned_word in self.VALID_WORDS:
                normalized_tokens.append(f"{prefix}{word}{suffix}")
                continue

            # Check general edit-distance vocabulary match for misspelled unknown token
            best_vocab = self.find_best_vocabulary_match(cleaned_word)
            if best_vocab:
                normalized_tokens.append(f"{prefix}{best_vocab}{suffix}")
            else:
                normalized_tokens.append(f"{prefix}{word}{suffix}")

        normalized_shielded = " ".join(normalized_tokens)
        normalized_shielded = re.sub(r'\s+', ' ', normalized_shielded).strip()

        # 4. Restore protected entities
        final_query = self.restore_entities(normalized_shielded, protected)

        return final_query, protected
