#!/usr/bin/env python3
"""Runner script for the LegalAI Automated Indian Legal Corpus Expansion Engine."""

import sys
import os

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.legal_knowledge.expansion.cli import main

if __name__ == "__main__":
    main()
