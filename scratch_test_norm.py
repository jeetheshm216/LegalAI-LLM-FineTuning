import re
from typing import List, Tuple, Dict, Set, Optional

VALID_WORDS = {
    'a', 'about', 'above', 'action', 'actions', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
    'any', 'are', 'aren\'t', 'as', 'at', 'attention', 'be', 'because', 'been', 'before', 'being',
    'below', 'between', 'both', 'but', 'by', 'can', 'cannot', 'can\'t', 'care', 'case', 'cases', 'could',
    'couldn\'t', 'deal', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down',
    'during', 'each', 'evidence', 'evidences', 'fact', 'facts', 'few', 'first', 'focus', 'focused',
    'focusing', 'for', 'from', 'further', 'gap', 'gaps', 'give', 'had', 'hadn\'t', 'happen', 'happened',
    'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'hearing', 'hearings', 'help', 'her', 'here',
    'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'identity', 'if', 'important', 'importance',
    'in', 'into', 'is', 'isn\'t', 'issue', 'issues', 'it', 'its', 'itself', 'key', 'let\'s', 'main',
    'major', 'matter', 'matters', 'me', 'missing', 'more', 'most', 'mustn\'t', 'my', 'myself', 'name',
    'names', 'need', 'next', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
    'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'point', 'points', 'prepare', 'preparation',
    'prioritize', 'priority', 'priorities', 'proof', 'prove', 'review', 'risk', 'risks', 'same',
    'see', 'shan\'t', 'she', 'should', 'shouldn\'t', 'show', 'simple', 'simply', 'so', 'some',
    'steps', 'such', 'summarize', 'summary', 'take', 'tell', 'than', 'that', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'timeline',
    'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'were', 'weren\'t', 'what',
    'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'won\'t', 'would', 'wouldn\'t',
    'you', 'your', 'yours', 'yourself', 'yourselves'
}

TARGET_DOMAIN_VOCABULARY = {
    'points', 'point', 'important', 'importance', 'matters', 'matter', 'issues', 'issue',
    'evidence', 'evidences', 'document', 'documents', 'witness', 'witnesses',
    'statement', 'statements', 'contradiction', 'contradictions', 'facts', 'fact',
    'summary', 'summarize', 'summarise', 'timeline', 'chronology', 'chronological',
    'arguments', 'argument', 'counterargument', 'counterarguments',
    'weakness', 'weaknesses', 'strengths', 'strength', 'risks', 'risk',
    'missing', 'prove', 'proof', 'prepare', 'preparation', 'hearing', 'hearings',
    'court', 'judge', 'bench', 'draft', 'drafting', 'notice', 'petition', 'reply',
    'affidavit', 'plaintiff', 'defendant', 'client', 'allegation', 'allegations',
    'claim', 'claims', 'focus', 'attention', 'critical', 'crucial',
    'essential', 'key', 'main', 'major', 'primary', 'about', 'happen', 'happened',
    'first', 'next', 'steps', 'action', 'detailed', 'analysis',
    'analyze', 'analyse', 'explain', 'simple', 'simply', 'everything',
    'overall', 'overview', 'review', 'reviewing', 'support', 'supports',
    'opposing', 'counsel', 'chargesheet', 'pleadings', 'bail', 'custody',
    'what', 'which', 'where', 'when', 'why', 'how', 'who', 'case', 'cases',
    'name', 'names', 'identity', 'priority', 'prioritize', 'priorities', 'deal', 'your', 'you'
}

def repair_split_and_joined_tokens(tokens: List[str]) -> List[str]:
    i = 0
    repaired: List[str] = []
    while i < len(tokens):
        if tokens[i].startswith('__LEGAL_PROT_'):
            repaired.append(tokens[i])
            i += 1
            continue

        if i + 1 < len(tokens) and not tokens[i+1].startswith('__LEGAL_PROT_'):
            t1, t2 = tokens[i].lower(), tokens[i+1].lower()
            
            # Check shifted space right: t1 + t2[0] and t2[1:]
            # e.g., 'i' + 'syour' -> ('is', 'your')
            if len(t1) <= 3 and len(t2) >= 3:
                cand1 = t1 + t2[0]
                cand2 = t2[1:]
                if (cand1 in VALID_WORDS or cand1 in TARGET_DOMAIN_VOCABULARY) and \
                   (cand2 in VALID_WORDS or cand2 in TARGET_DOMAIN_VOCABULARY):
                    repaired.append(cand1)
                    repaired.append(cand2)
                    i += 2
                    continue
            
            # Check shifted space left: t1[:-1] and t1[-1] + t2
            # e.g., 'wha' + 'tis' -> ('what', 'is')
            if len(t1) >= 3 and len(t2) <= 3:
                cand1 = t1[:-1]
                cand2 = t1[-1] + t2
                if (cand1 in VALID_WORDS or cand1 in TARGET_DOMAIN_VOCABULARY) and \
                   (cand2 in VALID_WORDS or cand2 in TARGET_DOMAIN_VOCABULARY):
                    repaired.append(cand1)
                    repaired.append(cand2)
                    i += 2
                    continue

            # Check split word joined: 'wa' + 'ht' -> 'what'
            combined = t1 + t2
            if combined in VALID_WORDS or combined in TARGET_DOMAIN_VOCABULARY:
                repaired.append(combined)
                i += 2
                continue

        # Check missing space inside single joined word: 'thiscase' -> 'this', 'case'
        t = tokens[i].lower()
        if t not in VALID_WORDS and t not in TARGET_DOMAIN_VOCABULARY and len(t) >= 6:
            split_found = False
            for k in range(2, len(t) - 2):
                p1 = t[:k]
                p2 = t[k:]
                if (p1 in VALID_WORDS or p1 in TARGET_DOMAIN_VOCABULARY) and \
                   (p2 in VALID_WORDS or p2 in TARGET_DOMAIN_VOCABULARY):
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

queries = [
    'what i syour name',
    'what is yor name',
    'wat is your name',
    'wht is your name',
    'what is the kay points',
    'what r the key pionts',
    'waht is the matter',
    'wht is the matter',
    'what evidnce do we have',
    'wa ht is the matter',
    'focus on thiscase please'
]

for q in queries:
    tokens = q.split()
    fixed = repair_split_and_joined_tokens(tokens)
    res_str = ' '.join(fixed)
    print(f'{q:30} -> {res_str}')
