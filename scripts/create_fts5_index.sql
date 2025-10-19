-- ============================================================================
-- SQLite FTS5 Full-Text Search Index for Glossary Application
-- ============================================================================
-- Purpose: Create FTS5 virtual table and automatic synchronization triggers
-- Created: 2025-10-19
-- Database: SQLite 3.9.0+ (FTS5 support required)
--
-- FTS5 provides:
-- - BM25 ranking algorithm for relevance scoring
-- - Porter stemming for English term normalization
-- - Unicode support with diacritic removal
-- - Phrase search, wildcards, Boolean operators
-- - 10-100x faster than LIKE queries
-- ============================================================================

-- ============================================================================
-- 1. CREATE FTS5 VIRTUAL TABLE
-- ============================================================================

-- Drop existing FTS5 table if it exists (for clean re-creation)
DROP TABLE IF EXISTS glossary_fts;

-- Create FTS5 virtual table with external content storage
-- Using 'content' option to link to existing glossary_entries table
CREATE VIRTUAL TABLE glossary_fts USING fts5(
    -- Searchable columns (indexed)
    term,                    -- The terminology term (e.g., "temperature control")
    definition_text,         -- Extracted definition text from JSON definitions array

    -- Non-searchable columns (for filtering only - UNINDEXED)
    language UNINDEXED,      -- Language code: 'en' or 'de'
    domain_tags UNINDEXED,   -- JSON array of domain tags for filtering
    source UNINDEXED,        -- Source: 'internal', 'NAMUR', 'DIN', etc.

    -- External content configuration
    content='glossary_entries',  -- Link to existing table
    content_rowid='id',          -- Use glossary_entries.id as rowid

    -- Tokenizer configuration
    -- porter: Porter stemming algorithm for English (running → run, controlled → control)
    -- unicode61: Unicode support with normalization
    -- remove_diacritics 2: Remove diacritics from text (café → cafe)
    tokenize='porter unicode61 remove_diacritics 2'
);

-- ============================================================================
-- 2. CREATE AUTOMATIC SYNCHRONIZATION TRIGGERS
-- ============================================================================
-- These triggers ensure FTS5 index stays in sync with glossary_entries table
-- Automatically fires on INSERT, UPDATE, DELETE operations
-- ============================================================================

-- ----------------------------------------------------------------------------
-- INSERT Trigger: Add new entries to FTS5 index
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS glossary_fts_insert;

CREATE TRIGGER glossary_fts_insert AFTER INSERT ON glossary_entries BEGIN
    -- Insert into FTS5 index
    -- Extract definition text from JSON definitions array
    INSERT INTO glossary_fts(
        rowid,
        term,
        definition_text,
        language,
        domain_tags,
        source
    )
    VALUES (
        new.id,
        new.term,
        -- Extract all definition texts from JSON array and concatenate with newlines
        -- JSON structure: [{"text": "definition 1", ...}, {"text": "definition 2", ...}]
        (
            SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
            FROM json_each(new.definitions)
            WHERE json_extract(value, '$.text') IS NOT NULL
        ),
        new.language,
        -- Convert domain_tags JSON array to comma-separated string for filtering
        COALESCE(
            (
                SELECT GROUP_CONCAT(value, ',')
                FROM json_each(new.domain_tags)
            ),
            ''
        ),
        new.source
    );
END;

-- ----------------------------------------------------------------------------
-- UPDATE Trigger: Update existing entries in FTS5 index
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS glossary_fts_update;

CREATE TRIGGER glossary_fts_update AFTER UPDATE ON glossary_entries BEGIN
    -- Delete old version from FTS5 index
    DELETE FROM glossary_fts WHERE rowid = old.id;

    -- Insert updated version into FTS5 index
    INSERT INTO glossary_fts(
        rowid,
        term,
        definition_text,
        language,
        domain_tags,
        source
    )
    VALUES (
        new.id,
        new.term,
        -- Extract all definition texts from JSON array
        (
            SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
            FROM json_each(new.definitions)
            WHERE json_extract(value, '$.text') IS NOT NULL
        ),
        new.language,
        -- Convert domain_tags to comma-separated string
        COALESCE(
            (
                SELECT GROUP_CONCAT(value, ',')
                FROM json_each(new.domain_tags)
            ),
            ''
        ),
        new.source
    );
END;

-- ----------------------------------------------------------------------------
-- DELETE Trigger: Remove deleted entries from FTS5 index
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS glossary_fts_delete;

CREATE TRIGGER glossary_fts_delete AFTER DELETE ON glossary_entries BEGIN
    -- Remove from FTS5 index
    DELETE FROM glossary_fts WHERE rowid = old.id;
END;

-- ============================================================================
-- 3. INITIAL POPULATION (run separately via Python script)
-- ============================================================================
-- This query populates FTS5 with existing glossary_entries data
-- NOTE: This is executed by the Python initialization script, not here
-- Kept as reference for manual population if needed
-- ============================================================================

/*
-- Populate FTS5 index with existing data
INSERT INTO glossary_fts(
    rowid,
    term,
    definition_text,
    language,
    domain_tags,
    source
)
SELECT
    ge.id,
    ge.term,
    -- Extract all definition texts from JSON array
    (
        SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
        FROM json_each(ge.definitions)
        WHERE json_extract(value, '$.text') IS NOT NULL
    ) AS definition_text,
    ge.language,
    -- Convert domain_tags to comma-separated string
    COALESCE(
        (
            SELECT GROUP_CONCAT(value, ',')
            FROM json_each(ge.domain_tags)
        ),
        ''
    ) AS domain_tags,
    ge.source
FROM glossary_entries ge;
*/

-- ============================================================================
-- 4. VERIFICATION QUERIES (for testing)
-- ============================================================================

-- Check FTS5 table structure
-- SELECT * FROM pragma_table_info('glossary_fts');

-- Count entries in FTS5 index
-- SELECT COUNT(*) FROM glossary_fts;

-- Test basic search
-- SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temperature' LIMIT 10;

-- Test search with BM25 ranking
-- SELECT
--     ge.*,
--     bm25(glossary_fts) AS relevance_score
-- FROM glossary_fts fts
-- JOIN glossary_entries ge ON fts.rowid = ge.id
-- WHERE glossary_fts MATCH 'control'
-- ORDER BY relevance_score
-- LIMIT 10;

-- ============================================================================
-- 5. PERFORMANCE INDEXES (already handled by FTS5)
-- ============================================================================
-- FTS5 automatically creates inverted indexes for searchable columns
-- No additional indexes needed for full-text search performance
-- ============================================================================

-- Schema creation complete!
-- Next steps:
-- 1. Run Python script to populate FTS5 with existing data
-- 2. Implement search API with BM25 ranking
-- 3. Add advanced search features (phrase search, wildcards, filters)
-- 4. Benchmark performance vs LIKE queries
