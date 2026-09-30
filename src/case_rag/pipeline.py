import urllib.request
import json
"""
src/case_rag/pipeline.py

End-to-end Case Document RAG Pipeline.
Coordinates:
1. Case document ingestion & indexing
2. Case-isolated hybrid retrieval
3. Evidence sufficiency & empty-case checks
4. Grounded Case Analysis prompt formulation (Facts vs Inferences vs Gaps vs Contradictions)
5. Dynamic PEFT LoRA adapter switching to Case Analysis V1 (outputs/qwen14b-case-analysis-v1)
6. Optional statutory authority enrichment via existing Legal RAG
7. Document and page-level citation formatting
"""

import os
import re
import time
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("CaseRAGPipeline")

import torch
from .models import CaseDocument, DocumentChunk, CaseRetrievalResult, CaseAnalysisResult
from .document_processor import DocumentProcessor
from .chunker import CaseDocumentChunker
from .embeddings import CaseEmbedder
from .index import CaseRAGIndex
from .retriever import CaseRetriever


CASE_ANALYSIS_SYSTEM_PROMPT = """You are LegalAI Case Assistant, an advanced legal intelligence engine specialized in Indian litigation, evidence analysis, and case preparation.

You are assisting an advocate with a specific legal matter based strictly on uploaded case documents and verified case records.

STRICT OPERATIONAL PRINCIPLES:
1. ANSWER THE USER'S SPECIFIC QUESTION WITH ADAPTIVE FORMATTING:
   - Answer directly and precisely what the user asked.
   - Format the response according to the user's specific request (e.g. comparative table, bullet points, structured breakdown, or executive summary).
   - If the user asks to clarify, simplify, or reformat a previous response, use the conversation history to provide an improved, clearer explanation.
   - If the user asks about earlier messages or issues mentioned at the start of the chat, review the conversation history and report them accurately.

2. FACTUAL FIDELITY & STRICT ANTI-HALLUCINATION:
   - Base all factual statements strictly on the provided CASE MATERIAL and document excerpts.
   - Do NOT invent facts, documents, evidence, dates, times, witnesses, legal provisions, procedural events, arguments, outcomes, or case history.
   - If the available case documents do not establish a point, state clearly: "The currently available case documents do not establish this."

3. ADMISSIBILITY & JUDICIAL DECISION BOUNDARY:
   - State findings objectively: what is documented vs what requires advocate verification.

4. CITATIONS & PROVENANCE:
   - Cite every factual observation with its Document Name and Page Number where available (e.g., [Master_Charterparty_Agreement_Executed.pdf — Page 2]).
   - Distinguish Case Sources from Statutory Legal Authorities."""


EMPTY_CASE_RESPONSE = """### Insufficient Case Material for Analysis

No case documents have been uploaded or indexed for this matter yet.

To generate a grounded case analysis, please upload relevant case documents in the **Documents** manager:
- **Pleadings & Complaints**: FIR, Complaint petition, Plaint, Written Statement
- **Investigative Records**: ChargeSheet, Seizure memo, Panchnama, Site inspection plan
- **Evidentiary Records**: Witness statements, Depositions, Affidavits
- **Technical & Medical**: Medical report, Forensic reports, Expert opinions
- **Judicial Orders**: Bail orders, Interlocutory orders, Previous judgments

*Once documents are uploaded, LegalAI will index them with page-level provenance and analyze evidence gaps, contradictions, and hearing readiness.*"""


class CaseRAGPipeline:
    """Production Case Document RAG pipeline integrated with Case Analysis V1 adapter."""

    def __init__(
        self,
        index_db_path: str = "data/legalai_case_rag.db",
        base_pipeline=None,
        embedder: Optional[CaseEmbedder] = None
    ):
        self.index = CaseRAGIndex(index_db_path)
        self.processor = DocumentProcessor()
        self.chunker = CaseDocumentChunker()
        self.embedder = embedder or CaseEmbedder()
        self.retriever = CaseRetriever(self.index, self.embedder)
        self.base_pipeline = base_pipeline  # Instance of LegalAIRAGPipeline (holds Qwen base + V2 adapter)

    def _get_case_metadata(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Safely fetches case metadata from data/legalai_app.db cases table without modifying DB."""
        app_db = "data/legalai_app.db"
        if not os.path.exists(app_db):
            return None
        try:
            conn = sqlite3.connect(app_db)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, caseNumber, title, client, opposingParty, court, caseType, status, priority, description, matterSummary FROM cases WHERE id = ? OR caseNumber = ?",
                (case_id, case_id)
            )
            row = cur.fetchone()
            conn.close()
            if row:
                return {
                    "case_id": row[0],
                    "case_number": row[1],
                    "case_title": row[2],
                    "client": row[3],
                    "opposing_party": row[4],
                    "court": row[5],
                    "case_type": row[6],
                    "status": row[7],
                    "priority": row[8],
                    "description": row[9] or "",
                    "matter_summary": row[10] or row[9] or ""
                }
        except Exception as e:
            logger.warning(f"Error fetching case metadata for {case_id}: {e}")
        return None

    def ingest_document(
        self,
        file_path: str,
        case_id: str,
        document_id: Optional[str] = None,
        filename: Optional[str] = None,
        category: str = "Evidence",
        **kwargs
    ) -> CaseDocument:
        """Processes, chunks, embeds, and indexes a case document."""
        path = os.path.abspath(file_path)
        if not filename:
            filename = kwargs.get("document_name") or os.path.basename(path)
        if not document_id:
            document_id = f"doc-{int(time.time() * 1000)}"
        file_size_mb = f"{(os.path.getsize(path) / (1024 * 1024)):.2f} MB"
        file_ext = os.path.splitext(filename)[1].lower().replace(".", "")

        # 1. Page-by-page extraction
        pages = self.processor.process_file(path)
        total_pages = max(len(pages), 1)

        doc = CaseDocument(
            id=document_id,
            case_id=case_id,
            filename=filename,
            category=category,
            file_type=file_ext,
            file_size=file_size_mb,
            uploaded_date=time.strftime("%Y-%m-%d"),
            status="indexing",
            pages=total_pages,
            storage_path=path
        )
        self.index.register_document(doc)

        # 2. Chunking with page provenance
        chunks = self.chunker.chunk_document(
            pages=pages,
            case_id=case_id,
            document_id=document_id,
            document_name=filename,
            document_type=category
        )

        if chunks:
            # 3. Embedding generation
            texts = [c.text for c in chunks]
            embeddings = self.embedder.encode_passages(texts)

            # 4. Atomic indexing
            self.index.add_chunks(chunks, embeddings)
            self.index.update_document_status(document_id, "indexed")
            doc.status = "indexed"
        else:
            self.index.update_document_status(document_id, "indexed_empty")
            doc.status = "indexed_empty"

        return doc

    def answer_case_question(
        self,
        question: str,
        case_id: str,
        top_k: int = 6,
        max_new_tokens: int = 768,
        output_plan: Optional[str] = None,
        sub_intent: Optional[str] = None,
        user_goal: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> CaseAnalysisResult:
        """Executes query-conditioned case retrieval, grounds prompt with page citations, and runs Case Analysis V1."""
        t0 = time.time()

        # Step 1: Verify case records & documents
        meta = self._get_case_metadata(case_id)
        case_id_clean = meta["case_id"] if meta else case_id
        case_num_clean = meta["case_number"] if meta else case_id
        case_title_clean = meta["case_title"] if meta else f"Case {case_id}"

        # Resolve case_id variants (e.g. CASE-2024-CV-1187 vs 2024-CV-1187 or case-01)
        chunk_count = self.index.count_chunks_for_case(case_id)
        if chunk_count == 0:
            candidates = []
            if case_id.upper().startswith("CASE-"):
                candidates.append(case_id[5:])
            if meta:
                candidates.extend([meta.get("case_number"), meta.get("case_id")])
            for cand in candidates:
                if cand and cand != case_id and self.index.count_chunks_for_case(cand) > 0:
                    case_id = cand
                    chunk_count = self.index.count_chunks_for_case(case_id)
                    break

        is_summary_request = (sub_intent == "CASE_SUMMARY" or output_plan == "CASE_SUMMARY" or any(kw in question.lower() for kw in ["what is the matter", "summary", "about this matter", "overview"]))
        is_context_dialogue_query = bool(
            conversation_history and any(turn.get("role") == "assistant" for turn in conversation_history) and
            any(kw in question.lower() for kw in [
                "previous", "earlier", "first", "start", "above", "last", "what did i ask",
                "what did we discuss", "recall", "format", "reformat", "table", "bullet",
                "clearly", "simplify", "simple terms", "break it down", "what about that"
            ])
        )

        if chunk_count == 0 and not is_context_dialogue_query:
            if meta and is_summary_request:
                matter_summary = meta.get("matter_summary") or meta.get("description") or "Registered matter."
                court = meta.get("court") or "Hon'ble Court"
                status = meta.get("status") or "Active"
                next_h = meta.get("next_hearing_date") or meta.get("next_hearing") or "Not scheduled"

                answer_text = (
                    f"### CASE SUMMARY\n\n"
                    f"**Matter**: {case_title_clean} ({case_num_clean})\n"
                    f"**Court**: {court}\n"
                    f"**Status**: {status}\n"
                    f"**Next Hearing**: {next_h}\n\n"
                    f"**What the case is about**:\n"
                    f"{matter_summary}\n\n"
                    f"**Current procedural position**:\n"
                    f"Case record registered. Specific evidentiary documents have not yet been uploaded to this matter's document repository."
                )
                source_rec = {
                    "id": f"record-{case_id_clean}",
                    "type": "document",
                    "title": f"Matter Record ({case_num_clean})",
                    "reference": f"Case File ({case_num_clean})",
                    "excerpt": (matter_summary[:180] + ("..." if len(matter_summary) > 180 else "")),
                    "case_id": case_id_clean,
                    "case_title": case_title_clean,
                    "case_number": case_num_clean,
                    "document_id": f"matter-record-{case_id_clean}",
                    "document_name": "Case Matter Record",
                    "chunk_id": f"summary-{case_id_clean}",
                    "source_type": "matter_record",
                    "source_scope": "CURRENT_MATTER"
                }
                return CaseAnalysisResult(
                    answer=answer_text,
                    case_sources=[source_rec],
                    legal_sources=[],
                    findings={},
                    reliability="supported",
                    reliability_label="Supported by registered case file",
                    confidence_status="CASE_RECORD_GROUNDED",
                    generation_time_sec=round(time.time() - t0, 3)
                )

            # Evidentiary / document-specific inquiry with no uploaded documents
            return CaseAnalysisResult(
                answer="No relevant case documents are currently available for this question.\n\nPlease upload relevant case documents to enable evidentiary analysis.",
                case_sources=[],
                legal_sources=[],
                findings={},
                reliability="limited",
                reliability_label="No case documents found",
                confidence_status="INSUFFICIENT_CASE_MATERIAL",
                generation_time_sec=round(time.time() - t0, 3)
            )

        # Step 2: Retrieve case-specific chunks (Strict isolation by case_id)
        search_query = question
        if conversation_history:
            is_referential = bool(re.search(
                r'\b(?:this|that|it|previous|earlier|first|above|last|explain|clearly|simple|reformat|table|summarize)\b',
                question, re.IGNORECASE
            ))
            if is_referential or len(question.strip().split()) <= 4:
                for turn in reversed(conversation_history):
                    if turn.get("role") == "user" and turn.get("content"):
                        search_query = f"{question} {turn['content']}"
                        break

        retrieved_chunks = self.retriever.retrieve(
            query=search_query,
            case_id=case_id,
            top_k=top_k,
            sub_intent=sub_intent,
            user_goal=user_goal,
            output_plan=output_plan
        )

        if not retrieved_chunks:
            has_history_dialogue = bool(conversation_history and any(turn.get("role") == "assistant" for turn in conversation_history))
            if has_history_dialogue:
                # Prior conversation turns exist; proceed to generation using dialogue context
                pass
            elif meta and is_summary_request:
                matter_summary = meta.get("matter_summary") or meta.get("description") or "Registered matter."
                court = meta.get("court") or "Hon'ble Court"
                status = meta.get("status") or "Active"
                next_h = meta.get("next_hearing_date") or meta.get("next_hearing") or "Not scheduled"
                answer_text = (
                    f"### CASE SUMMARY\n\n"
                    f"**Matter**: {case_title_clean} ({case_num_clean})\n"
                    f"**Court**: {court}\n"
                    f"**Status**: {status}\n"
                    f"**Next Hearing**: {next_h}\n\n"
                    f"**What the case is about**:\n"
                    f"{matter_summary}\n\n"
                    f"**Current procedural position**:\n"
                    f"Status: {status}. No specific document excerpts matched the query."
                )
                return CaseAnalysisResult(
                    answer=answer_text,
                    case_sources=[],
                    legal_sources=[],
                    findings={},
                    reliability="supported",
                    reliability_label="Case metadata record",
                    confidence_status="CASE_RECORD_GROUNDED",
                    generation_time_sec=round(time.time() - t0, 3)
                )
            else:
                return CaseAnalysisResult(
                    answer="No relevant case documents are currently available for this question.\n\nPlease upload relevant case documents to enable evidentiary analysis.",
                    case_sources=[],
                    legal_sources=[],
                    findings={},
                    reliability="limited",
                    reliability_label="No relevant document match",
                    confidence_status="ZERO_RETRIEVAL",
                    generation_time_sec=round(time.time() - t0, 3)
                )

        # Step 3: Format case context with explicit document and page demarcations
        case_context_blocks = []
        case_sources = []
        seen_sources = set()

        if meta:
            meta_header = (
                f"=== CURRENT MATTER AUTHORITATIVE RECORD ===\n"
                f"Case Title: {case_title_clean}\n"
                f"Case Number: {case_num_clean}\n"
                f"Court: {meta.get('court')}\n"
                f"Parties: {meta.get('client')} v. {meta.get('opposing_party')}\n"
                f"Matter Summary: {meta.get('matter_summary')}\n"
                f"===========================================\n"
            )
            case_context_blocks.append(meta_header)

        for idx, chunk in enumerate(retrieved_chunks):
            src_key = (chunk.document_name, chunk.page_number)
            if src_key not in seen_sources:
                seen_sources.add(src_key)
                case_sources.append({
                    "id": chunk.chunk_id,
                    "type": "document",
                    "title": chunk.document_name,
                    "reference": f"Page {chunk.page_number}",
                    "excerpt": chunk.text[:180] + ("..." if len(chunk.text) > 180 else ""),
                    "case_id": case_id_clean,
                    "case_title": case_title_clean,
                    "case_number": case_num_clean,
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    "chunk_id": chunk.chunk_id,
                    "source_type": "document",
                    "source_scope": "CURRENT_MATTER"
                })

            block = (
                f"--- DOCUMENT: {chunk.document_name} | PAGE: {chunk.page_number} | "
                f"CHUNK ID: {chunk.chunk_id} ---\n"
                f"{chunk.text}\n"
            )
            case_context_blocks.append(block)

        case_context_str = "\n".join(case_context_blocks)

        # Step 4: Check if statutory authority is also relevant (e.g. BSA electronic evidence, bail, etc.)
        legal_sources = []
        legal_authority_str = ""
        if self.base_pipeline and any(term in question.lower() for term in [
            "electronic evidence", "63", "65b", "bail", "167", "482", "recovery", "27", "trademark", "limitation"
        ]):
            try:
                # Query statutory Legal RAG
                stat_result = self.base_pipeline.retriever.retrieve(question, top_k=2)
                if stat_result:
                    stat_blocks = []
                    for s in stat_result:
                        act_lbl = getattr(s, "act", getattr(s, "act_name", "Statute"))
                        sec_lbl = getattr(s, "section", getattr(s, "section_number", ""))
                        stat_blocks.append(f"[{act_lbl} Section {sec_lbl}: {s.section_title}]\n{s.text[:400]}")
                        legal_sources.append({
                            "id": s.chunk_id,
                            "type": "statute",
                            "title": act_lbl,
                            "reference": f"Section {sec_lbl}",
                            "excerpt": s.section_title
                        })
                    legal_authority_str = (
                        "\n### APPLICABLE STATUTORY AUTHORITY (LEGAL RAG):\n" +
                        "\n\n".join(stat_blocks) + "\n"
                    )
            except Exception as e:
                print(f"[CaseRAGPipeline] Statutory authority enrichment skipped: {e}")

        # Step 5: Assemble Grounded Case Analysis Prompt
        instruction_text = ""
        if output_plan:
            try:
                from src.api.query_understanding.planner import ResponsePlanner
                guidance = ResponsePlanner.get_structure_guidance(output_plan)
                if guidance:
                    instruction_text = guidance.get("instruction") or guidance.get("system_instruction") or ""
                    if guidance.get("max_tokens"):
                        max_new_tokens = min(max_new_tokens, guidance["max_tokens"])
            except Exception as e:
                pass

        user_prompt = (
            f"CASE SCOPE: Current Matter ({case_title_clean}, {case_num_clean})\n"
            f"USER QUERY: {question}\n"
            f"SUB-INTENT: {sub_intent or 'CASE_QUERY'}\n"
            f"USER GOAL: {user_goal or 'UNDERSTAND_CASE'}\n"
            f"OUTPUT PLAN: {output_plan or 'CASE_SUMMARY'}\n\n"
            f"RETRIEVED CASE EVIDENCE:\n{case_context_str}\n"
        )
        if legal_authority_str:
            user_prompt += f"\nAPPLICABLE STATUTORY AUTHORITY:\n{legal_authority_str}\n"

        directive = (
            f"\nREQUIRED OUTPUT STRUCTURE & INSTRUCTIONS:\n"
            f"{instruction_text}\n\n"
            f"- Answer ONLY the specific query. Format the response according to the user's specific request (e.g. comparative table, bullet points, concise summary, or drafted clause).\n"
            f"- Base your analysis strictly on the retrieved case evidence and verified facts.\n"
            f"- If the available case documents do not establish a point, state clearly: 'The currently available case documents do not establish this.'\n"
            f"- If asked to reformat, simplify, or clarify the previous response, reference the previous response in context and present the clearer format.\n"
            f"- If asked about earlier messages or issues mentioned at the start of the chat, review the conversation history and report them accurately.\n\n"
            f"LAWYER QUERY:\n{question}"
        )
        user_prompt += directive

        messages = [{"role": "system", "content": CASE_ANALYSIS_SYSTEM_PROMPT}]
        if conversation_history:
            for turn in conversation_history[-8:]:
                r = turn.get("role")
                c = turn.get("content")
                if r in ("user", "assistant") and c:
                    messages.append({"role": r, "content": c})
        messages.append({"role": "user", "content": user_prompt})

        # Step 6: Generate via Case Analysis V1 LoRA adapter (or Base Qwen if clarifying/reformatting)
        is_reformat_or_simplify = any(kw in question.lower() for kw in [
            "simple terms", "simpler terms", "clearly", "reformat", "as a table",
            "in a table", "bullet points", "line by line", "from the first", "at the start"
        ])
        use_adapter = not is_reformat_or_simplify

        answer_text = self._generate_with_case_analysis_v1(messages, max_new_tokens=max_new_tokens, use_adapter=use_adapter)

        # Post-processing: clean self-continuation or hallucinated queries
        if "LAWYER QUERY" in answer_text:
            answer_text = answer_text.split("LAWYER QUERY")[0].strip()

        # Clean hallucinated generic boilerplate if not in chunks
        all_chunk_text = " ".join([c.text for c in retrieved_chunks])
        hallucinated_patterns = [
            r"^.*(?:Primary documents and affidavits|primary documents and affidavits).*$",
            r"^.*(?:Primary contracts, contemporaneous communications|primary contracts, contemporaneous).*$"
        ]
        for pat in hallucinated_patterns:
            if re.search(pat, answer_text, re.IGNORECASE | re.MULTILINE) and not re.search(pat, all_chunk_text, re.IGNORECASE):
                answer_text = re.sub(pat, "- The currently available case documents do not establish this.", answer_text, flags=re.IGNORECASE | re.MULTILINE)

        # Dynamic query-driven section pruning
        answer_text = self._prune_unrequested_sections(answer_text, output_plan)

        # Step 7: Reliability categorization
        has_verification = "requires verification" in answer_text.lower() or "not found" in answer_text.lower()
        reliability = "verify" if has_verification else "supported"
        reliability_label = "Requires verification" if has_verification else "Supported by case documents"

        return CaseAnalysisResult(
            answer=answer_text,
            case_sources=case_sources,
            legal_sources=legal_sources,
            findings={},
            reliability=reliability,
            reliability_label=reliability_label,
            confidence_status="CASE_DOCUMENT_GROUNDED",
            generation_time_sec=round(time.time() - t0, 3)
        )

    def _prune_unrequested_sections(self, answer_text: str, output_plan: Optional[str]) -> str:
        """Prunes unrequested boilerplate sections to guarantee question-driven generation."""
        if not output_plan or not answer_text:
            return answer_text

        plan = output_plan.upper()
        disallowed_headers = []
        if plan == "CASE_SUMMARY":
            disallowed_headers = ["EVIDENCE GAPS", "NEXT STEPS", "EVIDENCE"]
        elif plan == "AVAILABLE_EVIDENCE":
            disallowed_headers = ["EVIDENCE GAPS", "NEXT STEPS"]
        elif plan == "EVIDENCE_GAPS":
            disallowed_headers = ["AVAILABLE EVIDENCE", "NEXT STEPS"]
        elif plan == "KEY_POINTS":
            disallowed_headers = ["EVIDENCE GAPS", "NEXT STEPS"]
        elif plan in ("HEARING_BRIEF", "ACTIONABLE_NEXT_STEPS"):
            disallowed_headers = ["EVIDENCE GAPS"]

        if not disallowed_headers:
            return answer_text

        lines = answer_text.splitlines()
        filtered_lines = []
        current_section_is_disallowed = False

        known_headers = [
            "ANALYSIS", "FACTS", "EVIDENCE", "EVIDENCE ON RECORD", "AVAILABLE EVIDENCE",
            "EVIDENCE GAPS", "NEXT STEPS", "ACTIONABLE NEXT STEPS", "LEGAL AUTHORITY",
            "LEGAL ISSUES", "UNCERTAINTY", "KEY POINTS", "SUMMARY", "CASE SUMMARY",
            "POTENTIAL RISKS", "CASE RISKS", "ARGUMENTS", "COUNTERARGUMENTS"
        ]

        for line in lines:
            stripped = line.strip().strip("#").strip(":").strip()
            stripped_upper = stripped.upper()

            is_known_header = any(stripped_upper == h or stripped_upper.startswith(h + " ") or stripped_upper.startswith(h + ":") for h in known_headers)
            if is_known_header:
                if any(stripped_upper == dh or stripped_upper.startswith(dh) for dh in disallowed_headers):
                    current_section_is_disallowed = True
                else:
                    current_section_is_disallowed = False

            if not current_section_is_disallowed:
                filtered_lines.append(line)

        result = "\n".join(filtered_lines).strip()
        return result if result else answer_text

    def answer_cross_matter_question(
        self,
        question: str,
        current_case_id: str,
        top_k: int = 4,
        max_new_tokens: int = 768
    ) -> CaseAnalysisResult:
        """
        Executes query-dependent cross-matter retrieval and synthesis with structural provenance boundaries.
        Enforces Safeguard 1:
        - Structured provenance (case_id, case_title, case_number, document_id, document_name, chunk_id, source_scope='OTHER_MATTER')
        - Clear separation between CURRENT MATTER and OTHER MATTER / COMPARATIVE REFERENCE.
        - Fails safely if provenance cannot be validated.
        """
        t0 = time.time()
        current_meta = self._get_case_metadata(current_case_id)
        cur_id = current_meta["case_id"] if current_meta else current_case_id
        cur_num = current_meta["case_number"] if current_meta else current_case_id
        cur_title = current_meta["case_title"] if current_meta else f"Case {current_case_id}"

        # 1. Retrieve current matter context (chunks + metadata)
        current_chunks = self.retriever.retrieve(query=question, case_id=current_case_id, top_k=2) if self.index.count_chunks_for_case(current_case_id) > 0 else []
        current_context_blocks = []
        case_sources = []

        if current_meta:
            current_context_blocks.append(
                f"Title: {cur_title}\nCase Number: {cur_num}\nSummary: {current_meta.get('matter_summary')}"
            )
            case_sources.append({
                "id": f"record-{cur_id}",
                "type": "document",
                "title": f"Matter Record ({cur_num})",
                "reference": f"Case File ({cur_num})",
                "excerpt": (current_meta.get('matter_summary') or cur_title)[:180],
                "case_id": cur_id,
                "case_title": cur_title,
                "case_number": cur_num,
                "document_id": f"matter-record-{cur_id}",
                "document_name": "Current Matter Record",
                "chunk_id": f"rec-{cur_id}",
                "source_type": "matter_record",
                "source_scope": "CURRENT_MATTER"
            })

        for chunk in current_chunks:
            current_context_blocks.append(f"[{chunk.document_name} p.{chunk.page_number}]: {chunk.text}")
            case_sources.append({
                "id": chunk.chunk_id,
                "type": "document",
                "title": chunk.document_name,
                "reference": f"Page {chunk.page_number}",
                "excerpt": chunk.text[:180] + ("..." if len(chunk.text) > 180 else ""),
                "case_id": cur_id,
                "case_title": cur_title,
                "case_number": cur_num,
                "document_id": chunk.document_id,
                "document_name": chunk.document_name,
                "chunk_id": chunk.chunk_id,
                "source_type": "document",
                "source_scope": "CURRENT_MATTER"
            })

        # 2. Retrieve other cases for cross-matter comparison
        other_matters = []
        try:
            conn_app = sqlite3.connect("data/legalai_app.db")
            cur_app = conn_app.cursor()
            app_rows = cur_app.execute(
                "SELECT id, caseNumber, title, client, court, caseType, description, matterSummary FROM cases WHERE id != ? AND caseNumber != ?",
                (cur_id, cur_num)
            ).fetchall()
            conn_app.close()
            for r in app_rows:
                other_matters.append({
                    "case_id": r[0],
                    "case_number": r[1],
                    "case_title": r[2],
                    "client": r[3],
                    "court": r[4],
                    "case_type": r[5],
                    "description": r[6] or "",
                    "matter_summary": r[7] or r[6] or ""
                })
        except Exception as e:
            logger.warning(f"Error querying other cases: {e}")

        matched_other_records = []
        q_lower = question.lower()
        for om in other_matters:
            summary = (om["description"] + " " + om["matter_summary"] + " " + om["case_type"] + " " + om["case_title"]).lower()
            is_relevant = False
            if any(term in summary for term in ["freight", "logistics", "charterparty", "cargo", "commercial", "arbitration", "contract"]):
                if any(term in q_lower or term in (cur_title + " " + current_meta.get("matter_summary", "")).lower() for term in ["freight", "charterparty", "maritime", "cargo", "similar", "another"]):
                    is_relevant = True
            elif any(term in summary for term in ["bail", "criminal", "chargesheet"]):
                if any(term in q_lower for term in ["bail", "criminal", "whitfield", "chargesheet"]):
                    is_relevant = True
            elif any(term in q_lower for term in [om["case_id"].lower(), om["case_number"].lower(), om["case_title"].lower()]):
                is_relevant = True

            if is_relevant:
                # Structural provenance validation per Safeguard 1
                if not (om['case_id'] and om['case_title'] and om['case_number']):
                    continue

                matched_other_records.append({
                    "case_id": om["case_id"],
                    "case_title": om["case_title"],
                    "case_number": om["case_number"],
                    "court": om["court"],
                    "document_id": f"doc-record-{om['case_id']}",
                    "document_name": f"Matter Record ({om['case_number']})",
                    "chunk_id": f"meta-{om['case_id']}",
                    "source_type": "matter_record",
                    "source_scope": "OTHER_MATTER",
                    "text": f"Title: {om['case_title']} ({om['case_number']})\nCourt: {om['court']}\nType: {om['case_type']}\nSummary: {om['matter_summary']}"
                })

        if not matched_other_records and other_matters:
            # Default to first legitimate other matter
            om = other_matters[0] if other_matters[0]["case_id"] != "case-01" else other_matters[1]
            matched_other_records.append({
                "case_id": om["case_id"],
                "case_title": om["case_title"],
                "case_number": om["case_number"],
                "court": om["court"],
                "document_id": f"doc-record-{om['case_id']}",
                "document_name": f"Matter Record ({om['case_number']})",
                "chunk_id": f"meta-{om['case_id']}",
                "source_type": "matter_record",
                "source_scope": "OTHER_MATTER",
                "text": f"Title: {om['case_title']} ({om['case_number']})\nCourt: {om['court']}\nType: {om['case_type']}\nSummary: {om['matter_summary']}"
            })

        for rec in matched_other_records:
            case_sources.append({
                "id": rec["chunk_id"],
                "type": "document",
                "title": f"{rec['case_title']} ({rec['case_number']})",
                "reference": f"Comparative Case {rec['case_number']}",
                "excerpt": rec["text"][:180] + ("..." if len(rec["text"]) > 180 else ""),
                "case_id": rec["case_id"],
                "case_title": rec["case_title"],
                "case_number": rec["case_number"],
                "document_id": rec["document_id"],
                "document_name": rec["document_name"],
                "chunk_id": rec["chunk_id"],
                "source_type": rec["source_type"],
                "source_scope": "OTHER_MATTER"
            })

        current_section = "\n".join(current_context_blocks)
        other_section = "\n\n".join([f"=== OTHER MATTER: {r['case_title']} ({r['case_number']}) ===\n{r['text']}" for r in matched_other_records])

        user_prompt = (
            f"PRIMARY CONTEXT — CURRENT MATTER ({cur_title}):\n"
            f"{current_section}\n\n"
            f"==================================================\n"
            f"COMPARATIVE REFERENCE — OTHER MATTER (STRICT SEPARATION):\n"
            f"{other_section}\n\n"
            f"CRITICAL BOUNDARY INSTRUCTION:\n"
            f"1. The facts, allegations, parties, contracts, and proceedings from OTHER MATTER belong strictly to that other case.\n"
            f"2. You must NEVER conflate or attribute OTHER MATTER facts to the CURRENT MATTER ({cur_title}).\n"
            f"3. Address the user's question by drawing a clear, structured comparative distinction between the matters.\n\n"
            f"LAWYER QUERY:\n{question}"
        )

        messages = [
            {"role": "system", "content": CASE_ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        answer_text = self._generate_with_case_analysis_v1(messages, max_new_tokens=max_new_tokens)

        if matched_other_records:
            first_other = matched_other_records[0]
            caution_banner = (
                f"> [!CAUTION]\n"
                f"> **Cross-Matter Isolation**: Information concerning **{first_other['case_title']} ({first_other['case_number']})** "
                f"is provided for comparative reference only and is strictly independent of current matter **{cur_title}**.\n\n"
            )
            if not answer_text.startswith("> [!CAUTION]"):
                answer_text = caution_banner + answer_text

        return CaseAnalysisResult(
            answer=answer_text,
            case_sources=case_sources,
            legal_sources=[],
            findings={},
            reliability="supported",
            reliability_label="Cross-matter comparative reference",
            confidence_status="CROSS_MATTER_ISOLATED",
            generation_time_sec=round(time.time() - t0, 3)
        )

    def answer_multi_case_question(
        self,
        question: str,
        selected_case_ids: List[str],
        top_k: int = 3,
        max_new_tokens: int = 768
    ) -> CaseAnalysisResult:
        """
        Synthesizes legal questions across multiple selected matters while maintaining
        strict per-case boundaries and structured provenance.
        """
        t0 = time.time()
        case_sources = []
        context_blocks = []

        for cid in selected_case_ids:
            meta = self._get_case_metadata(cid)
            c_title = meta["case_title"] if meta else f"Matter {cid}"
            c_num = meta["case_number"] if meta else cid
            c_id = meta["case_id"] if meta else cid

            matter_header = f"=== MATTER: {c_title} ({c_num}) ==="
            matter_lines = [matter_header]
            if meta:
                matter_lines.append(f"Court: {meta.get('court')} | Status: {meta.get('status')}")
                matter_lines.append(f"Summary: {meta.get('matter_summary')}")
                case_sources.append({
                    "id": f"record-{c_id}",
                    "type": "document",
                    "title": f"Matter Record ({c_num})",
                    "reference": f"Case File ({c_num})",
                    "excerpt": (meta.get('matter_summary') or c_title)[:180],
                    "case_id": c_id,
                    "case_title": c_title,
                    "case_number": c_num,
                    "document_id": f"matter-record-{c_id}",
                    "document_name": "Matter Record",
                    "chunk_id": f"rec-{c_id}",
                    "source_type": "matter_record",
                    "source_scope": "SELECTED_MATTER"
                })

            if self.index.count_chunks_for_case(cid) > 0:
                chunks = self.retriever.retrieve(query=question, case_id=cid, top_k=top_k)
                for chunk in chunks:
                    matter_lines.append(f"[{chunk.document_name} p.{chunk.page_number}]: {chunk.text}")
                    case_sources.append({
                        "id": chunk.chunk_id,
                        "type": "document",
                        "title": chunk.document_name,
                        "reference": f"{c_num} - Page {chunk.page_number}",
                        "excerpt": chunk.text[:180] + ("..." if len(chunk.text) > 180 else ""),
                        "case_id": c_id,
                        "case_title": c_title,
                        "case_number": c_num,
                        "document_id": chunk.document_id,
                        "document_name": chunk.document_name,
                        "chunk_id": chunk.chunk_id,
                        "source_type": "document",
                        "source_scope": "SELECTED_MATTER"
                    })

            context_blocks.append("\n".join(matter_lines))

        user_prompt = (
            f"SELECTED MATTERS MATERIAL:\n\n" +
            "\n\n--------------------------------------------------\n\n".join(context_blocks) +
            f"\n\nCRITICAL INSTRUCTION:\n"
            f"Analyze and synthesize across the selected matters while keeping facts, dates, and parties explicitly attributed to each respective matter.\n\n"
            f"LAWYER QUERY:\n{question}"
        )

        messages = [
            {"role": "system", "content": CASE_ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        answer_text = self._generate_with_case_analysis_v1(messages, max_new_tokens=max_new_tokens)

        return CaseAnalysisResult(
            answer=answer_text,
            case_sources=case_sources,
            legal_sources=[],
            findings={},
            reliability="supported",
            reliability_label="Multi-matter synthesis",
            confidence_status="MULTI_MATTER_SYNTHESIS",
            generation_time_sec=round(time.time() - t0, 3)
        )

    def _generate_with_case_analysis_v1(self, messages: List[Dict[str, str]], max_new_tokens: int = 768, use_adapter: bool = True) -> str:
        """Executes generation with Case Analysis V1 adapter active (or disabled for pure Base Qwen formatting/simplification)."""
        if not self.base_pipeline or not self.base_pipeline.model:
            # Fallback if running offline or model not loaded
            return "Case Analysis V1 model is currently initializing."

        tokenizer = self.base_pipeline.tokenizer
        model = self.base_pipeline.model
        device = self.base_pipeline.device

        # Fast path: vLLM inference (50-150 tokens/s)
        target_model = "Qwen/Qwen2.5-14B-Instruct" if not use_adapter else "case_analysis"
        try:
            req_data = json.dumps({
                "model": target_model,
                "messages": messages,
                "max_tokens": max_new_tokens,
                "temperature": 0.0
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8009/v1/chat/completions",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                vllm_data = json.loads(resp.read().decode("utf-8"))
                return vllm_data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        input_length = inputs["input_ids"].shape[1]

        has_disable = hasattr(model, "disable_adapter")
        if not use_adapter and has_disable:
            with model.disable_adapter():
                with torch.inference_mode():
                    output_ids = model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=False,
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                    )
                new_tokens = output_ids[0, input_length:]
                answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                return answer

        # Temporarily activate Case Analysis V1 adapter if multi-adapter is active
        prev_adapter = getattr(model, "active_adapter", "default")
        has_case_adapter = hasattr(model, "peft_config") and "case_analysis_v1" in model.peft_config

        if has_case_adapter and hasattr(model, "set_adapter"):
            model.set_adapter("case_analysis_v1")

        try:
            with torch.inference_mode():
                output_ids = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            new_tokens = output_ids[0, input_length:]
            answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            return answer
        finally:
            # Restore previous adapter (legalai_v2 / default)
            if has_case_adapter and hasattr(model, "set_adapter"):
                model.set_adapter("default" if "default" in model.peft_config else "legalai_v2")
