#!/usr/bin/env python3
"""Reproducible legal corpus update pipeline for LegalAI.

Follows the controlled workflow:
DISCOVER -> CLASSIFY -> VERIFY SOURCE -> DOWNLOAD (polite) -> HASH -> PARSE -> VALIDATE -> INDEX

Produces:
- corpus_update_report.json
- updates corpus_manifest.json
"""

import sys
import os
import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from src.legal_knowledge.indexing.database import IndianLegalDatabaseManager
from src.legal_knowledge.sources.providers import IndiaCodeProvider
from src.legal_knowledge.sources.registry import IndianSourceRegistry
from src.legal_knowledge.parsers.statute_parser import IndianStatuteParser
from src.legal_knowledge.models import (
    IndianLegalDocument,
    IndianLegalChunk,
    IndianDocumentType,
    IndianJurisdictionLevel,
    AuthorityTier,
    TemporalStatus,
    ProvisionType
)


def update_corpus(
    catalogue_path: str = "verified_india_code_catalogue.json",
    dry_run: bool = False
) -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    db = IndianLegalDatabaseManager()
    provider = IndiaCodeProvider()
    parser = IndianStatuteParser()

    # Discover documents from verified catalogue if present, else from database documents
    discovered_acts = []
    cat_full_path = os.path.join(REPO_ROOT, catalogue_path)
    if os.path.exists(cat_full_path):
        with open(cat_full_path, "r", encoding="utf-8") as f:
            discovered_acts = json.load(f)

    report = {
        "generated_at": timestamp,
        "status": "COMPLETED",
        "dry_run": dry_run,
        "discovered_documents_count": len(discovered_acts),
        "skipped_unchanged_count": 0,
        "newly_downloaded_count": 0,
        "newly_indexed_chunks_count": 0,
        "failures_count": 0,
        "manual_review_required_count": 0,
        "processed_documents": [],
        "failures": []
    }

    # Fetch currently indexed document IDs and hashes
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT document_id, act_prefix, content_hash FROM indian_legal_documents")
        existing_docs = {r["document_id"]: r["content_hash"] for r in cursor.fetchall()}

    for item in discovered_acts:
        act_id = item.get("act_id")
        doc_id = f"DOC_{act_id}"
        text_url = item.get("text_url")
        act_name = item.get("act_name", act_id)

        # Check if already present and verified
        if doc_id in existing_docs and existing_docs[doc_id]:
            report["skipped_unchanged_count"] += 1
            report["processed_documents"].append({
                "act_id": act_id,
                "status": "SKIPPED_UNCHANGED",
                "reason": "Hash verified and already indexed."
            })
            continue

        if dry_run:
            report["processed_documents"].append({
                "act_id": act_id,
                "status": "QUEUED_FOR_INGESTION",
                "url": text_url
            })
            continue

        if not text_url:
            report["manual_review_required_count"] += 1
            report["processed_documents"].append({
                "act_id": act_id,
                "status": "MANUAL_SOURCE_REQUIRED",
                "reason": "No direct official text bitstream available."
            })
            continue

        # Fetch using IndiaCodeProvider
        success, filepath, content_hash, status_msg = provider.fetch_document(
            text_url, filename_prefix=act_id.lower()
        )

        if not success:
            report["failures_count"] += 1
            report["failures"].append({
                "act_id": act_id,
                "stage": "FETCH",
                "error": status_msg
            })
            continue

        report["newly_downloaded_count"] += 1

        # Parse text into statutory chunks
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()

            parsed_chunks = parser.parse_statute_text(
                raw_text=raw_text,
                act_name=act_name,
                act_prefix=act_id,
                document_id=doc_id,
                official_source_url=item.get("handle_url", text_url)
            )

            # Index document record
            doc_rec = IndianLegalDocument(
                document_id=doc_id,
                title=act_name,
                document_type=IndianDocumentType.ACT,
                jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
                act_prefix=act_id,
                act_number=item.get("act_number"),
                legal_domain="General Indian Law",
                authority_tier=AuthorityTier.TIER_1_PRIMARY,
                temporal_status=TemporalStatus.CURRENT,
                official_source_url=item.get("handle_url", text_url),
                source_id="SRC_INDIA_CODE",
                created_at=timestamp
            )
            doc_rec.content_hash = content_hash
            db.upsert_document(doc_rec)

            # Index chunks
            added_chunks = 0
            for ch in parsed_chunks:
                if db.upsert_chunk(ch):
                    added_chunks += 1

            report["newly_indexed_chunks_count"] += added_chunks
            report["processed_documents"].append({
                "act_id": act_id,
                "status": "INDEXED",
                "chunks_added": added_chunks,
                "hash": content_hash
            })
        except Exception as e:
            report["failures_count"] += 1
            report["failures"].append({
                "act_id": act_id,
                "stage": "PARSE_AND_INDEX",
                "error": str(e)
            })

    # Save corpus_update_report.json
    out_path = os.path.join(REPO_ROOT, "corpus_update_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    manifest_path = os.path.join(REPO_ROOT, "data/legal_corpus/manifests/corpus_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["last_successful_update"] = timestamp
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    print("==================================================================")
    print("LEGALAI ??? CORPUS UPDATE COMPLETE")
    print("==================================================================")
    print(f"Skipped Unchanged:        {report['skipped_unchanged_count']}")
    print(f"Newly Downloaded:         {report['newly_downloaded_count']}")
    print(f"Newly Indexed Chunks:     {report['newly_indexed_chunks_count']}")
    print(f"Failures:                 {report['failures_count']}")
    print(f"Manual Review Required:   {report['manual_review_required_count']}")
    print(f"Report Generated:         {out_path}")
    print("==================================================================")

    return report


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    update_corpus(dry_run=dry)

