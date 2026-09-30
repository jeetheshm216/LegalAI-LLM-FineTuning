"""Pipeline orchestrating discovery, safe acquisition, versioning, parsing, and indexing of Indian Acts."""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import IngestionStatus, DiscoveredAct, IngestionSummary
from .discovery import IndiaCodeDiscoveryEngine
from .fetcher import IndiaCodeFetcher
from .state_tracker import IngestionStateTracker
from .versioner import DocumentVersionManager
from .classifier import IndianDomainClassifier
from .pilot_data import PILOT_ACTS_METADATA

from ..models import (
    IndianLegalDocument,
    IndianLegalChunk,
    IndianDocumentType,
    IndianJurisdictionLevel,
    AuthorityTier,
    TemporalStatus
)
from ..indexing.database import IndianLegalDatabaseManager
from ..parsers.statute_parser import IndianStatuteParser

logger = logging.getLogger("CorpusExpansionPipeline")


class AutomatedCorpusExpansionPipeline:
    """End-to-end pipeline for discovering, acquiring, versioning, parsing, and indexing Indian Central Acts."""

    def __init__(
        self,
        db_path: str = "data/legalai_indian_legal_knowledge.db",
        raw_storage_dir: str = "data/raw/central_acts"
    ):
        self.db = IndianLegalDatabaseManager(db_path=db_path)
        self.tracker = IngestionStateTracker(db_path=db_path)
        self.discovery = IndiaCodeDiscoveryEngine()
        self.fetcher = IndiaCodeFetcher(storage_dir=raw_storage_dir)
        self.versioner = DocumentVersionManager(self.db)
        self.classifier = IndianDomainClassifier()
        self.parser = IndianStatuteParser()

    def discover_acts(self, limit: Optional[int] = None) -> List[DiscoveredAct]:
        """Discovers available Central Acts and records them into the state tracker."""
        discovered = self.discovery.discover_central_acts(limit=limit)
        for act in discovered:
            self.tracker.record_discovered(act)
        return discovered

    def process_single_act(self, act: DiscoveredAct, dry_run: bool = False) -> Dict[str, Any]:
        """
        Processes a single discovered Act through the genuine pipeline:
        Check State -> HTTP Fetch from India Code -> Hash -> Version -> Classify -> Parse -> Validate -> Index.
        """
        # Ensure discovered state is recorded
        self.tracker.record_discovered(act)

        # 1. Check if already indexed
        if self.tracker.is_already_indexed(act.handle_url):
            logger.info(f"Skipping already indexed Act: {act.short_title}")
            return {
                "status": IngestionStatus.SKIPPED,
                "reason": "Already indexed in database",
                "act_id": act.act_id,
                "title": act.short_title,
                "chunks": 0
            }

        if dry_run:
            domain, conf = self.classifier.classify_act(act.act_name)
            return {
                "status": IngestionStatus.QUEUED,
                "reason": "Dry-run plan generated",
                "act_id": act.act_id,
                "title": act.short_title,
                "predicted_domain": domain,
                "confidence": conf,
                "chunks": 0
            }

        self.tracker.update_status(act.handle_url, IngestionStatus.DOWNLOADING)

        # 2. Acquire Content from Official India Code Endpoint (GENUINE HTTP FETCH)
        success, path_or_err, content_hash, err = self.fetcher.fetch_act(act)

        if not success:
            fail_reason = err or "Official acquisition failed"
            self.tracker.update_status(act.handle_url, IngestionStatus.FAILED, error_message=fail_reason)
            return {
                "status": IngestionStatus.FAILED,
                "reason": fail_reason,
                "act_id": act.act_id,
                "title": act.short_title,
                "stage": "ACQUISITION",
                "chunks": 0
            }

        try:
            with open(path_or_err, "r", encoding="utf-8", errors="ignore") as f:
                statutory_text = f.read()
        except Exception as e:
            fail_reason = f"Failed reading downloaded file: {e}"
            self.tracker.update_status(act.handle_url, IngestionStatus.FAILED, error_message=fail_reason)
            return {
                "status": IngestionStatus.FAILED,
                "reason": fail_reason,
                "act_id": act.act_id,
                "title": act.short_title,
                "stage": "READ_ACQUIRED_FILE",
                "chunks": 0
            }

        if not statutory_text or len(statutory_text) < 500:
            fail_reason = f"Acquired statutory text too small ({len(statutory_text)} characters)"
            self.tracker.update_status(act.handle_url, IngestionStatus.FAILED, error_message=fail_reason)
            return {
                "status": IngestionStatus.FAILED,
                "reason": fail_reason,
                "act_id": act.act_id,
                "title": act.short_title,
                "stage": "EMPTY_PAYLOAD",
                "chunks": 0
            }

        self.tracker.update_status(act.handle_url, IngestionStatus.DOWNLOADED, content_hash=content_hash)

        # 3. Version Detection
        version_id, temporal_status, is_new_version, v_note = self.versioner.evaluate_document_version(
            act_prefix=act.act_id,
            new_content_hash=content_hash,
            amendment_date=str(act.enactment_year) if act.enactment_year else None
        )

        # 4. Domain Classification
        domain, _ = self.classifier.classify_act(act.act_name, statutory_text[:2000])

        # 5. Create Document Metadata
        commencement = PILOT_ACTS_METADATA.get(act.act_id, {}).get("commencement_date")
        doc_id = f"DOC_{act.act_id}" if not is_new_version else f"DOC_{act.act_id}_{version_id}"
        document = IndianLegalDocument(
            document_id=doc_id,
            title=act.act_name,
            document_type=IndianDocumentType.ACT,
            jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
            country="India",
            act_prefix=act.act_id,
            act_number=act.act_number,
            enactment_date=f"{act.enactment_year}-01-01" if act.enactment_year else None,
            commencement_date=commencement,
            legal_domain=domain,
            authority_tier=AuthorityTier.TIER_1_PRIMARY,
            temporal_status=temporal_status,
            effective_from=commencement,
            official_source_url=act.handle_url,
            source_id="SRC_INDIA_CODE",
            created_at=datetime.now().isoformat()
        )

        # 6. Parse Provisions
        self.tracker.update_status(act.handle_url, IngestionStatus.PARSED)
        chunks = self.parser.parse_provisions(
            document=document,
            raw_text=statutory_text,
            default_chapter=f"Provisions of {act.short_title}"
        )

        # 7. Validation
        if not chunks:
            fail_reason = "PARSER_FAILURE: No structured sections could be extracted from statutory text."
            self.tracker.update_status(act.handle_url, IngestionStatus.FAILED, error_message=fail_reason)
            return {
                "status": IngestionStatus.FAILED,
                "reason": fail_reason,
                "act_id": act.act_id,
                "title": act.short_title,
                "stage": "PARSING_VALIDATION",
                "chunks": 0
            }

        self.tracker.update_status(act.handle_url, IngestionStatus.VALIDATED)

        # 8. Index into Database
        self.db.upsert_document(document)
        indexed_chunks_count = 0
        for chunk in chunks:
            chunk.authority_tier = document.authority_tier
            chunk.temporal_status = document.temporal_status
            chunk.legal_domain = document.legal_domain
            chunk.official_source_url = document.official_source_url
            if self.db.upsert_chunk(chunk):
                indexed_chunks_count += 1

        self.tracker.update_status(
            source_url=act.handle_url,
            status=IngestionStatus.INDEXED,
            content_hash=content_hash,
            chunks_created=len(chunks),
            version_id=version_id
        )

        logger.info(f"Successfully indexed {act.short_title}: {len(chunks)} chunks.")
        return {
            "status": IngestionStatus.INDEXED,
            "act_id": act.act_id,
            "title": act.short_title,
            "act_prefix": act.act_id,
            "chunks": len(chunks),
            "version": version_id,
            "domain": domain,
            "content_hash": content_hash[:12]
        }

    def run_pilot_expansion(self, dry_run: bool = False, limit: Optional[int] = 12) -> IngestionSummary:
        """Executes the controlled Central Acts pilot run."""
        summary = IngestionSummary()
        discovered_acts = self.discover_acts(limit=limit)
        summary.discovered = len(discovered_acts)

        for act in discovered_acts:
            # Check already indexed
            if self.tracker.is_already_indexed(act.handle_url):
                summary.already_indexed += 1
                summary.skipped += 1
                continue

            summary.new_documents += 1
            res = self.process_single_act(act, dry_run=dry_run)

            if res["status"] == IngestionStatus.INDEXED:
                summary.downloaded += 1
                summary.parsed += 1
                summary.validated += 1
                summary.indexed += 1
                summary.chunks_added += res["chunks"]
                summary.indexed_acts.append(res)
            elif res["status"] == IngestionStatus.QUEUED:
                pass
            elif res["status"] == IngestionStatus.SKIPPED:
                summary.skipped += 1
            elif res["status"] == IngestionStatus.FAILED:
                summary.failed += 1
                summary.failures.append(res)

        return summary
