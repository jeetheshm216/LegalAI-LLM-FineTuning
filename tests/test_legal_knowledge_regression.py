#!/usr/bin/env python3
"""Comprehensive unit and regression test suite for LegalAI Indian Legal Knowledge System."""

import unittest
import os
import sys
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from src.legal_knowledge.models import (
    ProvisionType,
    IndianDocumentType,
    AuthorityTier,
    TemporalStatus,
    SearchFilter
)
from src.legal_knowledge.sources.registry import IndianSourceRegistry
from src.legal_knowledge.sources.providers import IndiaCodeProvider, GazetteProvider, SupremeCourtProvider
from src.legal_knowledge.indexing.database import IndianLegalDatabaseManager
from src.legal_knowledge.retrieval.act_resolver import IndianActResolver
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline


class TestLegalKnowledgeCorpusAndRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = IndianLegalDatabaseManager()
        cls.registry = IndianSourceRegistry()
        cls.resolver = IndianActResolver(cls.db)
        cls.pipeline = GeneralIndianLegalKnowledgePipeline()

    # 1. Sources & Providers Tests
    def test_sources_registry_and_domains(self):
        sources = self.registry.list_sources()
        self.assertGreaterEqual(len(sources), 5)
        source_domains = {s.domain for s in sources}
        self.assertIn("indiacode.nic.in", source_domains)
        self.assertIn("egazette.gov.in", source_domains)
        self.assertIn("judgments.ecourts.gov.in", source_domains)

    def test_provider_domain_provenance(self):
        provider = IndiaCodeProvider()
        self.assertTrue(provider.verify_provenance("https://indiacode.gov.in/handle/123456789/496128"))
        self.assertTrue(provider.verify_provenance("https://indiacode.nic.in/bitstream/123"))
        self.assertFalse(provider.verify_provenance("https://indiankanoon.org/doc/123/"))
        self.assertFalse(provider.verify_provenance("https://scconline.com/doc/456/"))

    def test_gazette_provider_safety(self):
        gp = GazetteProvider()
        success, _, _, msg = gp.fetch_document("nonexistent")
        self.assertFalse(success)
        self.assertIn("MANUAL_SOURCE_REQUIRED", msg)

    # 2. Database & Namespace Isolation Tests
    def test_database_counts(self):
        self.assertEqual(self.db.get_document_count(), 37)
        self.assertEqual(self.db.get_chunk_count(), 3971)

    def test_no_namespace_collisions(self):
        collisions = self.db.check_collision_matrix()
        self.assertEqual(len(collisions), 0, f"Detected namespace collisions: {collisions}")

    def test_strict_namespace_retrieval(self):
        # Section 89 of Companies Act
        sec89 = self.db.get_chunk_by_provision("COMPANIES_ACT_2013", "89", provision_type="SECTION")
        self.assertIsNotNone(sec89)
        self.assertEqual(sec89.provision_type, ProvisionType.SECTION)
        self.assertNotIn("Schedule", sec89.section_or_article)

        # Order 39 Rule 1 of CPC
        order39 = self.db.get_chunk_by_provision("CPC_1908", "ORDER_39_RULE_1", provision_type="ORDER_RULE")
        self.assertIsNotNone(order39)
        self.assertEqual(order39.provision_type, ProvisionType.ORDER_RULE)
        self.assertIn("Order XXXIX", order39.section_or_article)

        # Article 21 of Constitution
        art21 = self.db.get_chunk_by_provision("COI", "21", provision_type="ARTICLE")
        self.assertIsNotNone(art21)
        self.assertEqual(art21.provision_type, ProvisionType.ARTICLE)
        self.assertIn("Article 21", art21.section_or_article)

    # 3. Query Understanding & Act Resolver Tests
    def test_exact_provision_resolver(self):
        res = self.resolver.resolve("What is Section 89 of the Companies Act, 2013?")
        self.assertEqual(res["intent"], "EXACT_PROVISION_QUERY")
        self.assertEqual(res["act_prefix"], "COMPANIES_ACT_2013")
        self.assertEqual(res["provision_number"], "89")
        self.assertEqual(res["provision_type"], "SECTION")

    def test_context_inheritance(self):
        history = [{"content": "What is Section 89 of the Companies Act, 2013?"}]
        res = self.resolver.resolve("What about Section 90?", conversation_history=history)
        self.assertEqual(res["intent"], "EXACT_PROVISION_QUERY")
        self.assertEqual(res["act_prefix"], "COMPANIES_ACT_2013")
        self.assertEqual(res["provision_number"], "90")
        self.assertTrue(res["inherited_from_history"])

    def test_context_override(self):
        history = [{"content": "What is Section 89 of the Companies Act, 2013?"}]
        res = self.resolver.resolve("What about Section 21 of the POCSO Act?", conversation_history=history)
        self.assertEqual(res["intent"], "EXACT_PROVISION_QUERY")
        self.assertEqual(res["act_prefix"], "POCSO_ACT_2012")
        self.assertEqual(res["provision_number"], "21")
        self.assertFalse(res["inherited_from_history"])

    def test_ambiguity_clarification(self):
        res = self.resolver.resolve("Tell me about Section 49A.")
        self.assertEqual(res["intent"], "AMBIGUOUS_PROVISION")
        self.assertTrue(res["needs_clarification"])
        self.assertIn("Which Act or Code", res["clarification_question"])

    def test_act_overview(self):
        res = self.resolver.resolve("What is the Companies Act, 2013?")
        self.assertEqual(res["intent"], "ACT_OVERVIEW")
        self.assertEqual(res["act_prefix"], "COMPANIES_ACT_2013")

    # 4. Pipeline Execution & Safe Abstention Tests
    def test_pipeline_exact_retrieval(self):
        res = self.pipeline.query("What is Section 89 of the Companies Act, 2013?")
        self.assertEqual(res["response_type"], "EXACT_VERIFIED")
        self.assertFalse(res["abstained"])
        self.assertFalse(res["requires_verification"])
        self.assertEqual(len(res["sources"]), 1)
        self.assertEqual(res["sources"][0]["provision_number"], "89")

    def test_pipeline_safe_abstention_nonexistent_section(self):
        res = self.pipeline.query("What is Section 49A of the Companies Act, 2013?")
        self.assertEqual(res["response_type"], "EXACT_NOT_VERIFIED")
        self.assertTrue(res["abstained"])
        self.assertTrue(res["requires_verification"])
        self.assertEqual(len(res["sources"]), 0)
        self.assertIn("could not be verified", res["answer"])

    def test_pipeline_ambiguous_provision_prompt(self):
        res = self.pipeline.query("Tell me about Section 49A.")
        self.assertEqual(res["response_type"], "AMBIGUOUS_PROVISION")
        self.assertTrue(res["needs_clarification"])
        self.assertIn("Clarification Required", res["answer"])

    # 5. Audit Reports Verification
    def test_reports_exist_and_valid(self):
        for rep in [
            "corpus_inventory_report.json",
            "corpus_validation_report.json",
            "corpus_coverage_report.json",
            "corpus_collision_report.json",
            "corpus_manifest.json"
        ]:
            p = os.path.join(REPO_ROOT, rep)
            self.assertTrue(os.path.exists(p), f"Missing report: {rep}")
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, f"Invalid JSON in {rep}")


if __name__ == "__main__":
    unittest.main()

