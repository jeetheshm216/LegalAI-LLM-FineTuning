"""Statutory Section-Aware Parser for Indian Bare Acts.

Preserves exact statutory hierarchy:
Act -> Chapter -> Section -> Subsection -> Proviso -> Explanation -> Illustration
"""

import re
import unicodedata
from typing import List, Dict, Any, Tuple


class StatutoryParser:
    """Parses normalized statutory enactments into canonical sections and chunks."""

    def __init__(self, act_name: str, act_number: str, act_type: str, act_prefix: str):
        self.act_name = act_name
        self.act_number = act_number
        self.act_type = act_type
        self.act_prefix = act_prefix

    def _extract_chapters(self, text: str) -> List[Dict[str, Any]]:
        """Identifies Chapter boundaries and titles."""
        # E.g., CHAPTER I \n PRELIMINARY or CHAPTER VI \n OF OFFENCES AFFECTING...
        chapter_pat = re.compile(
            r'(?:^|\n)\s*(CHAPTER\s+[IVXLCDM\d]+)\s*\n\s*([^\n]+)',
            re.MULTILINE
        )
        chapters = []
        for m in chapter_pat.finditer(text):
            chap_num = m.group(1).strip()
            chap_title = m.group(2).strip()
            if chap_title in ["SECTIONS", "PART", ""]:
                continue
            chapters.append({
                "chapter_id": chap_num,
                "chapter_title": chap_title,
                "start_idx": m.start()
            })
        return chapters

    def _get_chapter_for_pos(self, pos: int, chapters: List[Dict[str, Any]]) -> Dict[str, str]:
        """Finds the applicable chapter for a given character index."""
        current = {"chapter_id": "PRELIMINARY", "chapter_title": "Preliminary"}
        for ch in chapters:
            if ch["start_idx"] <= pos:
                current = {"chapter_id": ch["chapter_id"], "chapter_title": ch["chapter_title"]}
            else:
                break
        return current

    def _clean_section_heading(self, header_line: str) -> Tuple[str, str]:
        """
        Extracts clean section title and separates it from the statutory text body.
        
        Example header_line:
        "Short title, commencement and application.––(1) This Act may be called..."
        returns ("Short title, commencement and application.", "(1) This Act may be called...")
        """
        # Split on dashes: .–– or .— or .– or . - or .  –
        dash_match = re.search(r'\.(?:––|—|–|-|\s+–|\s+—|\s+-)\s*', header_line)
        if dash_match:
            title = header_line[:dash_match.start() + 1].strip()
            body_start = header_line[dash_match.end():].strip()
            return title, body_start
            
        # Fallback: check for (1)
        sub_match = re.search(r'\s*\(\d+\)', header_line)
        if sub_match:
            title = header_line[:sub_match.start()].strip()
            body_start = header_line[sub_match.start():].strip()
            return title, body_start
            
        return header_line.strip(), ""

    def parse_enactment(
        self,
        full_text: str,
        total_sections: int,
        max_chunk_chars: int = 4000
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parses full enactment text into canonical sections and retrieval chunks.
        
        Returns:
            Tuple of (sections, chunks, parsing_stats)
        """
        normalized = unicodedata.normalize("NFKC", full_text)
        chapters = self._extract_chapters(normalized)
        
        section_spans = []
        pos = 0
        missing_sections = []
        
        for s in range(1, total_sections + 1):
            pat = re.compile(rf'(?:^|\n)\s*{s}\.\s*([^\n]+)', re.MULTILINE)
            m = pat.search(normalized, pos)
            if not m:
                pat2 = re.compile(rf'(?:^|\n)\s*{s}\.([^\n]+)', re.MULTILINE)
                m = pat2.search(normalized, pos)
                
            if m:
                section_spans.append({
                    "sec_num": s,
                    "start": m.start(),
                    "header_line": m.group(1).strip()
                })
                pos = m.start() + len(str(s)) + 2
            else:
                missing_sections.append(s)
                
        if missing_sections:
            raise ValueError(f"Parsing failed for {self.act_prefix}: Missing sections {missing_sections}")
            
        sections = []
        chunks = []
        
        for i, span in enumerate(section_spans):
            sec_num = span["sec_num"]
            start_idx = span["start"]
            
            if i + 1 < len(section_spans):
                end_idx = section_spans[i + 1]["start"]
            else:
                # Last section: cut before Schedules or Statement of Objects
                end_match = re.search(
                    r'(?:THE SCHEDULE|THE FIRST SCHEDULE|STATEMENT OF OBJECTS AND REASONS)',
                    normalized[start_idx:]
                )
                if end_match:
                    end_idx = start_idx + end_match.start()
                else:
                    end_idx = len(normalized)
                    
            raw_sec_text = normalized[start_idx:end_idx].strip()
            first_line = span["header_line"]
            sec_title, body_start = self._clean_section_heading(first_line)
            
            # Form clean complete section text
            # Ensure the section starts with "<sec_num>. <sec_title>"
            lines = raw_sec_text.splitlines()
            if lines:
                lines[0] = f"{sec_num}. {sec_title}"
                if body_start:
                    lines.insert(1, body_start)
            clean_sec_text = "\n".join(lines).strip()
            
            chap_info = self._get_chapter_for_pos(start_idx, chapters)
            
            sec_canonical_id = f"{self.act_prefix}_2023_SEC_{sec_num}"
            section_entry = {
                "section_id": sec_canonical_id,
                "act_name": self.act_name,
                "act_number": self.act_number,
                "act_type": self.act_type,
                "act_prefix": self.act_prefix,
                "section_number": str(sec_num),
                "section_title": sec_title,
                "chapter_id": chap_info["chapter_id"],
                "chapter_title": chap_info["chapter_title"],
                "text": clean_sec_text,
                "char_length": len(clean_sec_text),
                "word_count": len(clean_sec_text.split())
            }
            sections.append(section_entry)
            
            # Generate Chunks (Canonical retrieval unit)
            # Prepend contextual legal hierarchy header to ensure dense embeddings retain context
            context_header = (
                f"[{self.act_name} ({self.act_number}) | {chap_info['chapter_id']}: {chap_info['chapter_title']} | "
                f"Section {sec_num}: {sec_title}]\n"
            )
            
            if len(clean_sec_text) <= max_chunk_chars:
                canonical_chunk_id = sec_canonical_id
                chunk_entry = {
                    "chunk_id": canonical_chunk_id,
                    "section_id": sec_canonical_id,
                    "parent_section_id": sec_canonical_id,
                    "act_name": self.act_name,
                    "act_number": self.act_number,
                    "act_type": self.act_type,
                    "act_prefix": self.act_prefix,
                    "section_number": str(sec_num),
                    "section_title": sec_title,
                    "chapter_id": chap_info["chapter_id"],
                    "chapter_title": chap_info["chapter_title"],
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "content": context_header + clean_sec_text,
                    "raw_section_text": clean_sec_text
                }
                chunks.append(chunk_entry)
            else:
                # Sub-chunking long sections (preserving subsections/provisos)
                # Split along paragraphs or subsections: \n(?=\(\d+\))
                sub_parts = re.split(r'\n(?=\(\d+\))', clean_sec_text)
                sub_chunks_text = []
                curr_buf = ""
                
                for part in sub_parts:
                    if len(curr_buf) + len(part) < max_chunk_chars:
                        curr_buf += ("\n" if curr_buf else "") + part
                    else:
                        if curr_buf:
                            sub_chunks_text.append(curr_buf)
                        curr_buf = part
                if curr_buf:
                    sub_chunks_text.append(curr_buf)
                    
                total_c = len(sub_chunks_text)
                for c_idx, c_text in enumerate(sub_chunks_text, start=1):
                    chunk_id = f"{self.act_prefix}_2023_SEC_{sec_num}_CHUNK_{c_idx:02d}"
                    chunk_entry = {
                        "chunk_id": chunk_id,
                        "section_id": sec_canonical_id,
                        "parent_section_id": sec_canonical_id,
                        "act_name": self.act_name,
                        "act_number": self.act_number,
                        "act_type": self.act_type,
                        "act_prefix": self.act_prefix,
                        "section_number": str(sec_num),
                        "section_title": sec_title,
                        "chapter_id": chap_info["chapter_id"],
                        "chapter_title": chap_info["chapter_title"],
                        "chunk_index": c_idx,
                        "total_chunks": total_c,
                        "content": context_header + c_text,
                        "raw_section_text": clean_sec_text
                    }
                    chunks.append(chunk_entry)
                    
        stats = {
            "act_name": self.act_name,
            "act_prefix": self.act_prefix,
            "total_sections_expected": total_sections,
            "total_sections_parsed": len(sections),
            "total_chunks_created": len(chunks),
            "chapters_found": len(chapters),
            "missing_sections": missing_sections,
            "sub_chunked_sections": sum(1 for s in sections if s["char_length"] > max_chunk_chars)
        }
        
        return sections, chunks, stats
