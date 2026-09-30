"""Safe, rate-limited, resumable document fetcher for India Code repositories."""

import os
import time
import random
import hashlib
import json
import logging
import urllib.request
import urllib.error
from typing import Tuple, Optional, Dict, Any
from .models import DiscoveredAct

logger = logging.getLogger("IndiaCodeFetcher")

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


class IndiaCodeFetcher:
    """Acquires statutory documents from India Code with strict rate limiting, exponential backoff, and hash validation."""

    USER_AGENT = "LegalAI-IndianLawyerBot/1.0 (Academic & Legal Research; contact@legalai.in)"
    DEFAULT_STORAGE_DIR = "data/raw/central_acts"

    def __init__(
        self,
        storage_dir: str = DEFAULT_STORAGE_DIR,
        min_rate_delay: float = 0.5,
        max_rate_delay: float = 1.5,
        timeout: int = 40,
        max_retries: int = 3
    ):
        self.storage_dir = storage_dir
        self.min_rate_delay = min_rate_delay
        self.max_rate_delay = max_rate_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_request_time = 0.0
        os.makedirs(self.storage_dir, exist_ok=True)

    def _polite_delay(self):
        """Ensures respectful request throttling to avoid overloading government servers."""
        elapsed = time.time() - self._last_request_time
        target_delay = random.uniform(self.min_rate_delay, self.max_rate_delay)
        if elapsed < target_delay:
            time.sleep(target_delay - elapsed)
        self._last_request_time = time.time()

    def fetch_act(self, act: DiscoveredAct) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Fetches an official Act document directly from India Code via HTTP.
        Returns:
            (success: bool, filepath_or_error: str, content_hash: Optional[str], error_msg: Optional[str])
        """
        safe_prefix = act.act_id.lower()
        target_filename = f"{safe_prefix}.txt"
        target_path = os.path.join(self.storage_dir, target_filename)
        meta_path = f"{target_path}.meta.json"

        # Check local cache first
        if os.path.exists(target_path) and os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                with open(target_path, "rb") as f:
                    content_bytes = f.read()
                calc_hash = hashlib.sha256(content_bytes).hexdigest()
                
                # Cache hit requires genuine official acquisition metadata
                if (
                    calc_hash == meta.get("sha256_hash")
                    and len(content_bytes) > 500
                    and meta.get("http_status") == 200
                    and meta.get("acquisition_method") == "OFFICIAL_INDIA_CODE_HTTP_FETCH"
                ):
                    logger.info(f"Local official cache hit for {act.short_title} ({calc_hash[:8]})")
                    return True, target_path, calc_hash, None
            except Exception as e:
                logger.warning(f"Cache validation error for {act.short_title}, re-fetching: {e}")

        # Choose acquisition target:
        # Prefer full PDF if available and fitz is installed for Acts like Companies Act, or text_url
        download_url = act.text_url or act.pdf_url or act.handle_url
        
        # If Companies Act, the official PDF bitstream has all 470 sections (370 pages)
        if act.act_id == "COMPANIES_ACT_2013" and act.pdf_url and HAS_PYMUPDF:
            download_url = act.pdf_url

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/plain, application/pdf, */*"
        }

        for attempt in range(1, self.max_retries + 1):
            self._polite_delay()
            try:
                logger.info(f"Fetching {act.short_title} from {download_url} (Attempt {attempt}/{self.max_retries})...")
                req = urllib.request.Request(download_url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    http_status = resp.status
                    content_type = resp.headers.get("Content-Type", "")
                    raw_payload = resp.read()

                # Basic integrity checks
                if len(raw_payload) < 100:
                    raise ValueError(f"Payload too small ({len(raw_payload)} bytes)")

                if b"404 Not Found" in raw_payload or b"Internal Server Error" in raw_payload:
                    raise ValueError("Received HTTP error page content from server")

                # Extract text content
                total_pages = 0
                if download_url.endswith(".pdf") or "application/pdf" in content_type.lower() or raw_payload.startswith(b"%PDF"):
                    if not HAS_PYMUPDF:
                        raise RuntimeError("PyMuPDF (fitz) is required to process official PDF statutory documents.")
                    doc = fitz.open(stream=raw_payload, filetype="pdf")
                    total_pages = len(doc)
                    pages_text = [page.get_text() for page in doc]
                    extracted_text = "\n".join(pages_text)
                    content_bytes = extracted_text.encode("utf-8")
                else:
                    extracted_text = raw_payload.decode("utf-8", errors="ignore")
                    content_bytes = raw_payload

                content_hash = hashlib.sha256(content_bytes).hexdigest()

                # Save raw document to disk
                with open(target_path, "wb") as f:
                    f.write(content_bytes)

                # Write metadata sidecar proving real HTTP acquisition
                sidecar = {
                    "act_id": act.act_id,
                    "act_name": act.act_name,
                    "short_title": act.short_title,
                    "source_url": act.handle_url,
                    "download_url": download_url,
                    "http_status": http_status,
                    "content_type": content_type,
                    "sha256_hash": content_hash,
                    "file_size_bytes": len(content_bytes),
                    "total_pages": total_pages,
                    "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "acquisition_method": "OFFICIAL_INDIA_CODE_HTTP_FETCH",
                    "user_agent": self.USER_AGENT,
                    "is_full_document": True
                }
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(sidecar, f, indent=2)

                logger.info(f"Acquired {act.short_title}: {len(content_bytes):,} bytes | SHA-256: {content_hash[:12]}")
                return True, target_path, content_hash, None

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed for {act.short_title}: {e}")
                if attempt < self.max_retries:
                    backoff = (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(backoff)
                else:
                    return False, "", None, f"Fetch failed after {self.max_retries} attempts: {str(e)}"

        return False, "", None, "Unknown acquisition error"
