"""Database abstraction and operational adapters for LegalAI RAG."""

from .base import BaseLegalDatabase
from .sqlite_adapter import SQLiteLegalDatabase

__all__ = ["BaseLegalDatabase", "SQLiteLegalDatabase"]
