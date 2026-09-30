import sqlite3
from test_resolver import ActResolver

conn = sqlite3.connect('data/legalai_indian_legal_knowledge.db')
c = conn.cursor()
resolver = ActResolver()

queries = [
    "What does Section 19 of the POCSO Act require when an offence is known or suspected?",
    "What are the requirements for incorporation of a company under Section 7 of the Companies Act, 2013?",
    "What are the requirements for initiating the corporate insolvency resolution process by an operational creditor under Section 9 of the IBC?",
    "What remedies are available under Section 34 of the Arbitration and Conciliation Act, 1996 to challenge an arbitral award?",
    "What are the twin bail conditions under Section 45 of the Prevention of Money-Laundering Act?",
    "What safeguards apply to a personal search under Section 50 of the NDPS Act?",
    "What is the scope of a first appeal under Section 96 of the Code of Civil Procedure?",
    "When can specific performance be granted under the Specific Relief Act, 1963?",
    "What does Section 10 of the XYZ Act provide?",
    "What is Section 4 of the Marine Insurance Act, 1963?"
]

print("=" * 80)
for q in queries:
    res = resolver.resolve(q)
    print(f"\nQUERY: {q}")
    print(f"  Resolved: act_prefix={res['act_prefix']}, sec={res['provision_number']}, unindexed={res['is_unindexed_act']}")

    if res['is_unindexed_act']:
        print(f"  -> SAFE ABSTENTION: Requested Act '{res['unindexed_act_name']}' is not indexed in corpus.")
        continue

    # Test retrieval
    results = []
    # If exact provision and act prefix
    if res['act_prefix'] and res['provision_number']:
        exact_row = c.execute(
            "SELECT chunk_id, act_name, provision_number, provision_title FROM indian_legal_chunks WHERE act_prefix=? AND provision_number=?",
            (res['act_prefix'], res['provision_number'])
        ).fetchone()
        if exact_row:
            results.append(exact_row)

    # FTS query with act constraint
    clean_terms = []
    for term in q.replace('"', ' ').replace("'", ' ').split():
        clean = "".join(ch for ch in term if ch.isalnum() or ch in ("-", "_"))
        if clean and clean.lower() not in ("and", "or", "not", "near", "what", "does", "are", "the", "for", "of", "an", "under", "in", "is"):
            clean_terms.append(f'"{clean}"')

    if clean_terms:
        fts_match = " OR ".join(clean_terms)
        where_clauses = ["fts.indian_legal_chunks_fts MATCH ?"]
        params = [fts_match]
        if res['act_prefix']:
            where_clauses.append("c.act_prefix = ?")
            params.append(res['act_prefix'])

        sql = f"""
        SELECT c.chunk_id, c.act_name, c.provision_number, c.provision_title
        FROM indian_legal_chunks_fts fts
        JOIN indian_legal_chunks c ON fts.chunk_id = c.chunk_id
        WHERE {" AND ".join(where_clauses)}
        ORDER BY fts.rank
        LIMIT 5
        """
        fts_rows = c.execute(sql, params).fetchall()
        for r in fts_rows:
            if not any(r[0] == existing[0] for existing in results):
                results.append(r)

    print(f"  Retrieved {len(results)} chunks:")
    for r in results[:3]:
        print(f"    - {r[0]} | {r[1]} | Section {r[2]}: {r[3]}")
