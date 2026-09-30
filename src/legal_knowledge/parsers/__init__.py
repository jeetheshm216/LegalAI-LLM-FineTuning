"""Parsers for Indian legal documents and judgments."""

from .statute_parser import IndianStatuteParser
from .judgment_parser import IndianJudgmentParser

__all__ = ["IndianStatuteParser", "IndianJudgmentParser"]
