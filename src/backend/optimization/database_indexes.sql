-- Database Index Optimization
-- Optimizes query performance with strategic indexes

-- ============================================================================
-- Glossary Entries Indexes
-- ============================================================================

-- Index on term (most common search)
CREATE INDEX IF NOT EXISTS idx_glossary_entries_term
ON glossary_entries(term COLLATE NOCASE);

-- Index on language (filter by language)
CREATE INDEX IF NOT EXISTS idx_glossary_entries_language
ON glossary_entries(language);

-- Index on source_document (group by document)
CREATE INDEX IF NOT EXISTS idx_glossary_entries_source_document
ON glossary_entries(source_document);

-- Index on validation_status (filter validated/pending)
CREATE INDEX IF NOT EXISTS idx_glossary_entries_validation_status
ON glossary_entries(validation_status);

-- Composite index for common queries (language + validation)
CREATE INDEX IF NOT EXISTS idx_glossary_entries_language_validation
ON glossary_entries(language, validation_status);

-- Index on created_at (sort by date)
CREATE INDEX IF NOT EXISTS idx_glossary_entries_created_at
ON glossary_entries(created_at DESC);

-- ============================================================================
-- FTS5 Optimization
-- ============================================================================

-- FTS5 already has internal indexes
-- But we can optimize the trigger for faster updates

-- Drop existing trigger
DROP TRIGGER IF EXISTS glossary_entries_ai;
DROP TRIGGER IF EXISTS glossary_entries_ad;
DROP TRIGGER IF EXISTS glossary_entries_au;

-- Recreated optimized triggers
CREATE TRIGGER glossary_entries_ai AFTER INSERT ON glossary_entries BEGIN
  INSERT INTO glossary_entries_fts(rowid, term, definitions_text, context, language, domain_tags)
  VALUES (
    new.id,
    new.term,
    COALESCE(json_extract(new.definitions, '$[0].definition_text'), ''),
    COALESCE(new.context, ''),
    new.language,
    COALESCE(json_extract(new.domain_tags, '$'), '')
  );
END;

CREATE TRIGGER glossary_entries_ad AFTER DELETE ON glossary_entries BEGIN
  DELETE FROM glossary_entries_fts WHERE rowid = old.id;
END;

CREATE TRIGGER glossary_entries_au AFTER UPDATE ON glossary_entries BEGIN
  DELETE FROM glossary_entries_fts WHERE rowid = old.id;
  INSERT INTO glossary_entries_fts(rowid, term, definitions_text, context, language, domain_tags)
  VALUES (
    new.id,
    new.term,
    COALESCE(json_extract(new.definitions, '$[0].definition_text'), ''),
    COALESCE(new.context, ''),
    new.language,
    COALESCE(json_extract(new.domain_tags, '$'), '')
  );
END;

-- ============================================================================
-- Relationships Indexes
-- ============================================================================

-- Index on source_term_id (most common lookup)
CREATE INDEX IF NOT EXISTS idx_relationships_source_term
ON term_relationships(source_term_id);

-- Index on target_term_id (reverse lookup)
CREATE INDEX IF NOT EXISTS idx_relationships_target_term
ON term_relationships(target_term_id);

-- Index on relation_type (filter by type)
CREATE INDEX IF NOT EXISTS idx_relationships_relation_type
ON term_relationships(relation_type);

-- Composite index for bidirectional lookups
CREATE INDEX IF NOT EXISTS idx_relationships_source_target
ON term_relationships(source_term_id, target_term_id);

-- Index on confidence (filter high-confidence relationships)
CREATE INDEX IF NOT EXISTS idx_relationships_confidence
ON term_relationships(confidence DESC);

-- Index on validated status
CREATE INDEX IF NOT EXISTS idx_relationships_validated
ON term_relationships(validated);

-- Composite index for common filtered queries
CREATE INDEX IF NOT EXISTS idx_relationships_type_confidence
ON term_relationships(relation_type, confidence DESC);

-- ============================================================================
-- Query Optimization Hints
-- ============================================================================

-- Analyze tables to update statistics
ANALYZE glossary_entries;
ANALYZE glossary_entries_fts;
ANALYZE term_relationships;

-- Vacuum to reclaim space and optimize
-- Note: Run this periodically, not on every startup
-- VACUUM;

-- ============================================================================
-- Performance Testing Queries
-- ============================================================================

-- Test term lookup (should use idx_glossary_entries_term)
-- EXPLAIN QUERY PLAN SELECT * FROM glossary_entries WHERE term = 'temperature';

-- Test language filter (should use idx_glossary_entries_language_validation)
-- EXPLAIN QUERY PLAN SELECT * FROM glossary_entries WHERE language = 'EN' AND validation_status = 'validated';

-- Test FTS5 search (uses internal FTS index)
-- EXPLAIN QUERY PLAN SELECT * FROM glossary_entries_fts WHERE glossary_entries_fts MATCH 'temperature';

-- Test relationship lookup (should use idx_relationships_source_term)
-- EXPLAIN QUERY PLAN SELECT * FROM term_relationships WHERE source_term_id = 1;

-- ============================================================================
-- Index Maintenance
-- ============================================================================

-- Check index usage
-- SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND tbl_name LIKE '%glossary%';

-- Drop unused indexes (if any are identified)
-- DROP INDEX IF EXISTS idx_unused_index;

-- ============================================================================
-- Recommendations
-- ============================================================================

/*
PERIODIC MAINTENANCE (Weekly/Monthly):

1. ANALYZE - Update query planner statistics
   sqlite3 glossary.db "ANALYZE;"

2. VACUUM - Reclaim space and defragment
   sqlite3 glossary.db "VACUUM;"

3. REINDEX - Rebuild indexes if corrupted
   sqlite3 glossary.db "REINDEX;"

4. Check database integrity
   sqlite3 glossary.db "PRAGMA integrity_check;"

5. Check index usage with query plans
   EXPLAIN QUERY PLAN <your-query>;

MONITORING:

- Monitor slow queries (> 100ms)
- Track index hit rates
- Watch for table scans (SCAN TABLE)
- Profile frequently executed queries

OPTIMIZATION OPPORTUNITIES:

- Add indexes for new query patterns
- Remove unused indexes (overhead on writes)
- Consider covering indexes for frequent queries
- Partition large tables if needed (rare for SQLite)
*/
