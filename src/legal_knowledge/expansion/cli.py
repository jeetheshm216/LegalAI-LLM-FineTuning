"""Command Line Interface for the Indian Legal Corpus Expansion Engine."""

import argparse
import sys
import json
from .pipeline import AutomatedCorpusExpansionPipeline
from .models import IngestionStatus


def main():
    parser = argparse.ArgumentParser(
        description="LegalAI — Automated Indian Legal Corpus Expansion Engine"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate discovery and domain classification without downloading or modifying database."
    )
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Execute controlled pilot ingestion of 10-12 high-value Central Acts."
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an interrupted run, skipping already indexed documents."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display persistent state tracking summary and total corpus counts."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="Maximum number of Acts to process in this run (default: 12)."
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/legalai_indian_legal_knowledge.db",
        help="Path to Indian Legal Knowledge SQLite database."
    )

    args = parser.parse_args()

    pipeline = AutomatedCorpusExpansionPipeline(db_path=args.db_path)

    if args.stats:
        counts = pipeline.tracker.get_counts()
        total_docs = pipeline.db.get_document_count()
        total_chunks = pipeline.db.get_chunk_count()

        print("============================================================")
        print("LEGALAI — CORPUS EXPANSION PERSISTENT STATE")
        print("============================================================")
        print(f"Database Path:           {args.db_path}")
        print(f"Total Documents in DB:   {total_docs}")
        print(f"Total Chunks in DB:      {total_chunks}")
        print("Ingestion State Tracker:")
        for status_name, count in counts.items():
            print(f"  - {status_name:<15}: {count}")
        print("============================================================")
        sys.exit(0)

    if args.dry_run:
        print("Executing DRY RUN for Indian Central Acts Pilot...")
        summary = pipeline.run_pilot_expansion(dry_run=True, limit=args.limit)
        print(summary.to_report())
        sys.exit(0)

    if args.pilot or args.resume:
        mode_str = "PILOT INGESTION" if args.pilot else "RESUME INGESTION"
        print(f"Executing {mode_str} for Indian Central Acts (Limit: {args.limit})...")
        summary = pipeline.run_pilot_expansion(dry_run=False, limit=args.limit)
        print(summary.to_report())
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
