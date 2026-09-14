"""
src/case_rag/document_processor.py

Multi-format case document parser.
Supports PDF (page-by-page via PyMuPDF/fitz with pypdf fallback), DOCX, and TXT.
CRITICAL RULE: Never flattens PDFs into a single anonymous string; strictly preserves page provenance.
"""

import os
from pathlib import Path
from typing import List, Optional

from .models import ExtractedPage


class DocumentProcessor:
    """Extracts text page-by-page from case documents while preserving physical structure."""

    @classmethod
    def process_file(cls, file_path: str) -> List[ExtractedPage]:
        """Parses a document file and returns a list of ExtractedPage objects."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            return cls._process_pdf(str(path))
        elif ext in [".docx", ".doc"]:
            return cls._process_docx(str(path))
        elif ext in [".txt", ".md", ".text"]:
            return cls._process_txt(str(path))
        else:
            # Fallback to plain text read
            return cls._process_txt(str(path))

    @classmethod
    def _process_pdf(cls, file_path: str) -> List[ExtractedPage]:
        """Extracts text page-by-page from PDF."""
        pages: List[ExtractedPage] = []

        # Attempt 1: PyMuPDF (fitz) - fast, accurate layout extraction
        try:
            import fitz
            doc = fitz.open(file_path)
            for page_idx in range(len(doc)):
                page_num = page_idx + 1
                try:
                    page = doc[page_idx]
                    text = page.get_text("text").strip()
                    pages.append(ExtractedPage(
                        page_number=page_num,
                        text=text,
                        char_count=len(text),
                        has_error=False
                    ))
                except Exception as page_err:
                    pages.append(ExtractedPage(
                        page_number=page_num,
                        text="",
                        char_count=0,
                        has_error=True,
                        error_message=f"Error extracting page {page_num}: {str(page_err)}"
                    ))
            doc.close()
            if pages:
                return pages
        except ImportError:
            pass
        except Exception as fitz_err:
            print(f"[DocumentProcessor] PyMuPDF failed on {file_path}: {fitz_err}, trying pypdf...")

        # Attempt 2: pypdf fallback
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                page_num = page_idx + 1
                try:
                    text = (page.extract_text() or "").strip()
                    pages.append(ExtractedPage(
                        page_number=page_num,
                        text=text,
                        char_count=len(text),
                        has_error=False
                    ))
                except Exception as page_err:
                    pages.append(ExtractedPage(
                        page_number=page_num,
                        text="",
                        char_count=0,
                        has_error=True,
                        error_message=f"Error extracting page {page_num}: {str(page_err)}"
                    ))
            return pages
        except Exception as pypdf_err:
            print(f"[DocumentProcessor] pypdf failed on {file_path}: {pypdf_err}")
            return [ExtractedPage(
                page_number=1,
                text="",
                char_count=0,
                has_error=True,
                error_message=f"PDF extraction failed: {str(pypdf_err)}"
            )]

    @classmethod
    def _process_docx(cls, file_path: str) -> List[ExtractedPage]:
        """Extracts text from DOCX document. Paragraphs are grouped into synthetic pages."""
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)

            # Split into ~3000-character pages if lengthy, or 1 page if short
            if not full_text:
                return [ExtractedPage(page_number=1, text="", char_count=0)]

            chunk_size = 3000
            pages = []
            for i in range(0, len(full_text), chunk_size):
                page_num = (i // chunk_size) + 1
                slice_text = full_text[i:i + chunk_size].strip()
                pages.append(ExtractedPage(
                    page_number=page_num,
                    text=slice_text,
                    char_count=len(slice_text)
                ))
            return pages
        except Exception as docx_err:
            return [ExtractedPage(
                page_number=1,
                text="",
                char_count=0,
                has_error=True,
                error_message=f"DOCX extraction failed: {str(docx_err)}"
            )]

    @classmethod
    def _process_txt(cls, file_path: str) -> List[ExtractedPage]:
        """Extracts text from plain text files."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            if not content.strip():
                return [ExtractedPage(page_number=1, text="", char_count=0)]

            # Check for explicit page break markers (e.g. form feed \f or --- Page X ---)
            if "\f" in content:
                raw_pages = content.split("\f")
                pages = []
                for idx, p in enumerate(raw_pages):
                    t = p.strip()
                    if t:
                        pages.append(ExtractedPage(page_number=idx + 1, text=t, char_count=len(t)))
                if pages:
                    return pages

            # Default: page blocks of ~3000 characters
            chunk_size = 3000
            pages = []
            for i in range(0, len(content), chunk_size):
                page_num = (i // chunk_size) + 1
                slice_text = content[i:i + chunk_size].strip()
                pages.append(ExtractedPage(
                    page_number=page_num,
                    text=slice_text,
                    char_count=len(slice_text)
                ))
            return pages
        except Exception as txt_err:
            return [ExtractedPage(
                page_number=1,
                text="",
                char_count=0,
                has_error=True,
                error_message=f"TXT extraction failed: {str(txt_err)}"
            )]
