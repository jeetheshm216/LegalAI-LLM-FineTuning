import sys
from pathlib import Path
from draft_query_router import UniversalQueryRouter, QueryIntent

def run_tests():
    router = UniversalQueryRouter()
    failures = []

    test_cases = [
        # 1. System Info
        ("what is the model of legal ai", QueryIntent.SYSTEM_INFO),
        ("What model is LegalAI using?", QueryIntent.SYSTEM_INFO),
        ("What model powers LegalAI?", QueryIntent.SYSTEM_INFO),
        ("What technology does LegalAI use?", QueryIntent.SYSTEM_INFO),
        ("How does LegalAI work?", QueryIntent.SYSTEM_INFO),
        ("What are your capabilities?", QueryIntent.SYSTEM_INFO),
        ("How was LegalAI built?", QueryIntent.SYSTEM_INFO),
        ("What AI model are you using?", QueryIntent.SYSTEM_INFO),
        ("Does LegalAI use RAG?", QueryIntent.SYSTEM_INFO),
        ("Why does LegalAI use Qwen?", QueryIntent.SYSTEM_INFO),

        # 2. Technical AI
        ("What is artificial intelligence?", QueryIntent.TECHNICAL_AI),
        ("What is machine learning?", QueryIntent.TECHNICAL_AI),
        ("What is an LLM?", QueryIntent.TECHNICAL_AI),
        ("What is Qwen?", QueryIntent.TECHNICAL_AI),
        ("Can you explain Qwen", QueryIntent.TECHNICAL_AI),
        ("Explain RAG.", QueryIntent.TECHNICAL_AI),
        ("How does RAG work?", QueryIntent.TECHNICAL_AI),
        ("What is a LoRA adapter?", QueryIntent.TECHNICAL_AI),
        ("What is fine-tuning?", QueryIntent.TECHNICAL_AI),
        ("How does fine-tuning work?", QueryIntent.TECHNICAL_AI),
        ("What is the difference between RAG and fine-tuning?", QueryIntent.TECHNICAL_AI),
        ("What are embeddings?", QueryIntent.TECHNICAL_AI),
        ("What is a vector database?", QueryIntent.TECHNICAL_AI),

        # 3. Case Management
        ("what is the important thing i have to focus on now", QueryIntent.CASE_MANAGEMENT),
        ("like what case i have to focus more which have the high priority", QueryIntent.CASE_MANAGEMENT),
        ("Which case should I focus on?", QueryIntent.CASE_MANAGEMENT),
        ("Which case has the highest priority?", QueryIntent.CASE_MANAGEMENT),
        ("What is my most urgent case?", QueryIntent.CASE_MANAGEMENT),
        ("What hearings are scheduled for this week?", QueryIntent.CASE_MANAGEMENT),
        ("When is my next hearing?", QueryIntent.CASE_MANAGEMENT),
        ("Which cases have upcoming deadlines?", QueryIntent.CASE_MANAGEMENT),
        ("Show me my urgent cases", QueryIntent.CASE_MANAGEMENT),
        ("Which cases need attention?", QueryIntent.CASE_MANAGEMENT),

        # 4. Legal Concepts (No 'legal' word required!)
        ("What is negligence?", QueryIntent.LEGAL_QUERY),
        ("What is bail?", QueryIntent.LEGAL_QUERY),
        ("What is defamation?", QueryIntent.LEGAL_QUERY),
        ("What happens after an FIR?", QueryIntent.LEGAL_QUERY),
        ("Can a person claim self-defence?", QueryIntent.LEGAL_QUERY),
        ("What is consideration in contract law?", QueryIntent.LEGAL_QUERY),
        ("What is the punishment for cheating?", QueryIntent.LEGAL_QUERY),
        ("What is the limitation period?", QueryIntent.LEGAL_QUERY),
        ("What is anticipatory bail?", QueryIntent.LEGAL_QUERY),

        # 5. Exact Provisions
        ("What is Section 66C of the IT Act?", QueryIntent.EXACT_PROVISION_QUERY),
        ("What does BNS Section 103 cover?", QueryIntent.EXACT_PROVISION_QUERY),
        ("Section 63 of BSA", QueryIntent.EXACT_PROVISION_QUERY),
        ("Article 21", QueryIntent.EXACT_PROVISION_QUERY),
        ("Section 420 IPC", QueryIntent.EXACT_PROVISION_QUERY),
        ("Section 49A", QueryIntent.EXACT_PROVISION_QUERY),

        # 6. Case Queries
        ("What evidence is missing?", QueryIntent.CASE_QUERY),
        ("What are the key facts in this case?", QueryIntent.CASE_QUERY),
        ("What contradictions exist?", QueryIntent.CASE_QUERY),
        ("What documents support the client's position?", QueryIntent.CASE_QUERY),
        ("Summarize the uploaded documents", QueryIntent.CASE_QUERY),

        # 7. Hearing Preparation
        ("What should I prepare for the next hearing?", QueryIntent.HEARING_PREPARATION),
        ("What points should I tell the judge?", QueryIntent.HEARING_PREPARATION),

        # 8. Out of Scope
        ("Write me a Python game.", QueryIntent.OUT_OF_SCOPE),
        ("Who won the football match?", QueryIntent.OUT_OF_SCOPE),
        ("What laptop should I buy?", QueryIntent.OUT_OF_SCOPE),
        ("How do I cook biryani?", QueryIntent.OUT_OF_SCOPE),
        ("What is the weather today?", QueryIntent.OUT_OF_SCOPE),

        # 9. Conversational
        ("Hey! How are you doing today?", QueryIntent.CONVERSATIONAL),
        ("Thank you so much for the clarification", QueryIntent.CONVERSATIONAL),
        ("Are you an AI?", QueryIntent.CONVERSATIONAL),

        # 10. Ambiguous
        ("xyz", QueryIntent.AMBIGUOUS),
        ("49p", QueryIntent.AMBIGUOUS),
    ]

    print(f"Running {len(test_cases)} standalone query test cases...")
    for q, expected in test_cases:
        res = router.classify(q)
        if res.intent != expected:
            failures.append((q, expected, res.intent, res.reason))
            print(f"  [FAIL] '{q}' -> Expected {expected}, got {res.intent} (reason: {res.reason})")
        else:
            print(f"  [PASS] '{q}' -> {res.intent.value}")

    # Context Isolation Sequences
    print("\nTesting Context Isolation (History Override Prevention)...")
    # Case -> Technical: previous was CASE_QUERY, new query is "What is Qwen?"
    hist_case = [
        {"role": "user", "content": "What evidence is missing?", "query_type": "CASE_QUERY"},
        {"role": "assistant", "content": "Missing evidence...", "query_type": "CASE_QUERY"}
    ]
    res_tech = router.classify("What is Qwen?", conversation_history=hist_case, case_id="case-01")
    if res_tech.intent != QueryIntent.TECHNICAL_AI or res_tech.requires_case_documents:
        failures.append(("Context Isolation Case->Tech", QueryIntent.TECHNICAL_AI, res_tech.intent, "Leaked case"))
        print(f"  [FAIL] Context Isolation Case->Tech failed: {res_tech.intent}, docs={res_tech.requires_case_documents}")
    else:
        print("  [PASS] Context Isolation: 'What is Qwen?' after Case Query correctly routed to TECHNICAL_AI (no case docs)!")

    # Legal -> Technical: previous was LEGAL_QUERY, new is "Explain RAG."
    hist_legal = [
        {"role": "user", "content": "What is Section 66C of the IT Act?", "query_type": "EXACT_PROVISION_QUERY"},
        {"role": "assistant", "content": "Section 66C...", "query_type": "EXACT_PROVISION_QUERY"}
    ]
    res_rag = router.classify("Explain RAG.", conversation_history=hist_legal)
    if res_rag.intent != QueryIntent.TECHNICAL_AI or res_rag.requires_legal_rag:
        failures.append(("Context Isolation Legal->Tech", QueryIntent.TECHNICAL_AI, res_rag.intent, "Leaked legal"))
        print(f"  [FAIL] Context Isolation Legal->Tech failed: {res_rag.intent}, legal_rag={res_rag.requires_legal_rag}")
    else:
        print("  [PASS] Context Isolation: 'Explain RAG.' after Legal Query correctly routed to TECHNICAL_AI (no legal RAG)!")

    # Anaphoric continuation: Programming -> "for odd or even"
    hist_prog = [
        {"role": "user", "content": "Write a python code", "query_type": "OUT_OF_SCOPE"},
        {"role": "assistant", "content": "Programming is outside scope...", "query_type": "OUT_OF_SCOPE"}
    ]
    res_anaph = router.classify("for odd or even", conversation_history=hist_prog)
    if res_anaph.intent != QueryIntent.OUT_OF_SCOPE:
        failures.append(("Anaphora Prog->Odd/Even", QueryIntent.OUT_OF_SCOPE, res_anaph.intent, "Did not inherit anaphora"))
        print(f"  [FAIL] Anaphora follow-up failed: {res_anaph.intent}")
    else:
        print("  [PASS] Anaphora continuation: 'for odd or even' correctly inherited OUT_OF_SCOPE!")

    print(f"\nCompleted tests. Total Failures: {len(failures)} / {len(test_cases) + 3}")
    return len(failures) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
