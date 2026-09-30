"""Database schema definitions for General Indian Legal Knowledge."""

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- 1. Official Sources Table
CREATE TABLE IF NOT EXISTS indian_legal_sources (
    source_id TEXT PRIMARY KEY,
    authority TEXT NOT NULL,
    authority_level TEXT NOT NULL,
    domain TEXT NOT NULL,
    source_type TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'IN',
    active INTEGER NOT NULL DEFAULT 1,
    source_url TEXT NOT NULL UNIQUE,
    jurisdiction_level TEXT NOT NULL DEFAULT 'CENTRAL',
    access_method TEXT NOT NULL DEFAULT 'PUBLIC_OFFICIAL_PORTAL',
    license_or_terms TEXT NOT NULL,
    state TEXT,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED_OFFICIAL',
    notes TEXT
);

-- 2. Legal Documents Table
CREATE TABLE IF NOT EXISTS indian_legal_documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    short_title TEXT,
    document_type TEXT NOT NULL,
    jurisdiction_level TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    state TEXT,
    court TEXT,
    bench TEXT,
    judges TEXT,
    act_prefix TEXT,
    act_number TEXT,
    enactment_date TEXT,
    commencement_date TEXT,
    legal_domain TEXT NOT NULL DEFAULT 'General Indian Law',
    authority_tier TEXT NOT NULL,
    temporal_status TEXT NOT NULL,
    effective_from TEXT,
    effective_until TEXT,
    amended_by TEXT,
    repealed_by TEXT,
    struck_down_by TEXT,
    official_source_url TEXT NOT NULL,
    source_id TEXT REFERENCES indian_legal_sources(source_id),
    content_hash TEXT,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED_OFFICIAL',
    created_at TEXT NOT NULL
);

-- 3. Legal Chunks / Provisions (Statutory Sections, Articles, Order-Rules, Schedules)
CREATE TABLE IF NOT EXISTS indian_legal_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES indian_legal_documents(document_id),
    title TEXT NOT NULL,
    act_name TEXT NOT NULL,
    act_prefix TEXT NOT NULL,
    provision_type TEXT NOT NULL DEFAULT 'SECTION',
    section_or_article TEXT NOT NULL,
    provision_number TEXT NOT NULL,
    provision_title TEXT NOT NULL,
    chapter TEXT NOT NULL,
    content TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    document_type TEXT NOT NULL,
    jurisdiction_level TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    state TEXT,
    court TEXT,
    bench TEXT,
    citation TEXT,
    decision_date TEXT,
    legal_domain TEXT NOT NULL,
    authority_tier TEXT NOT NULL,
    temporal_status TEXT NOT NULL,
    effective_from TEXT,
    effective_until TEXT,
    transition_note TEXT,
    official_source_url TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    embedding_blob BLOB
);

-- 4. FTS5 Full-Text Search Table
CREATE VIRTUAL TABLE IF NOT EXISTS indian_legal_chunks_fts USING fts5(
    chunk_id UNINDEXED,
    title,
    act_name,
    act_prefix,
    provision_type,
    section_or_article,
    provision_number,
    provision_title,
    chapter,
    content,
    citation,
    court,
    state,
    tokenize='porter unicode61'
);

-- 5. Official Notifications Table
CREATE TABLE IF NOT EXISTS indian_legal_notifications (
    notification_id TEXT PRIMARY KEY,
    notification_number TEXT NOT NULL,
    date TEXT,
    issuing_authority TEXT NOT NULL,
    subject TEXT NOT NULL,
    source_url TEXT NOT NULL,
    effective_date TEXT,
    affected_act TEXT,
    affected_provision TEXT,
    document_id TEXT REFERENCES indian_legal_documents(document_id),
    content_hash TEXT,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED_OFFICIAL'
);

-- 6. Statutory Amendments Table
CREATE TABLE IF NOT EXISTS indian_legal_amendments (
    amendment_id TEXT PRIMARY KEY,
    act_id TEXT NOT NULL,
    act_name TEXT NOT NULL,
    amending_act_number TEXT NOT NULL,
    amending_act_year INTEGER NOT NULL,
    effective_date TEXT NOT NULL,
    sections_modified TEXT,
    source_url TEXT
);

-- Indexes for rapid filtered querying and strict namespace separation
CREATE INDEX IF NOT EXISTS idx_chunks_hash ON indian_legal_chunks(content_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_prefix ON indian_legal_chunks(act_prefix);
CREATE INDEX IF NOT EXISTS idx_chunks_prov_num ON indian_legal_chunks(provision_number);
CREATE INDEX IF NOT EXISTS idx_chunks_prov_type ON indian_legal_chunks(provision_type);
CREATE INDEX IF NOT EXISTS idx_chunks_exact_lookup ON indian_legal_chunks(act_prefix, provision_type, provision_number);
CREATE INDEX IF NOT EXISTS idx_chunks_jurisdiction ON indian_legal_chunks(jurisdiction_level);
CREATE INDEX IF NOT EXISTS idx_chunks_state ON indian_legal_chunks(state);
CREATE INDEX IF NOT EXISTS idx_chunks_court ON indian_legal_chunks(court);
CREATE INDEX IF NOT EXISTS idx_chunks_authority ON indian_legal_chunks(authority_tier);
CREATE INDEX IF NOT EXISTS idx_chunks_temporal ON indian_legal_chunks(temporal_status);
CREATE INDEX IF NOT EXISTS idx_chunks_domain ON indian_legal_chunks(legal_domain);
"""
