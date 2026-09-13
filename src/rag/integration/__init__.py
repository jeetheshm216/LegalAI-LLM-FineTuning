"""LegalAI RAG + LegalAI v2 Integration Layer."""

from .grounded_prompt import build_grounded_prompt, GroundedPromptContext
from .rag_legalai import LegalAIRAGPipeline, answer_legal_question

__all__ = [
    "build_grounded_prompt",
    "GroundedPromptContext",
    "LegalAIRAGPipeline",
    "answer_legal_question",
]
