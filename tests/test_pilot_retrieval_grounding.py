"""Grounding, provenance, and retrieval verification tests against the genuine India Code Central Acts pilot.

Validates that statutory texts are retrieved from official India Code full-act ingestions,
covering multiple chapters/provisions across all 12 pilot Acts.
"""

import pytest
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline


@pytest.fixture(scope="module")
def pipeline():
    return GeneralIndianLegalKnowledgePipeline(db_path="data/legalai_indian_legal_knowledge.db")


# ----------------------------------------------------------------------
# 1. Companies Act, 2013 (Multiple Chapters: Ch. II Incorporation & Ch. XI Directors)
# ----------------------------------------------------------------------
def test_grounding_01_companies_act_incorporation(pipeline):
    """Verifies retrieval of Section 7 Companies Act on incorporation documents."""
    res = pipeline.query("What documents must be filed for incorporation of a company under Section 7 of Companies Act?")
    assert not res["abstained"]
    assert "Section 7" in res["answer"]
    assert "Companies Act, 2013" in res["answer"]
    assert any("COMPANIES_ACT_2013" in s["chunk_id"] for s in res["sources"])
    assert any("indiacode.gov.in" in s["source_url"] for s in res["sources"])


def test_grounding_02_companies_act_board_of_directors(pipeline):
    """Verifies retrieval of Section 149 Companies Act on Board of Directors."""
    res = pipeline.query("What are the requirements for board of directors and independent directors under Section 149 of Companies Act?")
    assert not res["abstained"]
    assert "Section 149" in res["answer"]
    assert "Companies Act, 2013" in res["answer"]
    assert any("COMPANIES_ACT_2013" in s["chunk_id"] for s in res["sources"])
    assert any("indiacode.gov.in" in s["source_url"] for s in res["sources"])


# ----------------------------------------------------------------------
# 2. Insolvency and Bankruptcy Code, 2016 (CIRP Initiation & Moratorium)
# ----------------------------------------------------------------------
def test_grounding_03_ibc_operational_creditor(pipeline):
    """Verifies retrieval of Section 9 IBC on operational creditor CIRP initiation."""
    res = pipeline.query("How can an operational creditor initiate corporate insolvency resolution process under Section 9 of IBC?")
    assert not res["abstained"]
    assert "Section 9" in res["answer"]
    assert "Insolvency and Bankruptcy Code" in res["answer"]
    assert any("IBC_2016" in s["chunk_id"] for s in res["sources"])
    assert any("indiacode.gov.in" in s["source_url"] for s in res["sources"])


def test_grounding_04_ibc_moratorium(pipeline):
    """Verifies retrieval of Section 14 IBC on declaration of moratorium."""
    res = pipeline.query("What are the effects and prohibitions of moratorium under Section 14 of Insolvency and Bankruptcy Code?")
    assert not res["abstained"]
    assert "Section 14" in res["answer"]
    assert "Insolvency and Bankruptcy Code" in res["answer"]
    assert any("IBC_2016" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 3. Arbitration and Conciliation Act, 1996 (Interim Measures & Setting Aside Award)
# ----------------------------------------------------------------------
def test_grounding_05_arbitration_interim_measures(pipeline):
    """Verifies retrieval of Section 9 Arbitration Act on interim measures by court."""
    res = pipeline.query("What interim measures can a court grant under Section 9 of Arbitration and Conciliation Act?")
    assert not res["abstained"]
    assert "Section 9" in res["answer"]
    assert "Arbitration and Conciliation Act" in res["answer"]
    assert any("ARBITRATION_ACT_1996" in s["chunk_id"] for s in res["sources"])
    assert any("indiacode.gov.in" in s["source_url"] for s in res["sources"])


def test_grounding_06_arbitration_setting_aside_award(pipeline):
    """Verifies retrieval of Section 34 Arbitration Act on setting aside arbitral award."""
    res = pipeline.query("What are the grounds for setting aside an arbitral award under Section 34 of Arbitration and Conciliation Act?")
    assert not res["abstained"]
    assert "Section 34" in res["answer"]
    assert "Arbitration and Conciliation Act" in res["answer"]
    assert any("ARBITRATION_ACT_1996" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 4. POCSO Act, 2012 (Punishment & Mandatory Reporting)
# ----------------------------------------------------------------------
def test_grounding_07_pocso_punishment(pipeline):
    """Verifies retrieval of Section 4 POCSO on penetrative sexual assault."""
    res = pipeline.query("What is the punishment for penetrative sexual assault under Section 4 of POCSO Act?")
    assert not res["abstained"]
    assert "Section 4" in res["answer"]
    assert "POCSO" in res["answer"] or "Protection of Children" in res["answer"]
    assert any("POCSO_ACT_2012" in s["chunk_id"] for s in res["sources"])


def test_grounding_08_pocso_reporting_offences(pipeline):
    """Verifies retrieval of Section 19 POCSO on mandatory reporting."""
    res = pipeline.query("What is the procedure for reporting of offences under Section 19 of POCSO Act?")
    assert not res["abstained"]
    assert "Section 19" in res["answer"]
    assert "POCSO" in res["answer"] or "Protection of Children" in res["answer"]
    assert any("POCSO_ACT_2012" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 5. Prevention of Money-Laundering Act, 2002 (Offence & Bail Conditions)
# ----------------------------------------------------------------------
def test_grounding_09_pmla_offence_definition(pipeline):
    """Verifies retrieval of Section 3 PMLA defining offence of money-laundering."""
    res = pipeline.query("What constitutes the offence of money-laundering under Section 3 of PMLA?")
    assert not res["abstained"]
    assert "Section 3" in res["answer"]
    assert "Money-Laundering" in res["answer"]
    assert any("PMLA_2002" in s["chunk_id"] for s in res["sources"])


def test_grounding_10_pmla_bail_conditions(pipeline):
    """Verifies retrieval of Section 45 PMLA on non-bailable offences and twin conditions."""
    res = pipeline.query("What are the twin conditions for granting bail under Section 45 of Prevention of Money-Laundering Act?")
    assert not res["abstained"]
    assert "Section 45" in res["answer"]
    assert "Money-Laundering" in res["answer"]
    assert any("PMLA_2002" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 6. Transfer of Property Act, 1882 (Sale & Mortgage)
# ----------------------------------------------------------------------
def test_grounding_11_transfer_of_property_sale(pipeline):
    """Verifies retrieval of Section 54 Transfer of Property Act defining sale."""
    res = pipeline.query("How is sale defined and how is transfer effected under Section 54 of Transfer of Property Act?")
    assert not res["abstained"]
    assert "Section 54" in res["answer"]
    assert "Transfer of Property Act" in res["answer"]
    assert any("TRANSFER_OF_PROPERTY_ACT_1882" in s["chunk_id"] for s in res["sources"])


def test_grounding_12_transfer_of_property_mortgage(pipeline):
    """Verifies retrieval of Section 58 Transfer of Property Act defining mortgage."""
    res = pipeline.query("How is mortgage defined under Section 58 of Transfer of Property Act?")
    assert not res["abstained"]
    assert "Section 58" in res["answer"]
    assert "Transfer of Property Act" in res["answer"]
    assert any("TRANSFER_OF_PROPERTY_ACT_1882" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 7. Code of Civil Procedure, 1908 (First Appeal & Second Appeal)
# ----------------------------------------------------------------------
def test_grounding_13_cpc_appeal_from_original_decree(pipeline):
    """Verifies retrieval of Section 96 Code of Civil Procedure on first appeal."""
    res = pipeline.query("Under what section of CPC does an appeal lie from an original decree?")
    assert not res["abstained"]
    assert "Section 96" in res["answer"]
    assert "Civil Procedure" in res["answer"]
    assert any("CPC_1908" in s["chunk_id"] for s in res["sources"])


def test_grounding_14_cpc_second_appeal(pipeline):
    """Verifies retrieval of Section 100 Code of Civil Procedure on second appeal."""
    res = pipeline.query("When does a second appeal lie to the High Court under Section 100 of Code of Civil Procedure?")
    assert not res["abstained"]
    assert "Section 100" in res["answer"]
    assert "Civil Procedure" in res["answer"]
    assert any("CPC_1908" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 8. NDPS Act, 1985 (Cannabis Offences & Search Safeguards)
# ----------------------------------------------------------------------
def test_grounding_15_ndps_cannabis_contravention(pipeline):
    """Verifies retrieval of Section 20 NDPS Act on cannabis contravention."""
    res = pipeline.query("What is the punishment for contravention in relation to cannabis under Section 20 of NDPS Act?")
    assert not res["abstained"]
    assert "Section 20" in res["answer"]
    assert "Narcotic Drugs" in res["answer"]
    assert any("NDPS_ACT_1985" in s["chunk_id"] for s in res["sources"])


def test_grounding_16_ndps_search_conditions(pipeline):
    """Verifies retrieval of Section 50 NDPS Act on conditions of personal search."""
    res = pipeline.query("What are the conditions under which search of persons shall be conducted under Section 50 of NDPS Act?")
    assert not res["abstained"]
    assert "Section 50" in res["answer"]
    assert "Narcotic Drugs" in res["answer"]
    assert any("NDPS_ACT_1985" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 9. Motor Vehicles Act, 1988 (Accident Duty & Drunken Driving)
# ----------------------------------------------------------------------
def test_grounding_17_motor_vehicles_accident_duty(pipeline):
    """Verifies retrieval of Section 134 Motor Vehicles Act on duty in case of accident."""
    res = pipeline.query("What is the duty of a driver in case of an accident and injury to a person under Section 134 of Motor Vehicles Act?")
    assert not res["abstained"]
    assert "Section 134" in res["answer"]
    assert "Motor Vehicles Act" in res["answer"]
    assert any("MOTOR_VEHICLES_ACT_1988" in s["chunk_id"] for s in res["sources"])


def test_grounding_18_motor_vehicles_drunken_driving(pipeline):
    """Verifies retrieval of Section 185 Motor Vehicles Act on drunken driving."""
    res = pipeline.query("What is the legal limit and penalty for drunken driving under Section 185 of Motor Vehicles Act?")
    assert not res["abstained"]
    assert "Section 185" in res["answer"]
    assert "Motor Vehicles Act" in res["answer"]
    assert any("MOTOR_VEHICLES_ACT_1988" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 10. Specific Relief Act, 1963 (Specific Performance & Injunctions)
# ----------------------------------------------------------------------
def test_grounding_19_specific_relief_performance(pipeline):
    """Verifies retrieval of Section 10 Specific Relief Act on specific performance."""
    res = pipeline.query("When can specific performance of a contract be enforced under Section 10 of Specific Relief Act?")
    assert not res["abstained"]
    assert "Section 10" in res["answer"]
    assert "Specific Relief Act" in res["answer"]
    assert any("SPECIFIC_RELIEF_ACT_1963" in s["chunk_id"] for s in res["sources"])


def test_grounding_20_specific_relief_injunction(pipeline):
    """Verifies retrieval of Section 38 Specific Relief Act on perpetual injunctions."""
    res = pipeline.query("When can a perpetual injunction be granted under Section 38 of Specific Relief Act?")
    assert not res["abstained"]
    assert "Section 38" in res["answer"]
    assert "Specific Relief Act" in res["answer"]
    assert any("SPECIFIC_RELIEF_ACT_1963" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 11. Consumer Protection Act, 2019 (Complaint Filing Procedure)
# ----------------------------------------------------------------------
def test_grounding_21_consumer_protection_complaint_filing(pipeline):
    """Verifies retrieval of Section 35 Consumer Protection Act on manner of complaint."""
    res = pipeline.query("What is the manner in which a complaint shall be made under Section 35 of Consumer Protection Act?")
    assert not res["abstained"]
    assert "Section 35" in res["answer"]
    assert "Consumer Protection Act" in res["answer"]
    assert any("CONSUMER_PROTECTION_ACT_2019" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 12. SC/ST (POA) Act, 1989 (Atrocity Offences & Anticipatory Bail Exclusion)
# ----------------------------------------------------------------------
def test_grounding_22_sc_st_poa_anticipatory_bail_bar(pipeline):
    """Verifies retrieval of Section 18 SC/ST Prevention of Atrocities Act excluding Section 438 CrPC."""
    res = pipeline.query("Does anticipatory bail under Section 438 of the Code apply under Section 18 of SC and ST Prevention of Atrocities Act?")
    assert not res["abstained"]
    assert "Section 18" in res["answer"]
    assert "Scheduled Castes and the Scheduled Tribes" in res["answer"]
    assert any("SC_ST_POA_ACT_1989" in s["chunk_id"] for s in res["sources"])


# ----------------------------------------------------------------------
# 13. Provenance & Metadata Integrity Assertions
# ----------------------------------------------------------------------
def test_grounding_23_provenance_metadata_completeness(pipeline):
    """Verifies that retrieved chunks from pilot Acts contain complete official India Code provenance."""
    res = pipeline.query("Explain Section 7 of Companies Act 2013 and Section 9 of Arbitration Act 1996.")
    assert len(res["sources"]) > 0
    for s in res["sources"]:
        assert "indiacode.gov.in" in s["source_url"]
        assert s["temporal_status"] in ["CURRENT", "IN_FORCE"]
        assert s["authority_tier"] == "TIER_1_PRIMARY"
        assert s["document_type"] == "ACT"


# ----------------------------------------------------------------------
# 14. Domain Separation / No Cross-Domain Leakage
# ----------------------------------------------------------------------
def test_grounding_24_no_wrong_domain_leakage(pipeline):
    """Verifies that a corporate law inquiry does not return unrelated criminal sexual offence sections."""
    res = pipeline.query("What are the rules regarding incorporation of a company under Section 7 of Companies Act?")
    for s in res["sources"]:
        assert "POCSO" not in s["chunk_id"]
        assert "BNS_103" not in s["chunk_id"]
        assert "BNS_64" not in s["chunk_id"]
