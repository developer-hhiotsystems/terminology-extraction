# Validation Configuration Quick Reference

## Current vs Recommended

| Parameter | Current | Recommended | Impact |
|-----------|---------|-------------|--------|
| **min_term_length** | 3 | 4 | Filters "Ing", "Res" fragments |
| **max_term_length** | 100 | 80 | Prevents overly long phrases |
| **min_frequency** | 1 | 2 | Requires 2+ occurrences |
| **max_symbol_ratio** | 0.3 | 0.25 | Stricter symbol filtering |
| **min_acronym_length** | 2 | 3 | Filters "1 K", "0 E" |

**Expected Results:**
- Terms extracted: 4,511 → ~3,200-3,800 (15-25% reduction)
- Precision: ~70% → 85-90% (+15-20%)
- Fragments filtered: YES (Ing, Tion, Res, Tech)
- Stop words reduced: 30.5% → <10%

---

## Code Changes (Copy-Paste Ready)

### 1. Add to `config/validation_config.py` (after line 136)

```python
OPTIMIZED_TECHNICAL = ValidationConfig(
    min_term_length=4,
    max_term_length=80,
    min_word_count=1,
    max_word_count=4,
    max_symbol_ratio=0.25,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=3,
    max_acronym_length=8,
    language="en"
)
```

### 2. Update `src/backend/routers/documents.py` (line 272-280)

**Find:**
```python
if process_request.extract_terms and extracted_text:
    term_extractor = TermExtractor(language=process_request.language)
    extracted_terms = term_extractor.extract_terms(
        text=extracted_text,
        min_term_length=3,
        max_term_length=100,
        min_frequency=1,
        pages_data=pages_data
    )
```

**Replace with:**
```python
if process_request.extract_terms and extracted_text:
    from config.validation_config import OPTIMIZED_TECHNICAL
    from services.term_validator import TermValidator

    validator = TermValidator(OPTIMIZED_TECHNICAL)
    term_extractor = TermExtractor(language=process_request.language, validator=validator)

    extracted_terms = term_extractor.extract_terms(
        text=extracted_text,
        min_term_length=4,
        max_term_length=80,
        min_frequency=2,
        pages_data=pages_data,
        enable_validation=True
    )
```

### 3. Add to stop words in `src/backend/services/term_validator.py` (line 84)

**Add before the closing `}`:**
```python
        # PDF extraction fragments
        "ing", "tion", "ment", "res", "tech", "ions",
        # Ordinals
        "first", "second", "third", "fourth", "fifth",
        # Abbreviations
        "etc", "e.g", "i.e", "et al", "cf", "vs",
```

---

## Testing Commands

### Test validation changes
```bash
python scripts/analyze_validation.py
```

### Quick term quality check
```bash
python -c "
import sqlite3
conn = sqlite3.connect('./data/glossary.db')
cursor = conn.cursor()
cursor.execute('SELECT term FROM glossary_entries LIMIT 50')
for row in cursor.fetchall():
    print(row[0])
"
```

### A/B test setup
```bash
# Backup current database
cp data/glossary.db data/glossary_backup_before_validation.db

# Process a test PDF with new config
# (use API or frontend)

# Compare results
python scripts/analyze_validation.py > validation_after.txt
diff validation_before.txt validation_after.txt
```

---

## Rollback Instructions

### Quick rollback (revert extraction only)
```python
# In documents.py line 272
term_extractor = TermExtractor(language=process_request.language)
extracted_terms = term_extractor.extract_terms(
    text=extracted_text,
    min_term_length=3,
    max_term_length=100,
    min_frequency=1,
    pages_data=pages_data
)
```

### Full rollback (Git)
```bash
git checkout -- config/validation_config.py
git checkout -- src/backend/routers/documents.py
git checkout -- src/backend/services/term_validator.py
```

---

## Key Metrics to Monitor

**Before Changes:**
- Total terms: 4,511
- Rejection rate: 0.2%
- Fragments: Ing (774), Tion (196), Res (155)
- Stop word contamination: 30.5%

**After Changes (Expected):**
- Total terms: 3,200-3,800
- Rejection rate: 15-25%
- Fragments: FILTERED
- Stop word contamination: <10%

**Red Flags (if you see these, rollback):**
- Rejection rate >40% (too aggressive)
- Missing important technical terms
- Processing time >2x slower
- User complaints about missing terms

---

## Quality Checklist

After implementing changes, check these manually:

**Good Signs (✅):**
- [ ] Fragments like "Ing", "Tion", "Res" are gone
- [ ] Stop words like "The", "And" are reduced
- [ ] Technical terms like "Bioreactor", "Sensor" are kept
- [ ] Acronyms like "API", "SQL" are kept
- [ ] Compound terms like "Process Development" are kept

**Bad Signs (❌):**
- [ ] Valid terms like "API", "SQL" are rejected
- [ ] Important 3-letter acronyms are missing
- [ ] Rejection rate >40%
- [ ] Processing takes 2x longer

---

## Files Changed Summary

```
Modified:
  config/validation_config.py           (+15 lines)
  src/backend/services/term_validator.py   (+10 lines)
  src/backend/routers/documents.py       (~10 lines modified)

New:
  docs/VALIDATION_ANALYSIS.md
  docs/VALIDATION_CODE_CHANGES.md
  docs/VALIDATION_SUMMARY.md
  docs/VALIDATION_QUICK_REFERENCE.md
  scripts/analyze_validation.py
```

---

## Common Issues & Solutions

### Issue: Too many terms rejected
**Solution:** Reduce min_frequency from 2 to 1, or use DEFAULT profile instead of OPTIMIZED

### Issue: Fragments still appearing
**Solution:** Increase min_term_length from 4 to 5, add fragments to stop words

### Issue: Important acronyms rejected
**Solution:** Reduce min_acronym_length from 3 to 2

### Issue: Processing too slow
**Solution:** Disable enable_validation temporarily, or use simpler profile

---

## Contact / Questions

If you encounter issues:
1. Check `backend-error.log` for errors
2. Run `python scripts/analyze_validation.py` for metrics
3. Review extracted terms manually (first 50-100)
4. Adjust configuration based on domain needs

---

**Last Updated:** 2025-10-18
**Status:** READY TO IMPLEMENT
**Estimated Time:** 30 min implementation + 2 hours testing
