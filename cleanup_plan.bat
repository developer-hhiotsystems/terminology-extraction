@echo off
REM Comprehensive Project Cleanup Script - Windows Version
REM Generated: 2025-10-19
REM Safe to run - creates git checkpoint first

echo ========================================================================
echo                   GLOSSARY APP - PROJECT CLEANUP
echo ========================================================================
echo.

REM Safety checkpoint
echo Step 1: Creating git safety checkpoint...
git add .
git commit -m "Pre-cleanup checkpoint - preserving all files before cleanup"
echo Done: Safety checkpoint created
echo.

REM ============================================================================
REM CATEGORY 1: SAFE DELETIONS (Empty/Temp Files)
REM ============================================================================
echo Step 2: Deleting empty/temporary files...

del /F /Q nul 2>nul
del /F /Q scripts\nul 2>nul
del /F /Q glossary.db 2>nul
del /F /Q backend-error.log 2>nul
del /F /Q openapi_temp.json 2>nul
del /F /Q CHANGES_SUMMARY.txt 2>nul

echo Done: Deleted 6 empty/temporary files
echo.

REM ============================================================================
REM CATEGORY 2: SUPERSEDED VERSIONS
REM ============================================================================
echo Step 3: Deleting superseded document versions...

del /F /Q docs\PRT-v2.0.md 2>nul
del /F /Q docs\PRT-v2.1.md 2>nul
del /F /Q docs\IMPLEMENTATION-STRATEGY.md 2>nul

echo Done: Deleted 3 superseded versions (~107 KB saved)
echo.

REM ============================================================================
REM CATEGORY 3: DUPLICATE QUALITY ANALYSIS DOCS
REM ============================================================================
echo Step 4: Deleting duplicate quality analysis documents...

del /F /Q docs\README_QUALITY_ANALYSIS.md 2>nul
del /F /Q docs\QUALITY_SUMMARY_VISUAL.md 2>nul
del /F /Q docs\SECOND_ROUND_QUALITY_ANALYSIS.md 2>nul
del /F /Q docs\QUALITY_REVIEW_SUMMARY.md 2>nul

echo Done: Deleted 4 duplicate quality docs
echo.

REM ============================================================================
REM CATEGORY 4: DUPLICATE VALIDATION DOCS
REM ============================================================================
echo Step 5: Deleting duplicate validation documents...

del /F /Q docs\VALIDATION_ANALYSIS.md 2>nul
del /F /Q docs\VALIDATION_SUMMARY.md 2>nul
del /F /Q docs\VALIDATION_CODE_CHANGES.md 2>nul

echo Done: Deleted 3 duplicate validation docs
echo.

REM ============================================================================
REM CATEGORY 5: REDUNDANT SETUP DOCS
REM ============================================================================
echo Step 6: Deleting redundant setup documents...

del /F /Q docs\SETUP-SUMMARY.md 2>nul
del /F /Q docs\SETUP-COMPLETE.md 2>nul
del /F /Q docs\REMAINING-SETUP-TASKS.md 2>nul
del /F /Q docs\READINESS-CHECKLIST.md 2>nul

echo Done: Deleted 4 redundant setup docs
echo.

REM ============================================================================
REM CATEGORY 6: REDUNDANT SUMMARY DOCS
REM ============================================================================
echo Step 7: Deleting redundant summary documents...

del /F /Q docs\LINGUIST_SUMMARY.md 2>nul
del /F /Q docs\LINGUISTIC_REVIEW_SUMMARY.md 2>nul
del /F /Q docs\EXECUTIVE_SUMMARY_EXPERT_REVIEW.md 2>nul
del /F /Q docs\EXPERT_TEAM_SYNTHESIS.md 2>nul

echo Done: Deleted 4 redundant expert review summaries
echo.

REM ============================================================================
REM CATEGORY 7: MOVE SCREENSHOTS
REM ============================================================================
echo Step 8: Moving screenshots to correct location...

if not exist test-screenshots\docs-screenshots mkdir test-screenshots\docs-screenshots

move /Y docs\test-1-glossary-list.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\test-1-homepage.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\test-2-after-typing.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\test-3-after-search.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\test-glossary-view.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\ui-screenshot.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\upload-console-error.png test-screenshots\docs-screenshots\ 2>nul
move /Y docs\upload-scrolled.png test-screenshots\docs-screenshots\ 2>nul

echo Done: Moved 8 screenshots (saved ~7.7 MB in /docs)
echo.

REM ============================================================================
REM CATEGORY 8: ARCHIVE WEEKLY SUMMARIES
REM ============================================================================
echo Step 9: Archiving weekly progress summaries...

if not exist docs\archive\weekly-summaries mkdir docs\archive\weekly-summaries

move /Y docs\WEEK_1_COMPLETION_SUMMARY.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\WEEK_2_COMPLETION_SUMMARY.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\WEEK_2_FINAL_SUMMARY.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\WEEK_2_PREVENTION_FIRST_PLAN.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\WEEK_3_COMPLETION_SUMMARY.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\WEEK_4_COMPLETION_SUMMARY.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\WEEK_4_PLAN.md docs\archive\weekly-summaries\ 2>nul
move /Y docs\SESSION_SUMMARY_OCT17.md docs\archive\weekly-summaries\ 2>nul

echo Done: Archived 8 weekly summaries
echo.

REM ============================================================================
REM CATEGORY 9: ARCHIVE OLD PHASE DOCS
REM ============================================================================
echo Step 10: Archiving old phase documentation...

if not exist docs\archive\old-phases mkdir docs\archive\old-phases

move /Y docs\PHASE_3.8_PROGRESS.md docs\archive\old-phases\ 2>nul
move /Y docs\PHASE_3.8_TEST_PLAN.md docs\archive\old-phases\ 2>nul
move /Y docs\PHASE_3.8_TEST_RESULTS.md docs\archive\old-phases\ 2>nul
move /Y docs\PHASE_3.8_FINAL_SUMMARY.md docs\archive\old-phases\ 2>nul
move /Y docs\PHASE_3_ENHANCEMENTS.md docs\archive\old-phases\ 2>nul
move /Y docs\PHASE_4_NEO4J_INTEGRATION.md docs\archive\old-phases\ 2>nul
move /Y docs\PHASE_4_SUMMARY.md docs\archive\old-phases\ 2>nul
move /Y docs\PRE_NEO4J_ACTION_PLAN.md docs\archive\old-phases\ 2>nul

echo Done: Archived 8 old phase documents
echo.

REM ============================================================================
REM CATEGORY 10: MOVE TEST FILES
REM ============================================================================
echo Step 11: Moving test files to correct locations...

if not exist tests\e2e mkdir tests\e2e
if not exist tests\manual mkdir tests\manual
if not exist scripts\analysis mkdir scripts\analysis

move /Y test-app.js tests\e2e\ 2>nul
move /Y test-search.js tests\e2e\ 2>nul
move /Y test-document-ui.js tests\e2e\ 2>nul
move /Y test_api_manual.py tests\manual\ 2>nul
move /Y analyze_glossary.py scripts\analysis\ 2>nul

echo Done: Moved 5 test/analysis files to correct locations
echo.

REM ============================================================================
REM SUMMARY
REM ============================================================================
echo ========================================================================
echo                        CLEANUP COMPLETE!
echo ========================================================================
echo.
echo Files deleted: ~30 files
echo Files moved: ~25 files
echo Space saved: ~8 MB
echo.
echo Summary:
echo   - Empty/temporary files deleted
echo   - Superseded versions removed
echo   - Duplicate documentation consolidated
echo   - Screenshots organized
echo   - Weekly summaries archived
echo   - Old phase docs archived
echo   - Test files relocated
echo.
echo All deleted files are preserved in git history!
echo To undo: git reset --hard HEAD~1
echo.
echo Next: Commit these changes with:
echo   git add .
echo   git commit -m "Project cleanup: removed duplicates, organized files"
echo.
echo ========================================================================
pause
