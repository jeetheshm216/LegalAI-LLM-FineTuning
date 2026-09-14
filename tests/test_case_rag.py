"""
tests/test_case_rag.py

Comprehensive test suite for LegalAI Case Document RAG + Case Analysis V1.
Covers:
1. Document extraction (PDF, page preservation, metadata)
2. Chunking with strict page provenance ({doc_id}-p{page}-c{idx})
3. Case-isolated indexing and retrieval (Mandatory security: case-A vs case-B)
4. Evidence gap detection (CCTV referenced but unprovided)
5. Contradiction detection (8:00 PM vs 9:00 PM time conflict)
6. Empty case safe response (Zero documents -> Insufficient case material)
7. Statutory Legal RAG separation (Corpus isolation)
"""

import os
import sys
import shutil
import sqlite3
import pytest
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.case_rag.models import CaseDocument, DocumentChunk, EvidenceStatus
from src.case_rag.document_processor import DocumentProcessor, ExtractedPage
from src.case_rag.chunker import CaseDocumentChunker
from src.case_rag.embeddings import CaseEmbedder
from src.case_rag.index import CaseRAGIndex
from src.case_rag.retriever import CaseRetriever
from src.case_rag.pipeline import CaseRAGPipeline, EMPTY_CASE_RESPONSE


TEST_DB_PATH = REPO_ROOT / "data" / "test_case_rag.db"
DEMO_DIR = REPO_ROOT / "data" / "demo_case"


@pytest.fixture(scope="module")
def setup_test_index():
    """Initializes a fresh test Case RAG index with the demo documents."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    embedder = CaseEmbedder()
    pipeline = CaseRAGPipeline(
        index_db_path=str(TEST_DB_PATH),
        embedder=embedder
    )

    # Ingest Case A (demo case: case-demo-01)
    case_a_files = [
        ("FIR.pdf", "FIR"),
        ("Witness_Statement_01.pdf", "Witness Statement"),
        ("Medical_Report.pdf", "Medical Report"),
        ("Seizure_Record.pdf", "Seizure Record")
    ]

    for fname, category in case_a_files:
        fpath = DEMO_DIR / fname
        if fpath.exists():
            pipeline.ingest_document(
                case_id="case-demo-01",
                file_path=str(fpath),
                filename=fname,
                category=category
            )

    # Ingest Case B (separate case: case-demo-02) with completely different topic
    tmp_b_file = Path("/tmp/Patent_License.txt")
    with open(tmp_b_file, "w", encoding="utf-8") as f:
        f.write("Alpha Pharmaceuticals patent licensing agreement entered into on 10 January 2023 for formulation XY-99.")

    pipeline.ingest_document(
        case_id="case-demo-02",
        file_path=str(tmp_b_file),
        filename="Patent_License.txt",
        category="Pleading"
    )

    yield {
        "index": pipeline.index,
        "retriever": pipeline.retriever,
        "processor": pipeline.processor,
        "chunker": pipeline.chunker,
        "pipeline": pipeline
    }

    # Cleanup
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    if tmp_b_file.exists():
        tmp_b_file.unlink()


# -------------------------------------------------------------
# Unit Tests
# -------------------------------------------------------------

def test_01_pdf_page_extraction_preserves_provenance(setup_test_index):
    """Test 1: Verify PDF extraction extracts each page individually with exact page number."""
    processor = setup_test_index["processor"]
    fir_path = DEMO_DIR / "FIR.pdf"
    assert fir_path.exists(), "FIR.pdf must exist in demo_case"

    pages = processor.process_file(str(fir_path))
    assert len(pages) == 2, f"Expected 2 pages in FIR.pdf, got {len(pages)}"

    p1 = pages[0]
    assert p1.page_number == 1
    assert "FIRST INFORMATION REPORT" in p1.text
    assert "8:00 PM" in p1.text

    p2 = pages[1]
    assert p2.page_number == 2
    assert "CCTV" in p2.text
    assert "WhatsApp" in p2.text


def test_02_chunk_metadata_preservation(setup_test_index):
    """Test 2: Verify chunk ID and metadata preserve document ID, case ID, page number, and chunk index."""
    chunker = setup_test_index["chunker"]
    t1 = "Page 1 content discussing preliminary facts."
    t2 = "Page 2 content discussing subsequent evidence."
    pages = [
        ExtractedPage(page_number=1, text=t1, char_count=len(t1)),
        ExtractedPage(page_number=2, text=t2, char_count=len(t2))
    ]
    chunks = chunker.chunk_document(
        document_id="doc-test-101",
        document_name="TestDoc.pdf",
        case_id="case-test-99",
        pages=pages,
        document_type="FIR"
    )

    assert len(chunks) >= 2
    for c in chunks:
        assert c.case_id == "case-test-99"
        assert c.document_id == "doc-test-101"
        assert c.document_name == "TestDoc.pdf"
        assert c.page_number in [1, 2]
        assert f"doc-test-101-p{c.page_number}-c" in c.chunk_id


def test_03_case_isolation_security(setup_test_index):
    """Test 3: MANDATORY SECURITY TEST: Case A documents can NEVER be retrieved for Case B query."""
    retriever = setup_test_index["retriever"]

    # Query Case A for Case B's content ("patent licensing agreement XY-99")
    results_in_a = retriever.retrieve(
        query="patent licensing agreement formulation XY-99",
        case_id="case-demo-01",
        top_k=5
    )
    # None of Case B's documents should appear in Case A
    for r in results_in_a:
        assert r.document_name != "Patent_License.txt"
        assert "XY-99" not in r.text

    # Query Case B for Case A's content ("CCTV footage FIR robbery knife")
    results_in_b = retriever.retrieve(
        query="CCTV footage knife robbery FIR",
        case_id="case-demo-02",
        top_k=5
    )
    # Exactly 0 results or only Patent_License.txt, NEVER FIR or Witness statements
    for r in results_in_b:
        assert r.document_name == "Patent_License.txt"
        assert "CCTV" not in r.text
        assert "FIR" not in r.text


def test_04_contradiction_retrieval(setup_test_index):
    """Test 4: Verify retrieval finds contradictory time statements between FIR and Witness."""
    retriever = setup_test_index["retriever"]
    results = retriever.retrieve(
        query="time of incident occurrence evening 8:00 PM or 9:00 PM",
        case_id="case-demo-01",
        top_k=6
    )

    docs_found = {r.document_name for r in results}
    assert "FIR.pdf" in docs_found, "FIR should be retrieved for incident timing"
    assert "Witness_Statement_01.pdf" in docs_found, "Witness statement should be retrieved for timing"

    # Verify both timestamps are present in retrieved chunks
    all_text = " ".join([r.text for r in results])
    assert "8:00 PM" in all_text, "FIR time 8:00 PM should be in retrieved text"
    assert "9:00 PM" in all_text, "Witness time 9:00 PM should be in retrieved text"


def test_05_evidence_gap_cctv_retrieval(setup_test_index):
    """Test 5: Verify retrieval for CCTV footage returns references in FIR and Witness without fabricating CCTV file."""
    retriever = setup_test_index["retriever"]
    index = setup_test_index["index"]

    results = retriever.retrieve(
        query="Where is the CCTV footage and recording device?",
        case_id="case-demo-01",
        top_k=5
    )

    cctv_chunks = [r for r in results if "CCTV" in r.text]
    assert len(cctv_chunks) > 0, "Should retrieve CCTV references"

    # Verify that in database, no document titled CCTV or video exists
    conn = index._get_connection()
    c = conn.cursor()
    c.execute("SELECT filename FROM case_documents WHERE case_id = 'case-demo-01'")
    filenames = [row[0].lower() for row in c.fetchall()]
    conn.close()

    assert not any("cctv" in name or ".mp4" in name for name in filenames), \
        "CCTV video file must not exist in uploaded documents"


def test_06_empty_case_handling(setup_test_index):
    """Test 6: Querying an empty case must return insufficient material guidance, never fabricate."""
    pipeline = setup_test_index["pipeline"]

    result = pipeline.answer_case_question(
        question="Analyze this case and identify missing evidence.",
        case_id="case-empty-999"
    )

    assert result.confidence_status == "INSUFFICIENT_CASE_MATERIAL"
    assert "insufficient case material" in result.answer.lower()
    assert "no case documents have been uploaded" in result.answer.lower()
    assert len(result.case_sources) == 0


def test_07_source_provenance_page_accuracy(setup_test_index):
    """Test 7: Verify retrieved sources include exact page numbers and document names."""
    retriever = setup_test_index["retriever"]
    results = retriever.retrieve(
        query="Section 63 certificate for electronic records and WhatsApp chat",
        case_id="case-demo-01",
        top_k=3
    )

    assert len(results) > 0
    top = results[0]
    assert top.page_number in [1, 2]
    assert top.document_name in ["Seizure_Record.pdf", "FIR.pdf", "Witness_Statement_01.pdf"]
    assert top.chunk_id.startswith(f"{top.document_id}-p{top.page_number}-c")


def test_08_statutory_and_case_rag_separation(setup_test_index):
    """Test 8: Ensure Case RAG database does NOT contain statutory BNS/BNSS/BSA chunks."""
    index = setup_test_index["index"]

    # Direct query on Case RAG DB for statutory BNS sections
    conn = index._get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM case_chunks WHERE text LIKE '%Bharatiya Nyaya Sanhita, 2023%' AND document_name = 'BNS'")
    bns_count = c.fetchone()[0]
    conn.close()

    assert bns_count == 0, "Case RAG database must NOT contain statutory corpus"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
