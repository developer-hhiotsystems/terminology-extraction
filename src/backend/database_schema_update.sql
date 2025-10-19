-- Database Schema Update for Term Relationships
-- Add this table to support Phase C: Relationship Extraction

CREATE TABLE IF NOT EXISTS term_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Source and target terms
    source_term_id INTEGER NOT NULL,
    target_term_id INTEGER NOT NULL,

    -- Relationship type
    relation_type VARCHAR(50) NOT NULL,
    -- Values: uses, measures, part_of, produces, affects, requires, controls, defines, related_to

    -- Confidence and evidence
    confidence REAL NOT NULL DEFAULT 0.5,
    evidence TEXT,
    context TEXT,

    -- Metadata
    extraction_method VARCHAR(50),
    -- Values: dependency_parsing, pattern_matching, manual, imported

    validated VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- Values: pending, validated, rejected

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Foreign keys
    FOREIGN KEY (source_term_id) REFERENCES glossary_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (target_term_id) REFERENCES glossary_entries(id) ON DELETE CASCADE,

    -- Constraints
    CONSTRAINT unique_relationship UNIQUE (source_term_id, target_term_id, relation_type),
    CONSTRAINT different_terms CHECK (source_term_id != target_term_id),
    CONSTRAINT valid_confidence CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_relationships_source ON term_relationships(source_term_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON term_relationships(target_term_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON term_relationships(relation_type);
CREATE INDEX IF NOT EXISTS idx_relationships_confidence ON term_relationships(confidence);
CREATE INDEX IF NOT EXISTS idx_relationships_validated ON term_relationships(validated);
CREATE INDEX IF NOT EXISTS idx_relationships_source_target ON term_relationships(source_term_id, target_term_id);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_relationships_timestamp
AFTER UPDATE ON term_relationships
BEGIN
    UPDATE term_relationships
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Sample queries for testing

-- Get all relationships for a term (outgoing)
-- SELECT * FROM term_relationships WHERE source_term_id = ?;

-- Get all relationships for a term (incoming)
-- SELECT * FROM term_relationships WHERE target_term_id = ?;

-- Get all relationships of a specific type
-- SELECT * FROM term_relationships WHERE relation_type = 'uses';

-- Get high-confidence relationships
-- SELECT * FROM term_relationships WHERE confidence >= 0.7;

-- Get relationship graph data (for visualization)
-- SELECT
--     r.id,
--     r.source_term_id,
--     s.term as source_term,
--     r.target_term_id,
--     t.term as target_term,
--     r.relation_type,
--     r.confidence
-- FROM term_relationships r
-- JOIN glossary_entries s ON r.source_term_id = s.id
-- JOIN glossary_entries t ON r.target_term_id = t.id
-- WHERE r.validated != 'rejected'
-- ORDER BY r.confidence DESC;
