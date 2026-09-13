"""Text extraction and normalization pipeline for official Indian Bare Act PDFs."""

import os
import re
import unicodedata
from typing import Dict, Any, Tuple
import pymupdf


def clean_line_noise(line: str) -> str:
    """Clean running gazette headers, page numbers, and registration marks."""
    # Running gazette header
    if re.search(r'THE GAZETTE OF INDIA\s*:\s*EXTRAORDINARY', line, re.IGNORECASE):
        return ""
    if re.search(r'\[PART II\s*—\s*SEC\.\s*1\]', line, re.IGNORECASE):
        return ""
    if re.search(r'^\s*\d+\s*$', line):  # Isolated page number
        return ""
    if re.search(r'REGISTERED NO\.\s*DL—', line, re.IGNORECASE):
        return ""
    return line


def normalize_text(text: str) -> str:
    """Normalize unicode characters, quotes, hyphens, and whitespace."""
    # NFKC unicode normalization
    text = unicodedata.normalize("NFKC", text)
    # Standardize curly quotes and apostrophes
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    # Standardize long dashes/hyphens
    text = text.replace("—", "—").replace("–", "–")
    # Remove null bytes
    text = text.replace("\x00", "")
    return text


def extract_act_text(
    pdf_path: str,
    output_processed_path: str,
    start_page: int = 1,
    act_name: str = ""
) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts enactment text from official Bare Act PDF using PyMuPDF.
    
    Args:
        pdf_path: Path to the raw PDF file.
        output_processed_path: Path to save the normalized text.
        start_page: 1-indexed page where the actual statutory enactment begins.
        act_name: Canonical Act name.
        
    Returns:
        Tuple of (normalized_text, extraction_stats)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Source PDF not found at: {pdf_path}")
        
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    
    pages_extracted = 0
    extracted_blocks = []
    
    for p in range(start_page - 1, total_pages):
        page = doc[p]
        page_text = page.get_text("text")
        
        cleaned_lines = []
        for line in page_text.splitlines():
            cleaned = clean_line_noise(line)
            if cleaned:
                cleaned_lines.append(cleaned)
                
        page_normalized = "\n".join(cleaned_lines)
        page_normalized = normalize_text(page_normalized)
        extracted_blocks.append(page_normalized)
        pages_extracted += 1
        
    full_text = "\n\n".join(extracted_blocks)
    
    os.makedirs(os.path.dirname(output_processed_path), exist_ok=True)
    with open(output_processed_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    stats = {
        "act_name": act_name,
        "source_pdf": pdf_path,
        "total_pdf_pages": total_pages,
        "start_page": start_page,
        "pages_extracted": pages_extracted,
        "total_characters": len(full_text),
        "total_words": len(full_text.split()),
        "output_path": output_processed_path
    }
    
    return full_text, stats
