"""Abstract Base Class for LegalAI Database Adapters."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np


class BaseLegalDatabase(ABC):
    """Abstract interface for legal database implementations."""

    @abstractmethod
    def initialize_schema(self) -> None:
        """Creates tables, extensions, and indexes."""
        pass

    @abstractmethod
    def record_ingestion_run(
        self,
        corpus_version: str,
        embedding_model: str,
        vector_dimension: int,
        status: str = "RUNNING"
    ) -> str:
        """Records the start of an ingestion run and returns run_id."""
        pass

    @abstractmethod
    def complete_ingestion_run(
        self,
        run_id: str,
        status: str,
        total_docs: int,
        total_sections: int,
        total_chunks: int,
        error_log: Optional[str] = None
    ) -> None:
        """Marks ingestion run as complete."""
        pass

    @abstractmethod
    def insert_source(self, source_dict: Dict[str, Any]) -> str:
        """Inserts or updates an authoritative source record."""
        pass

    @abstractmethod
    def insert_document(self, doc_dict: Dict[str, Any]) -> str:
        """Inserts or updates an enacted statute record."""
        pass

    @abstractmethod
    def insert_sections(self, sections: List[Dict[str, Any]]) -> int:
        """Inserts statutory section records idempotently."""
        pass

    @abstractmethod
    def insert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: Optional[np.ndarray] = None
    ) -> int:
        """Inserts chunk records with dense embeddings and full-text indexing."""
        pass

    @abstractmethod
    def insert_concordance(self, concordance_list: List[Dict[str, Any]]) -> int:
        """Inserts verified statutory concordance records."""
        pass

    @abstractmethod
    def search_lexical(
        self,
        query: str,
        act_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        effective_date: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Executes full-text keyword search."""
        pass

    @abstractmethod
    def search_vector(
        self,
        query_vector: np.ndarray,
        act_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        effective_date: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Executes dense vector similarity search."""
        pass
