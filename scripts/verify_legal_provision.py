#!/usr/bin/env python3
"""CLI tool to verify exact legal statutory provisions and authoritative provenance."""

import sys
import os
import argparse
import json

# Ensure repository root is on PYTHONPATH
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline


def main():
    parser = argparse.ArgumentParser(description="Verify exact Indian legal provision existence and provenance.")
    parser.add_argument("--act", required=True, help="Act name or prefix (e.g. 'The Companies Act, 2013' or 'COMPANIES_ACT_2013')")
    parser.add_argument("--section", required=True, help="Section or Article or Rule identifier (e.g. '89', '49A', 'ORDER_39_RULE_1')")
    parser.add_argument("--provision-type", default="SECTION", help="Provision type (SECTION, ARTICLE, ORDER_RULE, REGULATION, SCHEDULE_ITEM)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON result")

    args = parser.parse_args()

    pipeline = GeneralIndianLegalKnowledgePipeline()
    query_str = f"Section {args.section} of {args.act}" if args.provision_type == "SECTION" else f"{args.provision_type} {args.section} of {args.act}"

    res = pipeline.query(query_str)

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print("==================================================================")
    print("LEGALAI ??? STATUTORY PROVISION VERIFICATION REPORT")
    print("==================================================================")
    print(f"Target Act:             {args.act}")
    print(f"Requested Provision:    {args.section}")
    print(f"Provision Type:         {args.provision_type}")
    print(f"Response Type:          {res.get('response_type')}")
    print(f"Abstained:              {res.get('abstained')}")
    print(f"Requires Verification:  {res.get('requires_verification')}")
    print(f"Temporal Status:        {res.get('temporal_status')}")
    print("------------------------------------------------------------------")
    if res.get("sources"):
        print("Verified Authoritative Source(s):")
        for s in res["sources"]:
            print(f"  ??? {s.get('citation')} | Chunk ID: {s.get('chunk_id')} | URL: {s.get('source_url')}")
    else:
        print("No verified source chunks found. Absence notice:")
        print(" ", res.get("answer").splitlines()[0] if res.get("answer") else "None")
    print("==================================================================")


if __name__ == "__main__":
    main()

