"""Official Authoritative Indian Legal Source Providers.

Strictly interfaces with official Indian Government, Legislative, and Judicial portals.
DO NOT fabricate endpoints or invent fake APIs.
If an official source cannot be retrieved automatically due to CAPTCHA or lack of API,
it is explicitly flagged as MANUAL_SOURCE_REQUIRED.
"""

import os
import re
import time
import random
import hashlib
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from ..models import IndianDocumentType, AuthorityTier, IndianJurisdictionLevel


class LegalSourceProvider(ABC):
    """Abstract base provider for authoritative Indian legal repositories."""

    USER_AGENT = "LegalAI-IndianLawyerBot/1.0 (Academic & Legal Research; contact@legalai.in)"

    def __init__(self, source_id: str, authority_name: str, official_domain: str):
        self.source_id = source_id
        self.authority_name = authority_name
        self.official_domain = official_domain

    @abstractmethod
    def fetch_document(self, identifier: str, **kwargs) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """Fetches document by official handle/identifier. Returns: (success, content/filepath, sha256_hash, error_or_status)"""
        pass

    @abstractmethod
    def verify_provenance(self, url: str) -> bool:
        """Verifies that the URL belongs strictly to the authoritative domain."""
        pass


class IndiaCodeProvider(LegalSourceProvider):
    """Authoritative provider for Central & State Acts from India Code (indiacode.nic.in / indiacode.gov.in)."""

    ALLOWED_DOMAINS = ("indiacode.nic.in", "indiacode.gov.in")

    def __init__(self, storage_dir: str = "data/legal_corpus/raw/central_acts"):
        super().__init__("SRC_INDIA_CODE", "India Code Digital Repository", "indiacode.nic.in")
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._last_request_time = 0.0

    def verify_provenance(self, url: str) -> bool:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        return any(hostname == d or hostname.endswith("." + d) for d in self.ALLOWED_DOMAINS)

    def _polite_delay(self, min_s: float = 0.5, max_s: float = 1.5):
        elapsed = time.time() - self._last_request_time
        target = random.uniform(min_s, max_s)
        if elapsed < target:
            time.sleep(target - elapsed)
        self._last_request_time = time.time()

    def fetch_document(self, bitstream_url: str, filename_prefix: str = "act", max_retries: int = 3) -> Tuple[bool, str, Optional[str], Optional[str]]:
        if not self.verify_provenance(bitstream_url):
            return False, "", None, f"URL {bitstream_url} does not belong to authoritative India Code domain"

        target_file = os.path.join(self.storage_dir, f"{filename_prefix}.txt")
        target_pdf = os.path.join(self.storage_dir, f"{filename_prefix}.pdf")

        # If already preserved on disk, verify hash and return
        if os.path.exists(target_file) and os.path.getsize(target_file) > 100:
            with open(target_file, 'rb') as f:
                h = hashlib.sha256(f.read()).hexdigest()
            return True, target_file, h, "CACHED_LOCAL"

        self._polite_delay()
        req = urllib.request.Request(bitstream_url, headers={"User-Agent": self.USER_AGENT})

        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status != 200:
                        return False, "", None, f"HTTP status {resp.status}"
                    data = resp.read()
                    h = hashlib.sha256(data).hexdigest()
                    content_type = resp.headers.get("Content-Type", "")

                    if "pdf" in content_type.lower() or data.startswith(b"%PDF"):
                        with open(target_pdf, "wb") as f:
                            f.write(data)
                        return True, target_pdf, h, "DOWNLOADED_PDF"
                    else:
                        text = data.decode("utf-8", errors="replace")
                        with open(target_file, "w", encoding="utf-8") as f:
                            f.write(text)
                        return True, target_file, h, "DOWNLOADED_TEXT"
            except Exception as e:
                if attempt == max_retries:
                    return False, "", None, f"Fetch failed after {max_retries} attempts: {str(e)}"
                time.sleep(attempt * 2)

        return False, "", None, "FETCH_FAILED"


class GazetteProvider(LegalSourceProvider):
    """Authoritative provider for Gazette of India (egazette.gov.in)."""

    ALLOWED_DOMAINS = ("egazette.gov.in", "egazette.nic.in")

    def __init__(self, storage_dir: str = "data/legal_corpus/raw/gazette"):
        super().__init__("SRC_EGAZETTE", "The Gazette of India", "egazette.gov.in")
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def verify_provenance(self, url: str) -> bool:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        return any(hostname == d or hostname.endswith("." + d) for d in self.ALLOWED_DOMAINS)

    def fetch_document(self, identifier: str, **kwargs) -> Tuple[bool, str, Optional[str], Optional[str]]:
        # Gazette requires authenticated session / dynamic token or manual download for most notifications
        # Never fabricate endpoints; flag for manual review if automated endpoint is unavailable
        return False, "", None, "MANUAL_SOURCE_REQUIRED: Official eGazette requires manual verification or direct gazette bitstream link."


class SupremeCourtProvider(LegalSourceProvider):
    """Authoritative provider for Supreme Court decisions (e-SCR / judgments.ecourts.gov.in)."""

    ALLOWED_DOMAINS = ("judgments.ecourts.gov.in", "main.sci.gov.in", "sci.gov.in")

    def __init__(self, storage_dir: str = "data/legal_corpus/raw/judgments"):
        super().__init__("SRC_SCI_ESCR", "Supreme Court of India e-SCR", "judgments.ecourts.gov.in")
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def verify_provenance(self, url: str) -> bool:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        return any(hostname == d or hostname.endswith("." + d) for d in self.ALLOWED_DOMAINS)

    def fetch_document(self, identifier: str, **kwargs) -> Tuple[bool, str, Optional[str], Optional[str]]:
        return False, "", None, "MANUAL_SOURCE_REQUIRED: Supreme Court judgments require verified e-SCR PDF or certified official transcript."


class HighCourtProvider(LegalSourceProvider):
    """Authoritative provider for official High Court websites."""

    def __init__(self, court_domain: str, storage_dir: str = "data/legal_corpus/raw/judgments"):
        super().__init__("SRC_HIGH_COURT", "Official High Court Repository", court_domain)
        self.storage_dir = storage_dir

    def verify_provenance(self, url: str) -> bool:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        return hostname.endswith(".gov.in") or hostname.endswith(".nic.in")

    def fetch_document(self, identifier: str, **kwargs) -> Tuple[bool, str, Optional[str], Optional[str]]:
        return False, "", None, "MANUAL_SOURCE_REQUIRED: High Court certified records require verified judicial copy."


class GovernmentNotificationProvider(LegalSourceProvider):
    """Authoritative provider for Central Government subordinate rules and notifications."""

    def __init__(self, ministry_domain: str = "mca.gov.in", storage_dir: str = "data/legal_corpus/raw/notifications"):
        super().__init__("SRC_GOV_NOTIF", "Official Government Subordinate Legislation", ministry_domain)
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def verify_provenance(self, url: str) -> bool:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        return hostname.endswith(".gov.in") or hostname.endswith(".nic.in")

    def fetch_document(self, identifier: str, **kwargs) -> Tuple[bool, str, Optional[str], Optional[str]]:
        return False, "", None, "MANUAL_SOURCE_REQUIRED: Ministerial subordinate notifications require official Gazette S.O. publication."
