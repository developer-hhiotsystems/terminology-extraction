# Term Extraction Quality - Quick Fix Checklist

## Problem Summary
**Current Quality:** 70.7% acceptable (755 of 2,577 entries are garbage)
**Target Quality:** 90%+ acceptable

## Root Causes (Priority Order)

### 1. No Stopword Filtering - CRITICAL
**Impact:** 6+ stopwords + hundreds of generic words
**Files:** `term_extractor.py` lines 88-97
**Fix:** Add STOP_WORDS filtering before adding to candidates

### 2. No Fragment Detection - CRITICAL
**Impact:** 379 entries (14.7%) are suffix fragments ("Tion", "Gulation")
**Files:** `term_extractor.py` lines 88-91
**Fix:** Detect and reject terms that are incomplete words

### 3. No Numeric/Symbol Filtering - CRITICAL
**Impact:** 296 entries (11.5%) contain numbers/symbols
**Files:** `term_extractor.py` lines 90, 96
**Fix:** Add character validation (alphanumeric check)

### 4. Min Length Too Short - HIGH
**Impact:** 74 entries (2.9%) are 3 chars or less
**Files:** `routers/documents.py` line 276
**Fix:** Change `min_term_length=3` to `min_term_length=4`

### 5. Min Frequency Too Low - HIGH
**Impact:** Allows OCR errors and typos (freq=1)
**Files:** `routers/documents.py` line 278
**Fix:** Change `min_frequency=1` to `min_frequency=2`

### 6. Not Using spaCy Features - MEDIUM
**Impact:** Missing built-in quality checks
**Files:** `term_extractor.py` lines 82-97
**Fix:** Use `token.is_stop`, `token.pos_`, `token.is_alpha`

---

## Quick Implementation Guide

### Step 1: Add Validation Function (5 min)
```python
# Add to term_extractor.py after imports
from spacy.lang.en.stop_words import STOP_WORDS
import re

CUSTOM_STOPWORDS = {
    'use', 'end', 'source', 'figure', 'table', 'page', 'section'
}
ALL_STOPWORDS = STOP_WORDS.union(CUSTOM_STOPWORDS)

SUFFIX_FRAGMENTS = {
    'tion', 'tions', 'ment', 'ness', 'ing', 'zation', 'gulation',
    'ization', 'ring', 'ducts', 'ance', 'ence'
}

def is_valid_term(term: str) -> bool:
    """Validate term quality"""
    term_lower = term.lower()

    # Reject stopwords
    if term_lower in ALL_STOPWORDS:
        return False

    # Reject fragments
    if term_lower in SUFFIX_FRAGMENTS or term[0].islower():
        return False

    # Reject pure numbers
    if re.match(r'^\d+$', term):
        return False

    # Reject if contains symbols (except hyphens)
    if re.search(r'[%$#@!&*()+=\[\]{}|\\:;"\'<>,?/]', term):
        return False

    # Reject if starts/ends with non-letter
    if not term[0].isalpha() or not term[-1].isalnum():
        return False

    # Reject if too many numbers
    num_digits = sum(c.isdigit() for c in term)
    if num_digits / len(term) > 0.3:
        return False

    return True
```

### Step 2: Update spaCy Extraction (10 min)
```python
# Replace lines 88-91 in _extract_with_spacy()
for chunk in doc.noun_chunks:
    term = chunk.text.strip()

    # Apply validation
    if not is_valid_term(term):
        continue

    # Additional spaCy-specific checks
    root = chunk.root
    if root.is_stop or not root.is_alpha:
        continue
    if root.pos_ not in ['NOUN', 'PROPN']:
        continue

    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())

# Also update lines 94-97 for entities
for ent in doc.ents:
    term = ent.text.strip()

    if not is_valid_term(term):
        continue

    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())
```

### Step 3: Update Document Router (2 min)
```python
# Update routers/documents.py lines 274-279
extracted_terms = term_extractor.extract_terms(
    text=extracted_text,
    min_term_length=4,  # Changed from 3 to 4
    max_term_length=100,
    min_frequency=2,  # Changed from 1 to 2
    pages_data=pages_data
)
```

### Step 4: Update Pattern Fallback (5 min)
```python
# Update lines 146-150 in _extract_with_patterns()
for pattern in patterns:
    matches = re.findall(pattern, text)
    for match in matches:
        # Apply same validation
        if not is_valid_term(match):
            continue

        if min_term_length <= len(match) <= max_term_length:
            candidates.add(match)
```

---

## Testing Checklist

- [ ] Test stopword filtering: "The system" should not extract "The"
- [ ] Test fragment detection: "Regulation" OK, "Gulation" rejected
- [ ] Test numeric filtering: "4000" rejected, "temperature" OK
- [ ] Test symbol filtering: "[%]", "70%" rejected
- [ ] Test minimum length: 3-char terms rejected
- [ ] Test frequency threshold: single-occurrence terms rejected
- [ ] Test valid technical terms: "Production", "Technology" accepted

---

## Database Cleanup

After implementing fixes, clean existing database:

```python
# Script to remove low-quality entries
from src.backend.database import SessionLocal
from src.backend.models import GlossaryEntry

db = SessionLocal()

# Remove entries that fail validation
removed_count = 0
entries = db.query(GlossaryEntry).all()

for entry in entries:
    if not is_valid_term(entry.term):
        db.delete(entry)
        removed_count += 1

db.commit()
print(f"Removed {removed_count} low-quality entries")
```

---

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Total Entries | 2,577 | ~1,800 |
| Low-Quality % | 29.3% | <5% |
| Stopwords | 6 | 0 |
| Fragments | 379 | <10 |
| With Numbers | 296 | <20 |
| Quality Score | 4/10 | 8/10 |

---

## Estimated Time
- Implementation: 30 minutes
- Testing: 30 minutes
- Database cleanup: 15 minutes
- **Total: ~1.5 hours**

---

## Files to Modify
1. `src/backend/services/term_extractor.py` (main changes)
2. `src/backend/routers/documents.py` (parameter updates)
3. Create cleanup script (optional)

---

**Priority:** CRITICAL - Do not process more documents until fixed
**Difficulty:** LOW - Straightforward validation logic
**Impact:** HIGH - Reduces bad entries from 30% to <5%
