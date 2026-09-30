"""Indexing module for Indian legal knowledge database."""

from .schema import SCHEMA_SQL
from .database import IndianLegalDatabaseManager

__all__ = ["SCHEMA_SQL", "IndianLegalDatabaseManager"]
