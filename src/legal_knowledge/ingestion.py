"""Ingestion script for the initial verified General Indian Legal Knowledge MVP corpus.

Ingests:
1. Constitution of India (Preamble, Fundamental Rights Arts 14, 19, 21, Writ Arts 32, 226)
2. Information Technology Act, 2000 (Sec 43A, 66, 66A [Struck Down], 79)
3. Negotiable Instruments Act, 1881 (Sec 138, 139, 140, 141, 142)
4. Indian Contract Act, 1872 (Sec 10, 23, 73, 74)
5. Supreme Court Precedents:
   - Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal (2020) 7 SCC 1 (Electronic Evidence)
   - Shreya Singhal v. Union of India (2015) 5 SCC 1 (Section 66A IT Act Struck Down)
6. Imports existing BNS, BNSS, BSA corpus from legalai_rag_mvp.db
"""

import sqlite3
import os
import logging
from typing import Optional
from .models import (
    IndianLegalDocument,
    IndianLegalChunk,
    IndianDocumentType,
    IndianJurisdictionLevel,
    AuthorityTier,
    TemporalStatus,
    LegalDomain
)
from .indexing.database import IndianLegalDatabaseManager
from .parsers.statute_parser import IndianStatuteParser
from .parsers.judgment_parser import IndianJudgmentParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IndianLegalIngestion")


def ingest_initial_corpus(
    db_path: str = "data/legalai_indian_legal_knowledge.db",
    mvp_rag_path: str = "data/legalai_rag_mvp.db",
    embedder=None
):
    db_manager = IndianLegalDatabaseManager(db_path=db_path)
    statute_parser = IndianStatuteParser()
    judgment_parser = IndianJudgmentParser()

    logger.info("Ingesting Verified Indian Legal Corpus...")

    # =========================================================================
    # 1. CONSTITUTION OF INDIA
    # =========================================================================
    doc_const = IndianLegalDocument(
        document_id="DOC_CONSTITUTION_OF_INDIA",
        title="Constitution of India",
        document_type=IndianDocumentType.CONSTITUTION,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        country="India",
        act_prefix="COI",
        enactment_date="1949-11-26",
        commencement_date="1950-01-26",
        legal_domain=LegalDomain.CONSTITUTIONAL.value,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        effective_from="1950-01-26",
        official_source_url="https://www.indiacode.nic.in",
        source_id="SRC_INDIA_CODE",
        created_at="1950-01-26"
    )
    db_manager.upsert_document(doc_const)

    const_text = """
Article 14. Equality before law.
The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.

Article 19. Protection of certain rights regarding freedom of speech, etc.
(1) All citizens shall have the right—
(a) to freedom of speech and expression;
(b) to assemble peaceably and without arms;
(c) to form associations or unions or co-operative societies;
(d) to move freely throughout the territory of India;
(e) to reside and settle in any part of the territory of India; and
(g) to practise any profession, or to carry on any occupation, trade or business.
(2) Nothing in sub-clause (a) of clause (1) shall affect the operation of any existing law, or prevent the State from making any law, in so far as such law imposes reasonable restrictions on the exercise of the right conferred by the said sub-clause in the interests of the sovereignty and integrity of India, the security of the State, friendly relations with foreign States, public order, decency or morality, or in relation to contempt of court, defamation or incitement to an offence.

Article 21. Protection of life and personal liberty.
No person shall be deprived of his life or personal liberty except according to procedure established by law.

Article 32. Remedies for enforcement of rights conferred by this Part.
(1) The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed.
(2) The Supreme Court shall have power to issue directions or orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari, whichever may be appropriate, for the enforcement of any of the rights conferred by this Part.

Article 226. Power of High Courts to issue certain writs.
(1) Notwithstanding anything in article 32, every High Court shall have power, throughout the territories in relation to which it exercises jurisdiction, to issue to any person or authority, including in appropriate cases, any Government, within those territories directions, orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari, or any of them, for the enforcement of any of the rights conferred by Part III and for any other purpose.
"""
    const_chunks = statute_parser.parse_provisions(doc_const, const_text, default_chapter="Part III: Fundamental Rights")
    for chunk in const_chunks:
        db_manager.upsert_chunk(chunk)
    logger.info(f"Ingested {len(const_chunks)} Constitutional provisions.")

    # =========================================================================
    # 2. INFORMATION TECHNOLOGY ACT, 2000
    # =========================================================================
    doc_it = IndianLegalDocument(
        document_id="DOC_IT_ACT_2000",
        title="Information Technology Act, 2000",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        country="India",
        act_prefix="IT_ACT",
        act_number="Act No. 21 of 2000",
        enactment_date="2000-06-09",
        commencement_date="2000-10-17",
        legal_domain=LegalDomain.CYBER_TECH.value,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        effective_from="2000-10-17",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/1999",
        source_id="SRC_INDIA_CODE",
        created_at="2000-10-17"
    )
    db_manager.upsert_document(doc_it)

    it_text = """
Section 43A. Compensation for failure to protect data.
Where a body corporate, possessing, dealing or handling any sensitive personal data or information in a computer resource which it owns, controls or operates, is negligent in implementing and maintaining reasonable security practices and procedures and thereby causes wrongful loss or wrongful gain to any person, such body corporate shall be liable to pay damages by way of compensation to the person so affected.

Section 66. Computer related offences.
If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.

Section 66A. Punishment for sending offensive messages through communication service, etc.
Any person who sends, by means of a computer resource or a communication device,—
(a) any information that is grossly offensive or has menacing character; or
(b) any information which he knows to be false, but for the purpose of causing annoyance, inconvenience, danger, obstruction, insult, injury, criminal intimidation, enmity, hatred or ill will, persistently by making use of such computer resource or a communication device;
(c) any electronic mail or electronic mail message for the purpose of causing annoyance or inconvenience or to deceive or to mislead the addressee or recipient about the origin of such messages,
shall be punishable with imprisonment for a term which may extend to three years and with fine.
[CRITICAL JUDICIAL STATUS: Section 66A was struck down in its entirety as unconstitutional by the Supreme Court of India in Shreya Singhal v. Union of India (2015) 5 SCC 1 on 24 March 2015. It is NOT enforceable law.]

Section 79. Exemption from liability of intermediary in certain cases.
(1) Notwithstanding anything contained in any law for the time being in force but subject to the provisions of sub-sections (2) and (3), an intermediary shall not be liable for any third party information, data, or communication link made available or hosted by him.
(2) The provisions of sub-section (1) shall apply if—
(a) the function of the intermediary is limited to providing access to a communication system over which information made available by third parties is transmitted or temporarily stored or hosted; or
(b) the intermediary does not—
(i) initiate the transmission,
(ii) select the receiver of the transmission, and
(iii) select or modify the information contained in the transmission;
(c) the intermediary observes due diligence while discharging his duties under this Act and also observes such other guidelines as the Central Government may prescribe in this behalf.
"""
    it_chunks = statute_parser.parse_provisions(doc_it, it_text, default_chapter="Electronic Governance & Penalties")
    for chunk in it_chunks:
        if chunk.provision_number == "66A":
            chunk.temporal_status = TemporalStatus.STRUCK_DOWN
            chunk.transition_note = "STRUCK DOWN as unconstitutional by Supreme Court in Shreya Singhal v. Union of India (2015) 5 SCC 1"
        db_manager.upsert_chunk(chunk)
    logger.info(f"Ingested {len(it_chunks)} IT Act provisions.")

    # =========================================================================
    # 3. NEGOTIABLE INSTRUMENTS ACT, 1881
    # =========================================================================
    doc_ni = IndianLegalDocument(
        document_id="DOC_NI_ACT_1881",
        title="Negotiable Instruments Act, 1881",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        country="India",
        act_prefix="NI_ACT",
        act_number="Act No. 26 of 1881",
        enactment_date="1881-12-09",
        commencement_date="1882-03-01",
        legal_domain=LegalDomain.BANKING_FINANCE.value,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        effective_from="1882-03-01",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2264",
        source_id="SRC_INDIA_CODE",
        created_at="1882-03-01"
    )
    db_manager.upsert_document(doc_ni)

    ni_text = """
Section 138. Dishonour of cheque for insufficiency, etc., of funds in the account.
Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for a term which may be extended to two years, or with fine which may extend to twice the amount of the cheque, or with both:
Provided that nothing contained in this section shall apply unless—
(a) the cheque has been presented to the bank within a period of three months from the date on which it is drawn or within the period of its validity, whichever is earlier;
(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and
(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within fifteen days of the receipt of the said notice.

Section 139. Presumption in favour of holder.
It shall be presumed, unless the contrary is proved, that the holder of a cheque received the cheque of the nature referred to in section 138 for the discharge, in whole or in part, of any debt or other liability.

Section 140. Defence which may not be allowed in any prosecution under section 138.
It shall not be a defence in a prosecution for an offence under section 138 that the drawer had no reason to believe when he issued the cheque that the cheque may be dishonoured on presentment for the reasons stated in that section.

Section 141. Offences by companies.
(1) If the person committing an offence under section 138 is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly:
Provided that nothing contained in this sub-section shall render any person liable to punishment if he proves that the offence was committed without his knowledge, or that he had exercised all due diligence to prevent the commission of such offence.

Section 142. Cognizance of offences.
(1) Notwithstanding anything contained in the Code of Criminal Procedure, 1973—
(a) no court shall take cognizance of any offence punishable under section 138 except upon a complaint, in writing, made by the payee or, as the case may be, the holder in due course of the cheque;
(b) such complaint is made within one month of the date on which the cause of action arises under clause (c) of the proviso to section 138.
"""
    ni_chunks = statute_parser.parse_provisions(doc_ni, ni_text, default_chapter="Chapter XVII: Penalties in Case of Dishonour of Cheques")
    for chunk in ni_chunks:
        db_manager.upsert_chunk(chunk)
    logger.info(f"Ingested {len(ni_chunks)} NI Act provisions.")

    # =========================================================================
    # 4. INDIAN CONTRACT ACT, 1872
    # =========================================================================
    doc_contract = IndianLegalDocument(
        document_id="DOC_CONTRACT_ACT_1872",
        title="Indian Contract Act, 1872",
        document_type=IndianDocumentType.ACT,
        jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
        country="India",
        act_prefix="CONTRACT_ACT",
        act_number="Act No. 9 of 1872",
        enactment_date="1872-04-25",
        commencement_date="1872-09-01",
        legal_domain=LegalDomain.CONTRACT.value,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        effective_from="1872-09-01",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2187",
        source_id="SRC_INDIA_CODE",
        created_at="1872-09-01"
    )
    db_manager.upsert_document(doc_contract)

    contract_text = """
Section 10. What agreements are contracts.
All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void.
Nothing herein contained shall affect any law in force in India, and not hereby expressly repealed, by which any contract is required to be made in writing or in the presence of witnesses, or any law relating to the registration of documents.

Section 23. What considerations and objects are lawful, and what not.
The consideration or object of an agreement is lawful, unless—
it is forbidden by law; or
is of such a nature that, if permitted, it would defeat the provisions of any law; or
is fraudulent; or
involves or implies, injury to the person or property of another; or
the Court regards it as immoral, or opposed to public policy.
In each of these cases, the consideration or object of an agreement is said to be unlawful. Every agreement of which the object or consideration is unlawful is void.

Section 73. Compensation for loss or damage caused by breach of contract.
When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach, or which the parties knew, when they made the contract, to be likely to result from the breach of it.
Such compensation is not to be given for any remote and indirect loss or damage sustained by reason of the breach.

Section 74. Compensation for breach of contract where penalty stipulated for.
When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such breach, or if the contract contains any other stipulation by way of penalty, the party complaining of the breach is entitled, whether or not actual damage or loss is proved to have been caused thereby, to receive from the party who has broken the contract reasonable compensation not exceeding the amount so named or, as the case may be, the penalty stipulated for.
"""
    contract_chunks = statute_parser.parse_provisions(doc_contract, contract_text, default_chapter="Contracts & Void Agreements")
    for chunk in contract_chunks:
        db_manager.upsert_chunk(chunk)
    logger.info(f"Ingested {len(contract_chunks)} Contract Act provisions.")

    # =========================================================================
    # 5. AUTHORITATIVE SUPREME COURT PRECEDENTS
    # =========================================================================
    # 5A. Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal (2020) 7 SCC 1
    doc_arjun = IndianLegalDocument(
        document_id="DOC_SC_ARJUN_PANDITRAO",
        title="Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal",
        document_type=IndianDocumentType.JUDGMENT,
        jurisdiction_level=IndianJurisdictionLevel.SUPREME_COURT,
        country="India",
        court="Supreme Court of India",
        bench="3-Judge Bench",
        judges=["R.F. Nariman", "S. Ravindra Bhat", "V. Ramasubramanian"],
        act_prefix="SC_ARJUN_PANDITRAO",
        legal_domain=LegalDomain.EVIDENCE.value,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        effective_from="2020-07-14",
        official_source_url="https://judgments.ecourts.gov.in/pdfsearch/?app_token=SCR_2020_ARJUN",
        source_id="SRC_SCI_ESCR",
        created_at="2020-07-14"
    )
    db_manager.upsert_document(doc_arjun)

    arjun_chunks = judgment_parser.parse_judgment(
        document=doc_arjun,
        citation="(2020) 7 SCC 1",
        decision_date="2020-07-14",
        acts_discussed=["Indian Evidence Act, 1872", "Bharatiya Sakshya Adhiniyam, 2023"],
        sections_discussed=["Section 65B IEA", "Section 63 BSA", "Section 65A IEA"],
        headnote_or_summary=(
            "Admissibility of secondary electronic records in evidence — Requirement of Certificate under Section 65B(4) IEA "
            "(corresponding to Section 63 BSA) — Supreme Court resolves divergence between Anvar P.V. v. P.K. Basheer (2014) 10 SCC 473 "
            "and Shafhi Mohammad v. State of Himachal Pradesh (2018) 2 SCC 801."
        ),
        ratio_decidendi=(
            "The 3-Judge Bench held that the certificate required under Section 65B(4) of the Indian Evidence Act, 1872 "
            "(now Section 63 of Bharatiya Sakshya Adhiniyam, 2023) is a mandatory condition precedent for the admissibility "
            "of secondary evidence of electronic records. The judgment clarifies:\n"
            "1. Oral evidence cannot substitute for the mandatory written certificate under Section 65B(4).\n"
            "2. Shafhi Mohammad was wrongly decided and is expressly overruled to the extent it held that the certificate could be dispensed with.\n"
            "3. The certificate is not required if the original electronic device itself is produced in court by the owner/author.\n"
            "4. Where the party seeking to rely on the electronic record is unable to procure the certificate because the device is in the custody of an adverse party or third party, an application can be made to the court to compel production under Section 91 CrPC / Order XVI CPC."
        ),
        operative_order="Reference answered confirming Anvar P.V. and overruling Shafhi Mohammad. Compliance with Section 65B(4) held mandatory."
    )
    for chunk in arjun_chunks:
        db_manager.upsert_chunk(chunk)
    logger.info(f"Ingested {len(arjun_chunks)} chunks for Arjun Panditrao Khotkar precedent.")

    # 5B. Shreya Singhal v. Union of India (2015) 5 SCC 1
    doc_shreya = IndianLegalDocument(
        document_id="DOC_SC_SHREYA_SINGHAL",
        title="Shreya Singhal v. Union of India",
        document_type=IndianDocumentType.JUDGMENT,
        jurisdiction_level=IndianJurisdictionLevel.SUPREME_COURT,
        country="India",
        court="Supreme Court of India",
        bench="Division Bench (2 Judges)",
        judges=["J. Chelameswar", "R.F. Nariman"],
        act_prefix="SC_SHREYA_SINGHAL",
        legal_domain=LegalDomain.CONSTITUTIONAL.value,
        authority_tier=AuthorityTier.TIER_1_PRIMARY,
        temporal_status=TemporalStatus.CURRENT,
        effective_from="2015-03-24",
        official_source_url="https://judgments.ecourts.gov.in/pdfsearch/?app_token=SCR_2015_SHREYA",
        source_id="SRC_SCI_ESCR",
        created_at="2015-03-24"
    )
    db_manager.upsert_document(doc_shreya)

    shreya_chunks = judgment_parser.parse_judgment(
        document=doc_shreya,
        citation="(2015) 5 SCC 1",
        decision_date="2015-03-24",
        acts_discussed=["Information Technology Act, 2000", "Constitution of India"],
        sections_discussed=["Section 66A IT Act", "Section 69A IT Act", "Section 79 IT Act", "Article 19(1)(a)", "Article 19(2)"],
        headnote_or_summary=(
            "Constitutional validity of Section 66A, Section 69A, and Section 79 of the Information Technology Act, 2000 — "
            "Freedom of speech and expression on the Internet versus reasonable restrictions under Article 19(2) — "
            "Vagueness, chilling effect, and overbreadth."
        ),
        ratio_decidendi=(
            "The Supreme Court declared Section 66A of the Information Technology Act, 2000 unconstitutional in its entirety "
            "as it infringes the fundamental right to freedom of speech and expression guaranteed under Article 19(1)(a) "
            "and is not saved by any of the reasonable restrictions in Article 19(2).\n"
            "Key holdings:\n"
            "1. Section 66A is void for vagueness: Terms like 'annoyance', 'inconvenience', 'grossly offensive' are undefined and open to arbitrary misuse.\n"
            "2. Discussion and advocacy on the internet cannot be criminalized unless it reaches the threshold of incitement.\n"
            "3. Section 79(3)(b) read down: Intermediaries are only required to take down content upon receiving actual knowledge by a court order or authorized government notification, not upon mere private complaint."
        ),
        operative_order="Section 66A struck down as unconstitutional. Section 79(3)(b) read down to require court order or government direction."
    )
    for chunk in shreya_chunks:
        db_manager.upsert_chunk(chunk)
    logger.info(f"Ingested {len(shreya_chunks)} chunks for Shreya Singhal precedent.")

    # =========================================================================
    # 6. IMPORT EXISTING CRIMINAL STATUTE CORPUS (BNS, BNSS, BSA)
    # =========================================================================
    if os.path.exists(mvp_rag_path):
        logger.info(f"Importing existing criminal corpus from {mvp_rag_path}...")
        try:
            conn_mvp = sqlite3.connect(mvp_rag_path)
            conn_mvp.row_factory = sqlite3.Row
            cursor_mvp = conn_mvp.cursor()

            # Import documents
            cursor_mvp.execute("SELECT * FROM legal_documents")
            docs = cursor_mvp.fetchall()
            for d in docs:
                ind_doc = IndianLegalDocument(
                    document_id=d["document_id"],
                    title=d["act_name"],
                    document_type=IndianDocumentType.ACT,
                    jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
                    country="India",
                    act_prefix=d["act_prefix"],
                    act_number=d["act_number"],
                    enactment_date=d["enactment_date"],
                    commencement_date=d["commencement_date"],
                    legal_domain=LegalDomain.CRIMINAL.value if d["act_prefix"] != "BSA" else LegalDomain.EVIDENCE.value,
                    authority_tier=AuthorityTier.TIER_1_PRIMARY,
                    temporal_status=TemporalStatus.CURRENT,
                    effective_from=d["commencement_date"],
                    official_source_url="https://www.indiacode.nic.in",
                    source_id="SRC_INDIA_CODE",
                    created_at=d["created_at"]
                )
                db_manager.upsert_document(ind_doc)

            # Import chunks
            cursor_mvp.execute("SELECT * FROM legal_chunks")
            chunks = cursor_mvp.fetchall()
            count = 0
            for c in chunks:
                ind_chunk = IndianLegalChunk(
                    chunk_id=c["chunk_id"],
                    document_id=f"DOC_{c['act_prefix']}",
                    title=f"{c['act_name']} Section {c['section_number']}",
                    act_name=c["act_name"],
                    act_prefix=c["act_prefix"],
                    section_or_article=f"Section {c['section_number']}",
                    provision_number=c["section_number"],
                    provision_title=c["section_title"],
                    chapter=c["chapter"],
                    content=c["content"],
                    raw_text=c["raw_section_text"],
                    document_type=IndianDocumentType.ACT,
                    jurisdiction_level=IndianJurisdictionLevel.CENTRAL,
                    country="India",
                    legal_domain=LegalDomain.CRIMINAL.value if c["act_prefix"] != "BSA" else LegalDomain.EVIDENCE.value,
                    authority_tier=AuthorityTier.TIER_1_PRIMARY,
                    temporal_status=TemporalStatus.CURRENT,
                    effective_from=c["effective_from"],
                    effective_until=c["effective_to"],
                    transition_note="Governed by 1 July 2024 commencement",
                    official_source_url=c["source_url"],
                    content_hash=c["content_hash"],
                    embedding_blob=c["embedding_blob"]
                )
                db_manager.upsert_chunk(ind_chunk)
                count += 1

            conn_mvp.close()
            logger.info(f"Successfully imported {count} criminal provisions from BNS, BNSS, and BSA.")
        except Exception as e:
            logger.warning(f"Failed to import from {mvp_rag_path}: {e}")
    else:
        logger.warning(f"Existing MVP database not found at {mvp_rag_path}")

    logger.info(
        f"Corpus ingestion completed! Total Documents: {db_manager.get_document_count()} | "
        f"Total Legal Chunks: {db_manager.get_chunk_count()}"
    )


if __name__ == "__main__":
    ingest_initial_corpus()
