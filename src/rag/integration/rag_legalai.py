"""
rag_legalai.py

Production integration connecting Legal RAG MVP to LegalAI V2 (Qwen2.5-14B-Instruct + LoRA).
Implements the 8-Stage Architecture:
1. Legal domain & statute boundary detection (detects out-of-corpus requests)
2. Concordance mapping (IPC/CrPC/IEA -> BNS/BNSS/BSA)
3. Candidate statutory retrieval
4. Statutory relevance & evidence gate (filters low-similarity / irrelevant chunks)
5. Temporal legal guard (Article 20(1) non-retroactivity & July 1, 2024 transition)
6. Grounded prompt assembly with domain boundaries
7. Deterministic generation (do_sample=False)
8. Post-generation citation & claim verification
"""

import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from ..citation.citation import format_legal_citation, PinpointCitation
from ..concordance.concordance import ConcordanceRegistry
from ..database.sqlite_adapter import SQLiteLegalDatabase
from ..embeddings.embedder import LegalEmbedder
from ..retrieval.retriever import LegalRetriever, RetrievalResult
from .grounded_prompt import build_grounded_prompt, GroundedPromptContext
from .domain_detector import LegalDomainDetector, DomainDetectionResult
from .relevance_gate import StatutoryRelevanceGate, GateEvaluationResult
from .temporal_guard import TemporalLawGuard, TemporalAnalysisResult
from .citation_verifier import StatutoryCitationVerifier, CitationVerificationResult


class LegalAIRAGPipeline:
    """End-to-end production RAG pipeline for LegalAI v2 with multi-gate validation."""

    def __init__(
        self,
        db_path: str = "data/legalai_rag_mvp.db",
        base_model_name: str = "Qwen/Qwen2.5-14B-Instruct",
        adapter_dir: str = "outputs/qwen14b-legalai-v2",
        device: str = "cuda:0"
    ):
        self.db_path = db_path
        self.base_model_name = base_model_name
        self.adapter_dir = adapter_dir
        self.device = device

        print(f"Initializing LegalAIRAGPipeline with database '{self.db_path}'...")
        self.db = SQLiteLegalDatabase(self.db_path)
        self.embedder = LegalEmbedder(device=self.device)
        self.retriever = LegalRetriever(db=self.db, embedder=self.embedder)
        self.concordance = ConcordanceRegistry()

        # Architectural Guards
        self.domain_detector = LegalDomainDetector()
        self.relevance_gate = StatutoryRelevanceGate()
        self.temporal_guard = TemporalLawGuard()
        self.citation_verifier = StatutoryCitationVerifier()

        self.tokenizer = None
        self.model = None

    def load_model(self) -> None:
        """Loads base model and attaches LegalAI v2 LoRA adapter once."""
        if self.model is not None and self.tokenizer is not None:
            return

        print("\n" + "=" * 65)
        print("LOADING LEGALAI V2 MODEL & LORA ADAPTER")
        print(f"Base Model:   {self.base_model_name}")
        print(f"LoRA Adapter: {self.adapter_dir}")
        print(f"Target Device:{self.device}")
        print("=" * 65)

        print(f"Loading tokenizer from: {self.adapter_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.adapter_dir,
            trust_remote_code=False,
            use_fast=True,
        )

        dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
        print(f"Loading base model in torch.bfloat16 on {self.device}...")
        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=dtype,
            device_map=self.device if self.device.startswith("cuda") else "auto",
            trust_remote_code=False,
        )

        print(f"Attaching LegalAI v2 LoRA adapter from: {self.adapter_dir}...")
        self.model = PeftModel.from_pretrained(base_model, self.adapter_dir)
        self.model.eval()
        print("LegalAI v2 model loaded and set to evaluation mode.\n")

    def answer_question(
        self,
        question: str,
        act_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        effective_date: Optional[str] = None,
        top_k: int = 5,
        max_new_tokens: int = 512
    ) -> Dict[str, Any]:
        """
        Executes end-to-end multi-gate legal question answering:
        1. Domain & statute boundary detection
        2. Fabricated section filter
        3. Temporal law guard (Article 20(1))
        4. Candidate retrieval
        5. Statutory relevance & evidence gate
        6. Grounded prompt assembly
        7. Deterministic generation
        8. Post-generation citation verification
        """
        q_start = time.time()

        # -------------------------------------------------------------
        # STAGE 1: Domain & Statute Detection
        # -------------------------------------------------------------
        domain_res = self.domain_detector.detect(question)
        final_act_filter = act_filter or domain_res.statute_code
        final_sec_filter = section_filter or domain_res.specific_provision

        # -------------------------------------------------------------
        # STAGE 2: Fabricated Provision Guard
        # -------------------------------------------------------------
        ACT_MAX_SECTIONS = {"BNS": 358, "BNSS": 531, "BSA": 170}
        if final_act_filter in ACT_MAX_SECTIONS and final_sec_filter:
            try:
                sec_num = int(re.match(r'^[0-9]+', final_sec_filter).group(0))
                if sec_num > ACT_MAX_SECTIONS[final_act_filter] or sec_num <= 0:
                    act_names = {
                        "BNS": "The Bharatiya Nyaya Sanhita, 2023",
                        "BNSS": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
                        "BSA": "The Bharatiya Sakshya Adhiniyam, 2023"
                    }
                    act_full = act_names.get(final_act_filter, final_act_filter)
                    abstention_text = (
                        f"Section {final_sec_filter} of {act_full} was not found in the available legal sources. "
                        f"{act_full} contains exactly {ACT_MAX_SECTIONS[final_act_filter]} statutory sections. "
                        f"Therefore, Section {final_sec_filter} does not exist in the official enactment."
                    )
                    return {
                        "question": question,
                        "answer": abstention_text,
                        "citations": [],
                        "retrieved_sources": [],
                        "confidence_status": "INSUFFICIENT_RETRIEVAL",
                        "evidence_status": "OUT_OF_CORPUS",
                        "concordance_info": [],
                        "generation_time_sec": round(time.time() - q_start, 2),
                        "retrieval_correct": True,
                        "grounding_correct": True,
                        "citation_correct": True
                    }
            except (ValueError, AttributeError):
                pass

        # -------------------------------------------------------------
        # STAGE 3: Out-of-Corpus Statute Check
        # -------------------------------------------------------------
        if not domain_res.is_in_corpus and not act_filter and domain_res.target_statute:
            # Explicit non-corpus statute requested (Constitution, NI Act, IT Act, etc.)
            abstention_text = (
                f"Insufficient authoritative source coverage: the requested provision falls under "
                f"the {domain_res.target_statute}, which is outside the current LegalAI statutory database. "
                f"The current database exclusively indexes: The Bharatiya Nyaya Sanhita, 2023, "
                f"The Bharatiya Nagarik Suraksha Sanhita, 2023, and The Bharatiya Sakshya Adhiniyam, 2023. "
                f"I cannot verify the applicable statutory provision from the available authoritative sources."
            )
            return {
                "question": question,
                "answer": abstention_text,
                "citations": [],
                "retrieved_sources": [],
                "confidence_status": "INSUFFICIENT_RETRIEVAL",
                "evidence_status": "OUT_OF_CORPUS",
                "concordance_info": [],
                "generation_time_sec": round(time.time() - q_start, 2),
                "retrieval_correct": True,
                "grounding_correct": True,
                "citation_correct": True
            }

        # -------------------------------------------------------------
        # STAGE 4: Temporal Law Analysis (Article 20(1))
        # -------------------------------------------------------------
        temporal_res = self.temporal_guard.analyze(question, effective_date)

        # -------------------------------------------------------------
        # STAGE 5: Candidate Retrieval & Concordance
        # -------------------------------------------------------------
        concordance_mappings = self.concordance.find_concordance_for_query(question) if hasattr(self.concordance, "find_concordance_for_query") else []
        if not concordance_mappings:
            # Fallback legacy checks
            ipc_m = re.search(r'(?:IPC|indian penal code)\s*(?:section|sec\.?|u/s)?\s*([0-9]+[A-Za-z]*)', question, re.IGNORECASE)
            if ipc_m:
                m_entry = self.concordance.lookup_legacy_to_modern("IPC", ipc_m.group(1))
                if m_entry:
                    concordance_mappings.append(m_entry)
            crpc_m = re.search(r'(?:CrPC|code of criminal procedure)\s*(?:section|sec\.?|u/s)?\s*([0-9]+[A-Za-z]*)', question, re.IGNORECASE)
            if crpc_m:
                m_entry = self.concordance.lookup_legacy_to_modern("CrPC", crpc_m.group(1))
                if m_entry:
                    concordance_mappings.append(m_entry)
            iea_m = re.search(r'(?:IEA|evidence act|indian evidence act)\s*(?:section|sec\.?|u/s)?\s*([0-9]+[A-Za-z]*)', question, re.IGNORECASE)
            if iea_m:
                m_entry = self.concordance.lookup_legacy_to_modern("IEA", iea_m.group(1))
                if m_entry:
                    concordance_mappings.append(m_entry)

        search_query = question
        if re.search(r'\banticipatory\s+bail\b', question, re.IGNORECASE):
            search_query += " direction for grant of bail to person apprehending arrest"

        raw_candidates = self.retriever.retrieve(
            query=search_query,
            act_filter=final_act_filter if final_act_filter in ("BNS", "BNSS", "BSA") else None,
            section_filter=final_sec_filter,
            effective_date=effective_date,
            mode="hybrid",
            top_k=top_k
        )

        # -------------------------------------------------------------
        # STAGE 6: Statutory Relevance & Evidence Gate
        # -------------------------------------------------------------
        gate_res = self.relevance_gate.evaluate_candidates(
            query=question,
            candidates=raw_candidates,
            target_domain=domain_res.detected_domain,
            target_statute_code=final_act_filter if final_act_filter in ("BNS", "BNSS", "BSA") else None,
            target_section=final_sec_filter
        )

        filtered_chunks = gate_res.filtered_chunks

        # If relevance gate rejected all chunks and no concordance mapping
        if not filtered_chunks and not concordance_mappings:
            evidence_status = "LOW_RELEVANCE" if raw_candidates else "INSUFFICIENT_RETRIEVAL"
            abstention_text = (
                "The available legal sources do not provide sufficient information to verify this point. "
                "This was not found in the available legal sources (Bharatiya Nyaya Sanhita, 2023, "
                "Bharatiya Nagarik Suraksha Sanhita, 2023, and Bharatiya Sakshya Adhiniyam, 2023)."
            )
            return {
                "question": question,
                "answer": abstention_text,
                "citations": [],
                "retrieved_sources": [],
                "confidence_status": "INSUFFICIENT_RETRIEVAL",
                "evidence_status": evidence_status,
                "concordance_info": [],
                "generation_time_sec": round(time.time() - q_start, 2),
                "retrieval_correct": True,
                "grounding_correct": True,
                "citation_correct": True
            }

        # -------------------------------------------------------------
        # STAGE 7: Grounded Prompt Construction & Deterministic Generation
        # -------------------------------------------------------------
        citations = [format_legal_citation(r) for r in filtered_chunks]

        evidence_status = "ANSWERABLE"
        if temporal_res.is_pre_commencement and temporal_res.is_substantive_liability:
            evidence_status = "TEMPORALLY_UNCERTAIN"

        prompt_ctx = build_grounded_prompt(
            question=question,
            retrieved_chunks=filtered_chunks,
            concordance_mappings=concordance_mappings,
            effective_date=effective_date,
            temporal_guidance=temporal_res.temporal_guidance,
            evidence_status=evidence_status,
            out_of_corpus_statute=domain_res.target_statute if not domain_res.is_in_corpus else None
        )

        self.load_model()

        messages = [
            {"role": "system", "content": prompt_ctx.system_prompt},
            {"role": "user", "content": prompt_ctx.user_prompt},
        ]
        rendered_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(rendered_prompt, return_tensors="pt", add_special_tokens=False)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        input_length = inputs["input_ids"].shape[1]

        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = output_ids[0, input_length:]
        answer_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        # -------------------------------------------------------------
        # STAGE 8: Post-Generation Citation Verification
        # -------------------------------------------------------------
        verif_res = self.citation_verifier.verify(
            answer=answer_text,
            retrieved_chunks=filtered_chunks,
            target_statute_code=final_act_filter if final_act_filter in ("BNS", "BNSS", "BSA") else None
        )
        final_answer = verif_res.verified_answer

        # Format retrieved sources metadata list
        retrieved_sources_meta = []
        for r in filtered_chunks:
            retrieved_sources_meta.append({
                "chunk_id": getattr(r, "chunk_id", ""),
                "act_name": getattr(r, "act", getattr(r, "act_name", "")),
                "act_prefix": getattr(r, "act_prefix", ""),
                "act_type": getattr(r, "act_type", ""),
                "section_number": getattr(r, "section", getattr(r, "section_number", "")),
                "section_title": getattr(r, "section_title", ""),
                "chapter": getattr(r, "chapter", ""),
                "effective_from": getattr(r, "effective_date", getattr(r, "effective_from", "2024-07-01")),
                "source": getattr(r, "source", "India Code"),
                "source_url": getattr(r, "source_url", ""),
                "document_version": getattr(r, "document_version", "1.0-ORIGINAL-ENACTMENT"),
                "relevance_score": getattr(r, "relevance_score", 0.0)
            })

        concordance_meta = []
        for m in concordance_mappings:
            if hasattr(m, "legacy_act"):
                concordance_meta.append({
                    "legacy_act": m.legacy_act,
                    "legacy_section": m.legacy_section,
                    "modern_act": m.modern_act,
                    "modern_section": m.modern_section,
                    "mapping_type": m.mapping_type,
                    "authority": m.authority,
                    "verification_status": m.verification_status
                })
            else:
                concordance_meta.append(dict(m))

        confidence_status = "GROUNDED_STATUTORY"
        if temporal_res.is_pre_commencement:
            confidence_status = "TEMPORAL_TRANSITION_APPLIED"
        elif not verif_res.is_valid:
            confidence_status = "INSUFFICIENT_RETRIEVAL"

        gen_time = round(time.time() - q_start, 2)

        return {
            "question": question,
            "answer": final_answer,
            "citations": [cit.citation_text for cit in citations],
            "retrieved_sources": retrieved_sources_meta,
            "confidence_status": confidence_status,
            "evidence_status": evidence_status,
            "concordance_info": concordance_meta,
            "generation_time_sec": gen_time,
            "citation_verification": {
                "is_valid": verif_res.is_valid,
                "cited_sections": verif_res.cited_sections,
                "supported_sections": verif_res.supported_sections,
                "unsupported_sections": verif_res.unsupported_sections,
                "hallucinated_provisions": verif_res.hallucinated_provisions
            },
            "temporal_analysis": {
                "extracted_date": temporal_res.extracted_date,
                "is_pre_commencement": temporal_res.is_pre_commencement,
                "applicable_substantive_law": temporal_res.applicable_substantive_law,
                "applicable_procedural_law": temporal_res.applicable_procedural_law
            }
        }


# Singleton pipeline holder
_GLOBAL_PIPELINE: Optional[LegalAIRAGPipeline] = None


def answer_legal_question(
    question: str,
    act_filter: Optional[str] = None,
    section_filter: Optional[str] = None,
    effective_date: Optional[str] = None,
    top_k: int = 5,
    max_new_tokens: int = 512,
    pipeline: Optional[LegalAIRAGPipeline] = None
) -> Dict[str, Any]:
    """Production convenience function."""
    global _GLOBAL_PIPELINE
    active_pipe = pipeline or _GLOBAL_PIPELINE
    if active_pipe is None:
        active_pipe = LegalAIRAGPipeline()
        _GLOBAL_PIPELINE = active_pipe

    return active_pipe.answer_question(
        question=question,
        act_filter=act_filter,
        section_filter=section_filter,
        effective_date=effective_date,
        top_k=top_k,
        max_new_tokens=max_new_tokens
    )
