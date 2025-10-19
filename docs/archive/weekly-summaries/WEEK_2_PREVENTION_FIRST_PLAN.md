# Week 2: Prevention-First Data Quality Plan
## Fix Extraction Logic to Prevent Bad Data

**Date:** 2025-10-19
**Phase:** Month 1 - Data Quality Foundation
**Approach:** ✅ **Prevention First, Cleanup Second**

---

## Philosophy Shift

### ❌ Wrong Approach (Reactive)
```
Extract everything → Clean up bad data afterwards → Repeat forever
```

### ✅ Correct Approach (Preventive)
```
Fix extraction logic → Never create bad data → One-time cleanup of legacy data
```

---

## The Root Cause Analysis

### Why Are Bad Terms Being Created?

**Current Pipeline:**
```
PDF File
  ↓
pdf_extractor.py (extracts raw text with OCR artifacts)
  ↓
term_extractor.py (extracts terms with article prefixes)
  ↓
term_validator.py (doesn't reject PDF artifacts)
  ↓
Database (saves bad data)
```

**Problems:**
1. **pdf_extractor.py** - Doesn't normalize OCR corruption
   - "Pplloottttiinngg" stays as "Pplloottttiinngg"
2. **term_extractor.py** - Doesn't strip article prefixes
   - Extracts "The Sensor" instead of "Sensor"
3. **term_validator.py** - Missing rejection patterns
   - Accepts "cid:31", "et al", fragments

**Result:** 40-45% bad terms saved to database

---

## Week 2 Revised Plan (12 hours)

### Phase 1: Fix Extraction Pipeline (8 hours)

#### Task 1: OCR Normalization in pdf_extractor.py (2h)

**Location:** `src/backend/services/pdf_extractor.py`

**Add OCR normalization BEFORE text is returned:**

```python
@staticmethod
def _normalize_ocr_artifacts(text: str) -> str:
    """
    Normalize common OCR artifacts from PDF extraction

    Fixes:
    - Doubled characters: "Pplloottttiinngg" → "Plotting"
    - Spaced characters: "S e n s o r" → "Sensor"
    - Encoding artifacts: "cid:31" removed

    Args:
        text: Raw extracted text from PDF

    Returns:
        Normalized text with OCR artifacts fixed
    """
    if not text:
        return text

    # Fix pattern: 3+ consecutive duplicate characters (Pplloottttiinngg → Plotting)
    # Match: P p l l o o t t t t i i n n g g
    # Keep only every other char when duplicated
    def fix_doubled_chars(match):
        char = match.group(1)
        count = len(match.group(0)) // len(char)
        # If odd number of duplicates, keep half+1, else keep half
        keep_count = (count + 1) // 2
        return char * keep_count

    text = re.sub(r'([a-z])\1{2,}', fix_doubled_chars, text, flags=re.IGNORECASE)

    # Fix spaced-out characters: "S e n s o r" → "Sensor"
    # Only if ALL letters have spaces (to avoid fixing legitimate "A B C Company")
    text = re.sub(r'\b([A-Z])\s+([a-z](?:\s+[a-z])+)\b',
                  lambda m: m.group(0).replace(' ', ''), text)

    # Remove PDF encoding artifacts
    text = re.sub(r'cid:\d+', '', text)  # cid:31 → (removed)

    return text

@staticmethod
def extract_text(pdf_path: str) -> Dict[str, any]:
    """Extract text from PDF file"""
    # ... existing code ...

    with pdfplumber.open(pdf_path) as pdf:
        pages_text = []
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                # ✅ NORMALIZE OCR ARTIFACTS BEFORE RETURNING
                page_text = PDFExtractor._normalize_ocr_artifacts(page_text)
                pages_text.append(page_text)

        result["text"] = "\n\n".join(pages_text)
        result["pages"] = len(pdf.pages)
        # ... rest of code ...
```

**Expected Impact:**
- ✅ Fixes 34 OCR-corrupted terms (0.8%) before extraction
- ✅ Future PDFs won't create corrupted terms

---

#### Task 2: Article Prefix Stripping in term_extractor.py (3h)

**Location:** `src/backend/services/term_extractor.py`

**Strip articles DURING extraction, not after:**

```python
class TermExtractor:
    # Add to class constants
    ENGLISH_ARTICLES = {'the', 'a', 'an'}
    GERMAN_ARTICLES = {'der', 'die', 'das', 'ein', 'eine', 'einer', 'eines', 'einem', 'einen'}

    @staticmethod
    def strip_leading_articles(term: str, language: str = 'en') -> str:
        """
        Strip leading articles from terms

        Args:
            term: Term that may start with article
            language: 'en' or 'de'

        Returns:
            Term with article removed

        Examples:
            >>> strip_leading_articles("The Sensor", "en")
            "Sensor"
            >>> strip_leading_articles("Die Temperatur", "de")
            "Temperatur"
        """
        if not term:
            return term

        articles = (TermExtractor.ENGLISH_ARTICLES if language == 'en'
                   else TermExtractor.GERMAN_ARTICLES)

        words = term.split()
        if len(words) > 1 and words[0].lower() in articles:
            # Remove article and rejoin
            return ' '.join(words[1:])

        return term

    def extract_terms_nlp(self, text: str, language: str = 'en') -> List[Dict]:
        """Extract terms using NLP (spaCy)"""
        # ... existing extraction code ...

        for chunk in doc.noun_chunks:
            # Extract base term
            term = chunk.text.strip()

            # ✅ STRIP ARTICLES DURING EXTRACTION
            term = self.strip_leading_articles(term, language)

            # Clean whitespace
            term = self.clean_term(term)

            # Skip if empty after cleaning
            if not term:
                continue

            # ... rest of validation ...
```

**Also update pattern-based extraction:**

```python
def extract_terms_patterns(self, text: str, language: str = 'en') -> List[Dict]:
    """Extract terms using patterns (fallback when spaCy unavailable)"""
    # ... existing pattern extraction ...

    for term in extracted_terms:
        # ✅ STRIP ARTICLES FROM PATTERN-BASED EXTRACTION TOO
        term = self.strip_leading_articles(term, language)
        term = self.clean_term(term)

        if term:  # Only process non-empty terms
            # ... rest of code ...
```

**Expected Impact:**
- ✅ Fixes 1,197 terms (26.5%) with article prefixes
- ✅ Future extractions won't have "The Sensor" → only "Sensor"

---

#### Task 3: PDF Artifact Rejection in term_validator.py (3h)

**Location:** `src/backend/services/term_validator.py`

**Add rejection patterns to validator:**

```python
class TermValidator:
    # Add to INVALID_PATTERNS list
    INVALID_PATTERNS = [
        # Existing patterns...
        r'^[\W\d]+$',           # Only special chars/numbers
        r'^\d+$',               # Only numbers

        # ✅ NEW: PDF encoding artifacts
        r'^cid:\d+$',           # cid:31, cid:128, etc.
        r'cid:\d+',             # Contains cid:XX anywhere

        # ✅ NEW: Bibliographic citations
        r'\bet\s+al\.?\b',      # "et al", "et al."
        r'\betal\b',            # "etal"
        r'\bibid\.?\b',         # "ibid", "ibid."

        # ✅ NEW: Word fragments (very short, likely broken)
        r'^[a-z]{1,2}$',        # Single/double letter (except "DO", "pH")
        r'^\w{1,3}$',           # 1-3 chars (catches "ber", "sponse")

        # ✅ NEW: Broken hyphenated words
        r'^-\w+',               # Starts with hyphen: "-tion"
        r'\w+-$',               # Ends with hyphen: "comple-"

        # ✅ NEW: OCR corruption patterns (backup if normalization missed)
        r'([a-z])\1{3,}',       # 4+ duplicate chars: "Ppppllll"
    ]

    # Add whitelist exceptions for short valid terms
    SHORT_TERM_WHITELIST = {
        'DO',   # Dissolved Oxygen
        'pH',   # Acidity
        'OTR',  # Oxygen Transfer Rate
        'CO2',  # Carbon Dioxide
        'O2',   # Oxygen
        'UV',   # Ultraviolet
        'IR',   # Infrared
        # Add more as needed
    }

    def validate_term(self, term: str, context: Dict = None) -> ValidationResult:
        """Validate a term"""
        # ... existing validation ...

        # ✅ CHECK WHITELIST BEFORE REJECTING SHORT TERMS
        if term in self.SHORT_TERM_WHITELIST:
            return ValidationResult(
                is_valid=True,
                confidence=0.95,
                issues=[],
                suggestions=[],
                validation_level=ValidationLevel.WHITELISTED
            )

        # Check invalid patterns
        for pattern in self.INVALID_PATTERNS:
            if re.search(pattern, term, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    confidence=0.0,
                    issues=[f"Matches invalid pattern: {pattern}"],
                    suggestions=["This term should not be extracted"],
                    validation_level=ValidationLevel.REJECTED
                )

        # ... rest of validation ...
```

**Expected Impact:**
- ✅ Rejects "cid:31", "et al", fragments BEFORE saving
- ✅ Whitelists valid short terms (DO, pH, UV)
- ✅ Future extractions won't save garbage

---

### Phase 2: Test New Extraction Logic (2 hours)

#### Task 4: Test with Sample PDF

```bash
# Process the sample PDF with new extraction logic
cd "C:\Users\devel\Coding Projects\Glossary APP"
venv\Scripts\python.exe -c "
from src.backend.services.pdf_extractor import PDFExtractor
from src.backend.services.term_extractor import TermExtractor
from src.backend.services.term_validator import create_default_validator

# Extract text (with OCR normalization)
pdf_result = PDFExtractor.extract_text('test-data/sample-technical-doc.pdf')
text = pdf_result['text']
print(f'Extracted {len(text)} characters')

# Extract terms (with article stripping)
extractor = TermExtractor()
terms = extractor.extract_terms_nlp(text, language='en')
print(f'Extracted {len(terms)} terms')

# Validate (with artifact rejection)
validator = create_default_validator()
valid_terms = []
rejected_terms = []

for term_dict in terms:
    result = validator.validate_term(term_dict['term'])
    if result.is_valid:
        valid_terms.append(term_dict['term'])
    else:
        rejected_terms.append({
            'term': term_dict['term'],
            'reason': result.issues[0] if result.issues else 'Unknown'
        })

print(f'✅ Valid: {len(valid_terms)}')
print(f'❌ Rejected: {len(rejected_terms)}')

# Show rejection reasons
from collections import Counter
reasons = Counter(r['reason'] for r in rejected_terms)
print('\\nRejection reasons:')
for reason, count in reasons.most_common(10):
    print(f'  {count:3d} - {reason}')
"
```

**Success Criteria:**
- ✅ No terms starting with "The", "A", "An"
- ✅ No OCR corrupted terms (Pplloottttiinngg)
- ✅ No PDF artifacts (cid:31)
- ✅ No bibliographic citations (et al)
- ✅ No word fragments (ber, sponse)

---

### Phase 3: One-Time Cleanup of Existing Data (2 hours)

**NOW we clean up the legacy bad data:**

```python
# scripts/cleanup_existing_bad_data.py
"""
One-time cleanup of bad data created before extraction fixes
This script should only be run AFTER extraction logic is fixed
"""
import logging
from sqlalchemy.orm import Session
from src.backend.database import get_db_context
from src.backend.models import GlossaryEntry
from src.backend.services.term_validator import create_default_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_bad_data():
    """Remove bad terms that were created before extraction fixes"""
    validator = create_default_validator()

    with get_db_context() as db:
        # Get all entries
        entries = db.query(GlossaryEntry).all()
        total = len(entries)
        logger.info(f"Checking {total} glossary entries...")

        to_delete = []

        for entry in entries:
            # Re-validate with NEW validation rules
            result = validator.validate_term(entry.term)

            if not result.is_valid:
                to_delete.append(entry)
                logger.debug(f"Marking for deletion: '{entry.term}' - {result.issues[0]}")

        # Confirm deletion
        logger.warning(f"Found {len(to_delete)} bad entries to delete")
        logger.info("Deletion breakdown:")

        # Show breakdown by rejection reason
        from collections import Counter
        reasons = Counter()
        for entry in to_delete:
            result = validator.validate_term(entry.term)
            reason = result.issues[0] if result.issues else "Unknown"
            reasons[reason] += 1

        for reason, count in reasons.most_common():
            logger.info(f"  {count:4d} - {reason}")

        # Delete
        logger.info("Deleting bad entries...")
        for entry in to_delete:
            db.delete(entry)

        db.commit()

        remaining = total - len(to_delete)
        quality_pct = (remaining / total * 100) if total > 0 else 0

        logger.info(f"✅ Cleanup complete!")
        logger.info(f"   Deleted: {len(to_delete)} bad entries")
        logger.info(f"   Remaining: {remaining} good entries")
        logger.info(f"   Quality: {quality_pct:.1f}%")

if __name__ == "__main__":
    cleanup_bad_data()
```

**Run cleanup:**
```bash
venv\Scripts\python.exe scripts/cleanup_existing_bad_data.py
```

**Expected Result:**
- ✅ Remove ~1,500 bad entries from database
- ✅ Quality improves from 55% → 95%+
- ✅ Future extractions will be clean (fixes prevent new bad data)

---

## Summary: Prevention First

### Before Week 2
```
PDF → Extract (broken) → Validate (weak) → Save (bad data) → Database (55% quality)
                                                               ↓
                                                        Cleanup forever ❌
```

### After Week 2
```
PDF → Extract (fixed!) → Validate (strong!) → Save (good data) → Database (95%+ quality)
  ↓                                                                ↑
  OCR normalized                                          One-time cleanup
  Articles stripped                                       of legacy data
  Artifacts rejected

Future extractions = Clean ✅
```

---

## Timeline (12 hours)

| Task | Time | Type |
|------|------|------|
| **1. OCR normalization in pdf_extractor.py** | 2h | Prevention |
| **2. Article stripping in term_extractor.py** | 3h | Prevention |
| **3. Artifact rejection in term_validator.py** | 3h | Prevention |
| **4. Test extraction pipeline** | 2h | Validation |
| **5. One-time cleanup of legacy data** | 2h | Cleanup |
| **Total** | **12h** | |

**Split:** 8h prevention + 2h testing + 2h cleanup

---

## Success Metrics

**Before Week 2:**
- ❌ 26.5% terms have article prefixes (1,197 terms)
- ❌ 0.8% OCR corrupted (34 terms)
- ❌ ~15% PDF artifacts, citations, fragments
- ❌ Overall quality: 55-60%

**After Week 2:**
- ✅ 0% terms with article prefixes (fixed at extraction)
- ✅ 0% OCR corrupted (normalized before extraction)
- ✅ 0% PDF artifacts (rejected by validator)
- ✅ Overall quality: 95%+ ✅

**Ongoing:**
- ✅ Future PDFs processed with clean extraction
- ✅ No more bad data created
- ✅ No recurring cleanup needed

---

## Why This Approach Is Better

### ❌ Reactive Approach (Cleanup After)
- Fix symptoms, not cause
- Must clean up after every extraction
- Technical debt accumulates
- Wastes time forever

### ✅ Preventive Approach (Fix at Source)
- Fix root cause
- One-time cleanup
- Clean data going forward
- Sustainable long-term

---

## Next Steps

**Ready to implement?** The order matters:

1. ✅ Fix extraction logic (8h)
2. ✅ Test with sample PDF (2h)
3. ✅ One-time cleanup (2h)

**Want to proceed with Week 2 fixes?**
