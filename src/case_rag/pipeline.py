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
from typing import Dict, Any, List, Optional, Tuple

import torch
from .models import CaseDocument, DocumentChunk, CaseRetrievalResult, CaseAnalysisResult
from .document_processor import DocumentProcessor
from .chunker import CaseDocumentChunker
from .embeddings import CaseEmbedder
from .index import CaseRAGIndex
from .retriever import CaseRetriever


CASE_ANALYSIS_SYSTEM_PROMPT = """You are LegalAI Case Analyst, an advanced legal intelligence engine specialized in Indian litigation, evidence analysis, and case preparation.

You are evaluating actual case documents uploaded by an advocate for a specific legal matter.

STRICT OPERATIONAL PRINCIPLES:
1. FACTUAL FIDELITY & NO FABRICATION:
   - Base all factual statements strictly on the provided CASE DOCUMENTS.
   - Do NOT invent facts, documents, dates, times, witnesses, statements, or forensic findings.
   - Do NOT assume an unprovided document exists simply because another document mentions it.

2. ABSENCE VS NON-EXISTENCE:
   - If a document, fact, or evidence item is not in the provided materials, explicitly state:
     "Not found in the supplied case material."
   - Do NOT state: "This evidence does not exist" or "The party has no evidence."
   - Always distinguish between what is documented vs what is missing from the supplied material.

3. ADMISSIBILITY & JUDICIAL DECISION BOUNDARY:
   - Do NOT make definitive judicial determinations such as "This evidence is admissible" or "The court will reject this evidence."
   - Instead, provide legal analysis: "Requires verification", "The supplied documents do not establish compliance with...", or "Potential issue under Section X".
   - Guide the advocate on what needs to be verified before submitting evidence.

4. STRUCTURED FINDINGS:
   Structure your analysis clearly where applicable:
   - **Documented Facts**: Specific facts directly established by the documents (with document and page citations).
   - **Evidence Gaps / Missing Materials**: Referenced documents or critical elements not found in supplied materials.
   - **Potential Contradictions**: Inconsistencies between documents, dates, times, or witness statements.
   - **Items Requiring Verification**: Authentication, chain of custody, certification requirements (e.g. BSA electronic evidence certificates).
   - **Strategic Recommendations / Hearing Preparation**: Practical next steps for the advocate.

5. CITATIONS:
   - Cite every factual observation with its Document Name and Page Number (e.g., [FIR.pdf — Page 3]).
   - If statutory provisions are referenced, distinguish Case Sources from Statutory Legal Authorities."""


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
        max_new_tokens: int = 768
    ) -> CaseAnalysisResult:
        """Executes case retrieval, grounds prompt with page citations, and runs Case Analysis V1."""
        t0 = time.time()

        # Step 1: Verify case has documents
        chunk_count = self.index.count_chunks_for_case(case_id)
        if chunk_count == 0:
            return CaseAnalysisResult(
                answer=EMPTY_CASE_RESPONSE,
                case_sources=[],
                legal_sources=[],
                findings={},
                reliability="limited",
                reliability_label="No case documents found",
                confidence_status="INSUFFICIENT_CASE_MATERIAL",
                generation_time_sec=round(time.time() - t0, 3)
            )

        # Step 2: Retrieve case-specific chunks (Strict isolation by case_id)
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            case_id=case_id,
            top_k=top_k
        )

        if not retrieved_chunks:
            return CaseAnalysisResult(
                answer=f"No relevant excerpts found in the supplied documents for case '{case_id}' matching: \"{question}\".",
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

        for idx, chunk in enumerate(retrieved_chunks):
            src_key = (chunk.document_name, chunk.page_number)
            if src_key not in seen_sources:
                seen_sources.add(src_key)
                case_sources.append({
                    "id": chunk.chunk_id,
                    "type": "document",
                    "title": chunk.document_name,
                    "reference": f"Page {chunk.page_number}",
                    "excerpt": chunk.text[:180] + ("..." if len(chunk.text) > 180 else "")
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
        user_prompt = f"CASE MATERIAL:\n{case_context_str}\n"
        if legal_authority_str:
            user_prompt += f"\nLEGAL AUTHORITY:\n{legal_authority_str}\n"
        user_prompt += f"\nLAWYER QUERY:\n{question}"

        messages = [
            {"role": "system", "content": CASE_ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # Step 6: Generate via Case Analysis V1 LoRA adapter
        answer_text = self._generate_with_case_analysis_v1(messages, max_new_tokens=max_new_tokens)

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

    def _generate_with_case_analysis_v1(self, messages: List[Dict[str, str]], max_new_tokens: int = 768) -> str:
        """Executes generation with Case Analysis V1 adapter active."""
        if not self.base_pipeline or not self.base_pipeline.model:
            # Fallback if running offline or model not loaded
            return "Case Analysis V1 model is currently initializing."

        tokenizer = self.base_pipeline.tokenizer
        model = self.base_pipeline.model
        device = self.base_pipeline.device

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        input_length = inputs["input_ids"].shape[1]

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
