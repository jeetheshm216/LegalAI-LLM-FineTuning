"""
src/case_rag/chunker.py

Page-aware text chunking for case documents.
Ensures every chunk preserves strict provenance:
case_id, document_id, document_name, document_type, page_number, chunk_index, chunk_id.
"""

import re
from typing import List, Dict, Any
from .models import ExtractedPage, DocumentChunk


class CaseDocumentChunker:
    """Splits extracted document pages into coherent chunks preserving page provenance."""

    def __init__(self, target_chunk_size: int = 1200, chunk_overlap: int = 200):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        pages: List[ExtractedPage],
        case_id: str,
        document_id: str,
        document_name: str,
        document_type: str = "Evidence"
    ) -> List[DocumentChunk]:
        """Chunks a document page-by-page. Chunks do not cross page boundaries to ensure citation accuracy."""
        all_chunks: List[DocumentChunk] = []

        for page in pages:
            if not page.text or page.has_error:
                continue

            page_text = page.text.strip()
            if not page_text:
                continue

            # If page is short enough, keep as single chunk
            if len(page_text) <= self.target_chunk_size:
                chunk_id = f"{document_id}-p{page.page_number}-c1"
                all_chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    case_id=case_id,
                    document_id=document_id,
                    document_name=document_name,
                    document_type=document_type,
                    page_number=page.page_number,
                    chunk_index=1,
                    text=page_text,
                    metadata={
                        "char_length": len(page_text),
                        "page_number": page.page_number,
                        "document_name": document_name,
                    }
                ))
                continue

            # Split by paragraphs or natural sentence breaks
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n+', page_text) if p.strip()]
            current_buffer: List[str] = []
            current_len = 0
            page_chunk_idx = 1

            for para in paragraphs:
                para_len = len(para)
                if current_len + para_len > self.target_chunk_size and current_buffer:
                    chunk_text = "\n\n".join(current_buffer).strip()
                    chunk_id = f"{document_id}-p{page.page_number}-c{page_chunk_idx}"
                    all_chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        case_id=case_id,
                        document_id=document_id,
                        document_name=document_name,
                        document_type=document_type,
                        page_number=page.page_number,
                        chunk_index=page_chunk_idx,
                        text=chunk_text,
                        metadata={
                            "char_length": len(chunk_text),
                            "page_number": page.page_number,
                            "document_name": document_name,
                        }
                    ))
                    page_chunk_idx += 1

                    # Retain last paragraph for overlap if within reasonable size
                    if current_buffer and len(current_buffer[-1]) < self.chunk_overlap:
                        current_buffer = [current_buffer[-1], para]
                        current_len = len(current_buffer[0]) + para_len + 2
                    else:
                        current_buffer = [para]
                        current_len = para_len
                else:
                    current_buffer.append(para)
                    current_len += para_len + 2

            # Remainder buffer
            if current_buffer:
                chunk_text = "\n\n".join(current_buffer).strip()
                chunk_id = f"{document_id}-p{page.page_number}-c{page_chunk_idx}"
                all_chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    case_id=case_id,
                    document_id=document_id,
                    document_name=document_name,
                    document_type=document_type,
                    page_number=page.page_number,
                    chunk_index=page_chunk_idx,
                    text=chunk_text,
                    metadata={
                        "char_length": len(chunk_text),
                        "page_number": page.page_number,
                        "document_name": document_name,
                    }
                ))

        return all_chunks
