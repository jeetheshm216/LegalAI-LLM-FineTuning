-- ============================================================================
-- Production PostgreSQL 16 + pgvector DDL for LegalAI RAG
-- Standard Target: Self-Hosted PostgreSQL with pgvector extension
-- Vector Dimension: 1024 (BAAI/bge-large-en-v1.5)
-- ============================================================================

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Enumerated Types
DO $$ BEGIN
    CREATE TYPE act_type_enum AS ENUM (
        'SUBSTANTIVE_CRIMINAL_LAW',
        'CRIMINAL_PROCEDURE',
        'EVIDENCE_LAW',
        'CIVIL_PROCEDURE',
        'COMMERCIAL_LAW',
        'CONSTITUTIONAL_LAW'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE authority_level_enum AS ENUM (
        'CONSTITUTIONAL',
        'PARLIAMENTARY_ACT',
        'APEX_PRECEDENT',
        'HIGH_COURT_PRECEDENT',
        'SUBORDINATE_RULES'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE verification_status_enum AS ENUM (
        'VERIFIED_OFFICIAL_GAZETTE',
        'VERIFIED_STATUTORY_CONCORDANCE',
        'UNVERIFIED',
        'PENDING_REVIEW'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 3. Ingestion Runs (Audit Trail)
CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'RUNNING',
    corpus_version VARCHAR(50) NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    vector_dimension INT NOT NULL,
    total_documents_ingested INT DEFAULT 0,
    total_sections_extracted INT DEFAULT 0,
    total_chunks_created INT DEFAULT 0,
    error_log TEXT
);

-- 4. Legal Sources (Authoritative Origin)
CREATE TABLE IF NOT EXISTS legal_sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    official_domain VARCHAR(255) NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    pdf_download_url TEXT,
    publication_authority VARCHAR(255) NOT NULL,
    acquisition_method VARCHAR(100) NOT NULL,
    sha256_hash CHAR(64) NOT NULL,
    retrieval_timestamp TIMESTAMPTZ NOT NULL,
    verification_status verification_status_enum NOT NULL DEFAULT 'VERIFIED_OFFICIAL_GAZETTE',
    notes TEXT
);

-- 5. Legal Documents (Enacted Acts / Codes)
CREATE TABLE IF NOT EXISTS legal_documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES legal_sources(source_id) ON DELETE RESTRICT,
    act_name VARCHAR(255) NOT NULL,
    act_number VARCHAR(100) NOT NULL,
    act_prefix VARCHAR(20) NOT NULL UNIQUE,
    act_type act_type_enum NOT NULL,
    enactment_date DATE NOT NULL,
    commencement_date DATE NOT NULL,
    commencement_authority TEXT NOT NULL,
    document_version VARCHAR(50) NOT NULL DEFAULT '1.0-ORIGINAL-ENACTMENT',
    jurisdiction VARCHAR(100) NOT NULL DEFAULT 'INDIA_CENTRAL',
    language VARCHAR(10) NOT NULL DEFAULT 'EN',
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    total_sections INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Legal Sections (Structural Statutory Unit)
CREATE TABLE IF NOT EXISTS legal_sections (
    section_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES legal_documents(document_id) ON DELETE CASCADE,
    act_prefix VARCHAR(20) NOT NULL,
    section_number VARCHAR(50) NOT NULL,
    section_title TEXT NOT NULL,
    chapter_id VARCHAR(50) NOT NULL,
    chapter_title TEXT NOT NULL,
    full_text TEXT NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    amendment_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_act_section UNIQUE (document_id, section_number)
);

-- 7. Legal Chunks (Fine-Grained Retrieval Unit)
CREATE TABLE IF NOT EXISTS legal_chunks (
    chunk_id VARCHAR(100) PRIMARY KEY,
    section_id UUID NOT NULL REFERENCES legal_sections(section_id) ON DELETE CASCADE,
    parent_section_id VARCHAR(100) NOT NULL,
    act_name VARCHAR(255) NOT NULL,
    act_number VARCHAR(100) NOT NULL,
    act_type act_type_enum NOT NULL,
    act_prefix VARCHAR(20) NOT NULL,
    section_number VARCHAR(50) NOT NULL,
    section_title TEXT NOT NULL,
    chapter VARCHAR(255) NOT NULL,
    chunk_index INT NOT NULL DEFAULT 0,
    total_chunks INT NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    raw_section_text TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL,
    publication_date DATE NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    authority_level authority_level_enum NOT NULL DEFAULT 'PARLIAMENTARY_ACT',
    content_hash CHAR(64) NOT NULL,
    embedding vector(1024),  -- Configurable: matches BAAI/bge-large-en-v1.5
    tsv_content tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(section_number, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(section_title, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'C')
    ) STORED
);

-- 8. Legal Concordance (Verified Predecessor-Successor Provisions)
CREATE TABLE IF NOT EXISTS legal_concordance (
    concordance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    legacy_act VARCHAR(255) NOT NULL,
    legacy_section VARCHAR(50) NOT NULL,
    modern_act VARCHAR(255) NOT NULL,
    modern_section VARCHAR(50) NOT NULL,
    mapping_type VARCHAR(100) NOT NULL,
    authority TEXT NOT NULL,
    verification_status verification_status_enum NOT NULL DEFAULT 'VERIFIED_STATUTORY_CONCORDANCE',
    notes TEXT,
    CONSTRAINT uq_concordance UNIQUE (legacy_act, legacy_section, modern_act, modern_section)
);

-- 9. Production Indexes
CREATE INDEX IF NOT EXISTS idx_chunks_act_prefix ON legal_chunks(act_prefix);
CREATE INDEX IF NOT EXISTS idx_chunks_sec_num ON legal_chunks(section_number);
CREATE INDEX IF NOT EXISTS idx_chunks_effective ON legal_chunks(effective_from, effective_to);
CREATE INDEX IF NOT EXISTS idx_chunks_is_current ON legal_chunks(is_current);

-- Lexical full-text GIN index
CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON legal_chunks USING GIN(tsv_content);

-- Dense vector HNSW index (Cosine distance)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw ON legal_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
