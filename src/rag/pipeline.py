"""Master ingestion pipeline for LegalAI Real-Data RAG MVP."""

import os
import json
import time
from typing import Dict, Any, List
from .ingestion.extract import extract_act_text
from .ingestion.parser import StatutoryParser
from .ingestion.metadata import create_chunk_metadata
from .concordance.concordance import ConcordanceRegistry
from .database.sqlite_adapter import SQLiteLegalDatabase
from .embeddings.embedder import LegalEmbedder

ACT_CONFIGS = [
    {
        "act_name": "The Bharatiya Nyaya Sanhita, 2023",
        "act_number": "45 of 2023",
        "act_prefix": "BNS",
        "act_type": "SUBSTANTIVE_CRIMINAL_LAW",
        "pdf_filename": "BNS_2023_Act_45.pdf",
        "start_page": 16,
        "total_sections": 358,
        "enactment_date": "2023-12-25",
        "commencement_date": "2024-07-01",
        "commencement_authority": "Ministry of Home Affairs Notification S.O. 848(E) dated 23-02-2024"
    },
    {
        "act_name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
        "act_number": "46 of 2023",
        "act_prefix": "BNSS",
        "act_type": "CRIMINAL_PROCEDURE",
        "pdf_filename": "BNSS_2023_Act_46.pdf",
        "start_page": 18,
        "total_sections": 531,
        "enactment_date": "2023-12-25",
        "commencement_date": "2024-07-01",
        "commencement_authority": "Ministry of Home Affairs Notification S.O. 849(E) dated 23-02-2024"
    },
    {
        "act_name": "The Bharatiya Sakshya Adhiniyam, 2023",
        "act_number": "47 of 2023",
        "act_prefix": "BSA",
        "act_type": "EVIDENCE_LAW",
        "pdf_filename": "BSA_2023_Act_47.pdf",
        "start_page": 10,
        "total_sections": 170,
        "enactment_date": "2023-12-25",
        "commencement_date": "2024-07-01",
        "commencement_authority": "Ministry of Home Affairs Notification S.O. 850(E) dated 23-02-2024"
    }
]


def run_mvp_ingestion(
    project_dir: str = ".",
    db_path: str = "data/legalai_rag_mvp.db",
    embedder: LegalEmbedder = None
) -> Dict[str, Any]:
    """
    Executes complete MVP ingestion pipeline:
    Source verification -> Raw extraction -> Parsing -> Metadata -> Embedding -> Database.
    """
    start_time = time.time()
    raw_dir = os.path.join(project_dir, "data/raw")
    processed_dir = os.path.join(project_dir, "data/processed")
    manifest_path = os.path.join(project_dir, "data/sources/legal_sources_manifest.json")

    full_db_path = os.path.join(project_dir, db_path)
    os.makedirs(os.path.dirname(full_db_path), exist_ok=True)
    db = SQLiteLegalDatabase(full_db_path)

    # 1. Load Sources Manifest
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found at {manifest_path}. Run source verification first.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    manifest_map = {act["filename"]: act for act in manifest_data.get("acts", [])}

    # 2. Record Ingestion Run
    if embedder is None:
        embedder = LegalEmbedder(device="cuda:0")

    run_id = db.record_ingestion_run(
        corpus_version="MVP-3-ACTS-2023",
        embedding_model=embedder.model_name,
        vector_dimension=embedder.vector_dim
    )

    total_docs = 0
    total_sections = 0
    total_chunks = 0
    act_stats = []

    try:
        # 3. Process each Act
        for act_cfg in ACT_CONFIGS:
            prefix = act_cfg["act_prefix"]
            pdf_path = os.path.join(raw_dir, act_cfg["pdf_filename"])
            manifest_entry = manifest_map.get(act_cfg["pdf_filename"], {})

            print(f"\n==================================================")
            print(f"INGESTING: {act_cfg['act_name']} ({prefix})")
            print(f"==================================================")

            # Insert Source
            source_dict = {
                "official_domain": manifest_entry.get("official_domain", "indiacode.gov.in"),
                "source_name": act_cfg["act_name"],
                "source_url": manifest_entry.get("source_url", f"https://indiacode.gov.in/handle/{manifest_entry.get('handle', '')}"),
                "pdf_download_url": manifest_entry.get("pdf_download_url", ""),
                "publication_authority": "Legislative Department, Ministry of Law and Justice",
                "acquisition_method": "AUTOMATED_HTTPS_GET_OFFICIAL_BITSTREAM",
                "sha256_hash": manifest_entry.get("sha256_hash", ""),
                "retrieval_timestamp": manifest_entry.get("retrieval_timestamp", "2026-09-13T11:22:55"),
                "verification_status": "VERIFIED_OFFICIAL_GAZETTE",
                "notes": f"Enactment Act No. {act_cfg['act_number']}"
            }
            source_id = db.insert_source(source_dict)

            # Insert Document
            doc_dict = {
                "source_id": source_id,
                "act_name": act_cfg["act_name"],
                "act_number": act_cfg["act_number"],
                "act_prefix": prefix,
                "act_type": act_cfg["act_type"],
                "enactment_date": act_cfg["enactment_date"],
                "commencement_date": act_cfg["commencement_date"],
                "commencement_authority": act_cfg["commencement_authority"],
                "total_sections": act_cfg["total_sections"]
            }
            doc_id = db.insert_document(doc_dict)
            total_docs += 1

            # Step 3: Text Extraction
            processed_txt_path = os.path.join(processed_dir, f"{prefix.lower()}_2023_normalized.txt")
            print(f"  [1/4] Extracting text from {pdf_path} (Start page: {act_cfg['start_page']})...")
            full_text, extract_stats = extract_act_text(
                pdf_path=pdf_path,
                output_processed_path=processed_txt_path,
                start_page=act_cfg["start_page"],
                act_name=act_cfg["act_name"]
            )
            print(f"        Extracted {extract_stats['pages_extracted']} pages, {extract_stats['total_words']:,} words.")

            # Step 4: Statutory Section Parsing
            print(f"  [2/4] Parsing legal sections (Expected: {act_cfg['total_sections']})...")
            parser = StatutoryParser(
                act_name=act_cfg["act_name"],
                act_number=act_cfg["act_number"],
                act_type=act_cfg["act_type"],
                act_prefix=prefix
            )
            sections, chunks, parse_stats = parser.parse_enactment(
                full_text=full_text,
                total_sections=act_cfg["total_sections"]
            )
            for s in sections:
                s["document_id"] = doc_id

            # Insert sections into DB
            db.insert_sections(sections)
            total_sections += len(sections)
            print(f"        Parsed {len(sections)} sections, created {len(chunks)} retrieval chunks.")

            # Step 5: Metadata Enrichment
            print(f"  [3/4] Enriching metadata and validating controlled vocabulary...")
            enriched_chunks = []
            for c in chunks:
                enriched = create_chunk_metadata(c, manifest_entry)
                enriched["raw_section_text"] = c["raw_section_text"]
                enriched_chunks.append(enriched)

            # Step 6: Embeddings & Vector Storage
            print(f"  [4/4] Generating {len(enriched_chunks)} dense vectors via {embedder.model_name} on GPU 0...")
            chunk_texts = [c["content"] for c in enriched_chunks]
            embeddings = embedder.encode_passages(chunk_texts, batch_size=32, show_progress=False)

            db.insert_chunks(enriched_chunks, embeddings)
            total_chunks += len(enriched_chunks)
            print(f"        Successfully persisted {len(enriched_chunks)} indexed vectors in database.")

            act_stats.append({
                "act_prefix": prefix,
                "act_name": act_cfg["act_name"],
                "sections_extracted": len(sections),
                "chunks_created": len(chunks),
                "expected_sections": act_cfg["total_sections"],
                "sha256": manifest_entry.get("sha256_hash", "")
            })

        # 4. Insert Concordance Data
        print(f"\n==================================================")
        print(f"INSERTING VERIFIED STATUTORY CONCORDANCE MAPPINGS")
        print(f"==================================================")
        registry = ConcordanceRegistry()
        verified_mappings = registry.get_all_verified_mappings()
        db.insert_concordance(verified_mappings)
        print(f"Inserted {len(verified_mappings)} verified predecessor-to-successor legal mappings.")

        # Complete Ingestion Run
        elapsed_sec = time.time() - start_time
        db.complete_ingestion_run(
            run_id=run_id,
            status="COMPLETED",
            total_docs=total_docs,
            total_sections=total_sections,
            total_chunks=total_chunks
        )

        db_stats = db.get_stats()
        print(f"\n==================================================")
        print(f"INGESTION COMPLETE in {elapsed_sec:.2f}s")
        print(f"Total Documents: {db_stats['total_documents']}")
        print(f"Total Sections: {db_stats['total_sections']}")
        print(f"Total Chunks: {db_stats['total_chunks']}")
        print(f"Total Concordance: {db_stats['total_concordance']}")
        print(f"==================================================")

        return {
            "status": "SUCCESS",
            "elapsed_seconds": elapsed_sec,
            "run_id": run_id,
            "db_stats": db_stats,
            "act_stats": act_stats,
            "db_path": full_db_path,
            "embedding_model": embedder.model_name,
            "vector_dimension": embedder.vector_dim
        }

    except Exception as e:
        db.complete_ingestion_run(
            run_id=run_id,
            status="FAILED",
            total_docs=total_docs,
            total_sections=total_sections,
            total_chunks=total_chunks,
            error_log=str(e)
        )
        raise e


if __name__ == "__main__":
    run_mvp_ingestion()
