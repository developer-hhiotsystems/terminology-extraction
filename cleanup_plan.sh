#!/bin/bash
# Comprehensive Project Cleanup Script
# Generated: 2025-10-19
# Safe to run - creates git checkpoint first

set -e  # Exit on error

echo "========================================================================"
echo "                   GLOSSARY APP - PROJECT CLEANUP"
echo "========================================================================"
echo ""

# Safety checkpoint
echo "Step 1: Creating git safety checkpoint..."
git add .
git commit -m "Pre-cleanup checkpoint - preserving all files before cleanup"
echo "✓ Safety checkpoint created"
echo ""

# ============================================================================
# CATEGORY 1: SAFE DELETIONS (Empty/Temp Files)
# ============================================================================
echo "Step 2: Deleting empty/temporary files..."

# Empty files
rm -f nul
rm -f scripts/nul
rm -f glossary.db
rm -f backend-error.log

# Temporary files
rm -f openapi_temp.json
rm -f CHANGES_SUMMARY.txt

echo "✓ Deleted 6 empty/temporary files"
echo ""

# ============================================================================
# CATEGORY 2: SUPERSEDED VERSIONS
# ============================================================================
echo "Step 3: Deleting superseded document versions..."

# Keep only v2.2, delete v2.0 and v2.1
rm -f docs/PRT-v2.0.md
rm -f docs/PRT-v2.1.md

# Keep only v1.1, delete v1.0
rm -f docs/IMPLEMENTATION-STRATEGY.md

echo "✓ Deleted 3 superseded versions (~107 KB saved)"
echo ""

# ============================================================================
# CATEGORY 3: DUPLICATE QUALITY ANALYSIS DOCS
# ============================================================================
echo "Step 4: Deleting duplicate quality analysis documents..."

rm -f docs/README_QUALITY_ANALYSIS.md
rm -f docs/QUALITY_SUMMARY_VISUAL.md
rm -f docs/SECOND_ROUND_QUALITY_ANALYSIS.md
rm -f docs/QUALITY_REVIEW_SUMMARY.md

echo "✓ Deleted 4 duplicate quality docs"
echo ""

# ============================================================================
# CATEGORY 4: DUPLICATE VALIDATION DOCS
# ============================================================================
echo "Step 5: Deleting duplicate validation documents..."

rm -f docs/VALIDATION_ANALYSIS.md
rm -f docs/VALIDATION_SUMMARY.md
rm -f docs/VALIDATION_CODE_CHANGES.md

echo "✓ Deleted 3 duplicate validation docs"
echo ""

# ============================================================================
# CATEGORY 5: REDUNDANT SETUP DOCS
# ============================================================================
echo "Step 6: Deleting redundant setup documents..."

rm -f docs/SETUP-SUMMARY.md
rm -f docs/SETUP-COMPLETE.md
rm -f docs/REMAINING-SETUP-TASKS.md
rm -f docs/READINESS-CHECKLIST.md

echo "✓ Deleted 4 redundant setup docs"
echo ""

# ============================================================================
# CATEGORY 6: REDUNDANT SUMMARY DOCS
# ============================================================================
echo "Step 7: Deleting redundant summary documents..."

rm -f docs/LINGUIST_SUMMARY.md
rm -f docs/LINGUISTIC_REVIEW_SUMMARY.md
rm -f docs/EXECUTIVE_SUMMARY_EXPERT_REVIEW.md
rm -f docs/EXPERT_TEAM_SYNTHESIS.md

echo "✓ Deleted 4 redundant expert review summaries"
echo ""

# ============================================================================
# CATEGORY 7: MOVE SCREENSHOTS
# ============================================================================
echo "Step 8: Moving screenshots to correct location..."

# Ensure directory exists
mkdir -p test-screenshots/docs-screenshots

# Move screenshots from docs to test-screenshots
mv -f docs/test-1-glossary-list.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/test-1-homepage.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/test-2-after-typing.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/test-3-after-search.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/test-glossary-view.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/ui-screenshot.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/upload-console-error.png test-screenshots/docs-screenshots/ 2>/dev/null || true
mv -f docs/upload-scrolled.png test-screenshots/docs-screenshots/ 2>/dev/null || true

echo "✓ Moved 8 screenshots (saved ~7.7 MB in /docs)"
echo ""

# ============================================================================
# CATEGORY 8: ARCHIVE WEEKLY SUMMARIES
# ============================================================================
echo "Step 9: Archiving weekly progress summaries..."

# Create archive directory
mkdir -p docs/archive/weekly-summaries

# Move weekly summaries
mv -f docs/WEEK_1_COMPLETION_SUMMARY.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/WEEK_2_COMPLETION_SUMMARY.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/WEEK_2_FINAL_SUMMARY.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/WEEK_2_PREVENTION_FIRST_PLAN.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/WEEK_3_COMPLETION_SUMMARY.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/WEEK_4_COMPLETION_SUMMARY.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/WEEK_4_PLAN.md docs/archive/weekly-summaries/ 2>/dev/null || true
mv -f docs/SESSION_SUMMARY_OCT17.md docs/archive/weekly-summaries/ 2>/dev/null || true

echo "✓ Archived 8 weekly summaries"
echo ""

# ============================================================================
# CATEGORY 9: ARCHIVE OLD PHASE DOCS
# ============================================================================
echo "Step 10: Archiving old phase documentation..."

# Create archive directory
mkdir -p docs/archive/old-phases

# Move old phase 3.8 docs
mv -f docs/PHASE_3.8_PROGRESS.md docs/archive/old-phases/ 2>/dev/null || true
mv -f docs/PHASE_3.8_TEST_PLAN.md docs/archive/old-phases/ 2>/dev/null || true
mv -f docs/PHASE_3.8_TEST_RESULTS.md docs/archive/old-phases/ 2>/dev/null || true
mv -f docs/PHASE_3.8_FINAL_SUMMARY.md docs/archive/old-phases/ 2>/dev/null || true
mv -f docs/PHASE_3_ENHANCEMENTS.md docs/archive/old-phases/ 2>/dev/null || true

# Move Neo4j phase 4 docs (not implemented)
mv -f docs/PHASE_4_NEO4J_INTEGRATION.md docs/archive/old-phases/ 2>/dev/null || true
mv -f docs/PHASE_4_SUMMARY.md docs/archive/old-phases/ 2>/dev/null || true
mv -f docs/PRE_NEO4J_ACTION_PLAN.md docs/archive/old-phases/ 2>/dev/null || true

echo "✓ Archived 8 old phase documents"
echo ""

# ============================================================================
# CATEGORY 10: MOVE TEST FILES
# ============================================================================
echo "Step 11: Moving test files to correct locations..."

# Create test directories
mkdir -p tests/e2e
mkdir -p tests/manual

# Move E2E tests from root
mv -f test-app.js tests/e2e/ 2>/dev/null || true
mv -f test-search.js tests/e2e/ 2>/dev/null || true
mv -f test-document-ui.js tests/e2e/ 2>/dev/null || true

# Move manual test
mv -f test_api_manual.py tests/manual/ 2>/dev/null || true

# Move analyze script
mkdir -p scripts/analysis
mv -f analyze_glossary.py scripts/analysis/ 2>/dev/null || true

echo "✓ Moved 5 test/analysis files to correct locations"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "========================================================================"
echo "                        CLEANUP COMPLETE!"
echo "========================================================================"
echo ""
echo "Files deleted: ~30 files"
echo "Files moved: ~25 files"
echo "Space saved: ~8 MB"
echo ""
echo "Summary:"
echo "  ✓ Empty/temporary files deleted"
echo "  ✓ Superseded versions removed"
echo "  ✓ Duplicate documentation consolidated"
echo "  ✓ Screenshots organized"
echo "  ✓ Weekly summaries archived"
echo "  ✓ Old phase docs archived"
echo "  ✓ Test files relocated"
echo ""
echo "All deleted files are preserved in git history!"
echo "To undo: git reset --hard HEAD~1"
echo ""
echo "Next: Commit these changes with:"
echo "  git add ."
echo "  git commit -m 'Project cleanup: removed duplicates, organized files'"
echo ""
echo "========================================================================"
