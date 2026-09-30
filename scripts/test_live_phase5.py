import json
import urllib.request

BASE_URL = "http://127.0.0.1:8008/api/v1/ai/chat"

def query(text):
    payload = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

queries = [
    ("Companies §7", "What are the requirements for incorporation of a company under Section 7 of the Companies Act, 2013?", "COMPANIES_ACT_2013", "7"),
    ("IBC §9", "What are the requirements for initiating the corporate insolvency resolution process by an operational creditor under Section 9 of the IBC?", "IBC_2016", "9"),
    ("Arbitration §34", "What remedies are available under Section 34 of the Arbitration and Conciliation Act, 1996 to challenge an arbitral award?", "ARBITRATION_ACT_1996", "34"),
    ("POCSO §19", "What does Section 19 of the POCSO Act require when an offence is known or suspected?", "POCSO_ACT_2012", "19"),
    ("PMLA §45", "What are the twin bail conditions under Section 45 of the Prevention of Money-Laundering Act?", "PMLA_2002", "45"),
    ("NDPS §50", "What safeguards apply to a personal search under Section 50 of the NDPS Act?", "NDPS_ACT_1985", "50"),
    ("CPC §96", "What is the scope of a first appeal under Section 96 of the Code of Civil Procedure?", "CPC_1908", "96"),
    ("Specific Relief", "When can specific performance be granted under the Specific Relief Act, 1963?", "SPECIFIC_RELIEF_ACT_1963", None),
    ("Unindexed XYZ Act", "What does Section 10 of the XYZ Act provide?", None, "10")
]

print("=" * 80)
print("PHASE 5 LIVE API ENDPOINT VERIFICATION")
print("=" * 80)

all_passed = True
for name, q, expected_act, expected_sec in queries:
    print(f"\n--- {name} ---")
    print(f"Query: {q}")
    res = query(q)
    content = res.get("content", "")
    sources = res.get("sources", [])
    query_type = res.get("query_type")
    reliability = res.get("reliability")
    evidence_status = res.get("evidence_status")

    print(f"Query Type: {query_type}")
    print(f"Reliability: {reliability} ({res.get('reliabilityLabel')})")
    print(f"Evidence Status: {evidence_status}")
    print(f"Sources count: {len(sources)}")
    if sources:
        top_s = sources[0]
        print(f"Top Source: {top_s.get('chunk_id')} | {top_s.get('act_name')} | {top_s.get('section_number')}")
    print(f"Content preview: {content[:180].replace('\n', ' ')}...")

    if expected_act is None:
        # Expecting safe abstention
        assert len(sources) == 0, f"Expected 0 sources for unindexed Act, got {len(sources)}"
        assert "insufficient authoritative source coverage" in content.lower() or "outside the current legalai" in content.lower(), "Expected safe abstention message"
        assert res.get("requires_verification") is True
        print(f"-> PASS: Safe abstention verified for unindexed Act.")
    else:
        assert len(sources) > 0, f"Expected sources for {expected_act}, got 0"
        top_chunk_id = sources[0].get("chunk_id", "")
        assert expected_act in top_chunk_id, f"Expected {expected_act} in top chunk, got {top_chunk_id}"
        if expected_sec:
            assert expected_sec in top_chunk_id or expected_sec in sources[0].get("section_number", ""), f"Expected section {expected_sec} in top source"
        # Verify NO wrong Act leakage
        for s in sources:
            cid = s.get("chunk_id", "")
            assert expected_act in cid or "SC_" in cid, f"Wrong Act leakage: {cid} in query for {expected_act}"
        print(f"-> PASS: Correct Act '{expected_act}' retrieved at Rank 1 with zero cross-domain leakage.")

print("\n" + "=" * 80)
print("ALL PHASE 5 QUERIES PASSED WITH ZERO CROSS-DOMAIN LEAKAGE!")
print("=" * 80)
