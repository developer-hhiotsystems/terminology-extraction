# TermValidator Tuning Recommendations

**Date:** 2025-10-18
**Review Type:** Post-Implementation Quality Assessment
**Reviewer:** Technical Documentation Specialist
**Status:** 🔴 CRITICAL ISSUES FOUND

---

## Executive Summary

After reviewing 80 random terms (1.8% of 4,511 total), the TermValidator shows **significant quality issues**:

- **42.5% BAD** (should be rejected but passed validation)
- **32.5% QUESTIONABLE** (borderline quality)
- **17.5% GOOD** (acceptable but generic)
- **7.5% EXCELLENT** (perfect technical terms)

**Overall Grade: D+ (Poor)**

**Recommendation:** Implement CRITICAL (P0) fixes immediately before production use.

---

## Critical Issues Summary

### Issue 1: Leading Articles Not Filtered (14 terms affected)
**Examples:**
- "The Development"
- "A Promising Approach"
- "An Additional Way"

**Impact:** 17.5% of sample
**Severity:** CRITICAL
**Fix:** Check if term STARTS with article, not just if entire term IS article

---

### Issue 2: Line Break Artifacts (7 terms affected)
**Examples:**
- "Minute\nH"
- "The Nitro-\nGen Excess"
- "Gassing\nDevices"

**Impact:** 8.75% of sample
**Severity:** CRITICAL
**Fix:** Preprocess terms to clean line breaks and hyphenation before validation

---

### Issue 3: OCR Doubled Characters (4 terms affected)
**Examples:**
- "Tthhee Ssttiirrrreerr"
- "Bbeeyyoonndd 5500 Lliittrreess"

**Impact:** 5% of sample
**Severity:** CRITICAL
**Fix:** Detect pattern of doubled characters using regex: `(.)\1(.)\2(.)\3`

---

### Issue 4: Document Structure Artifacts (8 terms affected)
**Examples:**
- "5.4 Example D" (section heading)
- "= Eq" (equation fragment)
- "14\n\nSingle-Use Technology" (page number + heading)

**Impact:** 10% of sample
**Severity:** CRITICAL
**Fix:** Reject terms matching document structure patterns

---

## Recommended Code Changes

### 1. Add Preprocessing Function (CRITICAL - P0)

**File:** `src/backend/services/term_validator.py`

**Add this function at module level:**

```python
import re

def preprocess_term(term: str) -> str:
    """
    Clean PDF extraction artifacts before validation.

    Handles:
    - Hyphenation across line breaks: "nitro-\ngen" → "nitrogen"
    - Line breaks within terms: "Minute\nH" → "Minute H"
    - Multiple whitespace: "  " → " "

    Args:
        term: Raw extracted term

    Returns:
        Cleaned term ready for validation
    """
    if not term:
        return term

    # Fix hyphenation across line breaks
    # Pattern: word-\nword → wordword
    term = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', term)

    # Replace remaining line breaks with spaces
    term = re.sub(r'\n+', ' ', term)

    # Normalize whitespace
    term = ' '.join(term.split())

    return term
```

**Modify `is_valid_term()` method:**

```python
def is_valid_term(self, term: str) -> bool:
    """Check if a term is valid"""
    if not term or not isinstance(term, str):
        return False

    # CRITICAL: Preprocess term before validation
    term = preprocess_term(term)

    if not term:  # Check again after preprocessing
        return False

    # Run all validation checks
    validators = [
        self._validate_length,
        self._validate_not_empty_or_whitespace,
        self._validate_not_pure_number,
        self._validate_not_percentage,
        self._validate_not_pure_symbols,
        self._validate_symbol_ratio,
        self._validate_not_stop_word,
        self._validate_not_leading_article,      # NEW
        self._validate_not_leading_demonstrative,  # NEW
        self._validate_not_leading_question_word,  # NEW
        self._validate_word_count,
        self._validate_not_fragment,
        self._validate_capitalization,
        self._validate_not_ocr_artifact,          # NEW
        self._validate_not_document_artifact,     # NEW
    ]

    for validator in validators:
        is_valid, _ = validator(term)
        if not is_valid:
            return False

    return True
```

---

### 2. Add Leading Article Detection (CRITICAL - P0)

```python
def _validate_not_leading_article(self, term: str) -> Tuple[bool, str]:
    """
    Validate term does not start with an article.

    Articles: a, an, the

    Args:
        term: The term to validate

    Returns:
        (is_valid, rejection_reason)

    Examples:
        "The Development" → False
        "Development" → True
        "A Promising Approach" → False
        "Approach" → True
    """
    words = term.strip().split()
    if not words:
        return True, ""

    first_word = words[0].lower()

    if first_word in ['a', 'an', 'the']:
        return False, f"Term starts with article: '{first_word}'"

    return True, ""
```

---

### 3. Add Demonstrative Detection (HIGH - P1)

```python
def _validate_not_leading_demonstrative(self, term: str) -> Tuple[bool, str]:
    """
    Validate term does not start with a demonstrative pronoun.

    Demonstratives: this, that, these, those

    Args:
        term: The term to validate

    Returns:
        (is_valid, rejection_reason)

    Examples:
        "These Plants" → False
        "Plants" → True
    """
    words = term.strip().split()
    if not words:
        return True, ""

    first_word = words[0].lower()

    demonstratives = ['this', 'that', 'these', 'those']

    if first_word in demonstratives:
        return False, f"Term starts with demonstrative: '{first_word}'"

    return True, ""
```

---

### 4. Add Question Word Detection (HIGH - P1)

```python
def _validate_not_leading_question_word(self, term: str) -> Tuple[bool, str]:
    """
    Validate term does not start with a question word.

    Question words: which, what, where, when, why, how, who

    Args:
        term: The term to validate

    Returns:
        (is_valid, rejection_reason)

    Examples:
        "Which Execution Approach" → False
        "Execution Approach" → True
    """
    words = term.strip().split()
    if not words:
        return True, ""

    first_word = words[0].lower()

    question_words = ['which', 'what', 'where', 'when', 'why', 'how', 'who']

    if first_word in question_words:
        return False, f"Term starts with question word: '{first_word}'"

    return True, ""
```

---

### 5. Add OCR Artifact Detection (CRITICAL - P0)

```python
def _validate_not_ocr_artifact(self, term: str) -> Tuple[bool, str]:
    """
    Validate term is not an OCR artifact with doubled characters.

    Detects patterns like:
    - "Tthhee" (every character doubled)
    - "Ssttiirrrreerr"

    Args:
        term: The term to validate

    Returns:
        (is_valid, rejection_reason)

    Examples:
        "Tthhee Ssttiirrrreerr" → False
        "The Stirrer" → True
    """
    cleaned = term.strip()

    # Pattern: Three consecutive doubled characters
    # (.)\1(.)\2(.)\3 matches: T-T-h-h-e-e
    if re.search(r'(.)\1(.)\2(.)\3', cleaned):
        return False, "Term contains OCR doubling artifacts"

    return True, ""
```

---

### 6. Add Document Artifact Detection (CRITICAL - P0)

```python
def _validate_not_document_artifact(self, term: str) -> Tuple[bool, str]:
    """
    Validate term is not a document structure artifact.

    Rejects:
    - Section numbers: "5.4 Example D", "6 3. Overview"
    - Page numbers: "14\n\nSingle-Use"
    - Equations: "= Eq", "Dt Eq"
    - Citations: "52-64\n"
    - Table data: "Run 1 2.0"

    Args:
        term: The term to validate

    Returns:
        (is_valid, rejection_reason)
    """
    cleaned = term.strip()

    # Patterns for document artifacts
    patterns = [
        (r'^\d+\.?\d*\s+\w+', "Section number"),
        (r'^\d+\s*\n\s*\w+', "Page number with text"),
        (r'^\d+[-–]\d+\s*\n', "Page range"),
        (r'^(Run|Test|Trial|Sample)\s+\d+', "Data table entry"),
        (r'^=\s*Eq', "Equation fragment"),
        (r'^\w{1,2}\s+Eq$', "Variable + equation"),
        (r'^\d+\.\d+\s+\w+\s+\w+', "Numbered heading"),
        (r'^\(\w+\)?\s*$', "Lone parenthetical"),
    ]

    for pattern, description in patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False, f"Term is a document artifact: {description}"

    return True, ""
```

---

### 7. Update ValidationConfig (HIGH - P1)

**Add new fields to dataclass:**

```python
@dataclass
class ValidationConfig:
    """Configuration for term validation rules"""

    # ... existing fields ...

    # NEW: Linguistic filtering
    reject_leading_articles: bool = True
    reject_leading_demonstratives: bool = True
    reject_leading_question_words: bool = True
    reject_leading_comparatives: bool = True

    # NEW: Preprocessing
    preprocess_terms: bool = True

    # NEW: Generic term filtering
    reject_overly_generic_singles: bool = True
    generic_single_words: set = None

    def __post_init__(self):
        """Initialize stop words and generic terms if not provided"""
        if self.stop_words is None:
            self.stop_words = self._get_default_stop_words()

        if self.generic_single_words is None:
            self.generic_single_words = {
                'time', 'end', 'start', 'begin', 'air', 'water',
                'basis', 'year', 'day', 'hour', 'minute', 'second',
                'first', 'last', 'next', 'previous', 'grey', 'gray',
            }
```

---

### 8. Reduce Max Word Count (HIGH - P1)

**Change default from 4 to 3:**

```python
@dataclass
class ValidationConfig:
    # ...
    max_word_count: int = 3  # Changed from 4
    # ...
```

**Rationale:**
- Most good technical terms are 1-3 words
- 4+ word terms are usually sentence fragments
- Examples: "Mass Transfer Coefficient" (3), "Particle Image Velocimetry" (3)

---

## Updated Factory Functions

### Default Profile (Recommended for Production)

```python
def create_default_validator(language: str = "en") -> TermValidator:
    """
    Create a validator with balanced rules for production use.

    Filters out:
    - Numbers, percentages, symbols
    - Leading articles, demonstratives, question words
    - OCR artifacts and document structure
    - Overly generic single words
    - Line break artifacts (via preprocessing)

    Args:
        language: Language code ('en' or 'de')

    Returns:
        TermValidator with production-ready configuration
    """
    config = ValidationConfig(
        min_term_length=3,
        max_term_length=80,
        min_word_count=1,
        max_word_count=3,              # Reduced from 4
        max_symbol_ratio=0.2,           # Reduced from 0.3
        reject_pure_numbers=True,
        reject_percentages=True,
        allow_all_uppercase=True,
        min_acronym_length=2,
        max_acronym_length=8,
        reject_leading_articles=True,   # NEW
        reject_leading_demonstratives=True,  # NEW
        reject_leading_question_words=True,  # NEW
        preprocess_terms=True,          # NEW
        reject_overly_generic_singles=True,  # NEW
        language=language
    )
    return TermValidator(config)
```

---

## Testing Requirements

### Unit Tests to Add

**File:** `tests/unit/test_term_validator.py`

```python
import pytest
from src.backend.services.term_validator import (
    TermValidator,
    create_default_validator,
    preprocess_term
)

class TestPreprocessing:
    """Test term preprocessing"""

    def test_hyphenation_removal(self):
        assert preprocess_term("nitro-\ngen") == "nitrogen"
        assert preprocess_term("oxy-\ngen") == "oxygen"

    def test_line_break_to_space(self):
        assert preprocess_term("Minute\nH") == "Minute H"
        assert preprocess_term("The\nData") == "The Data"

    def test_whitespace_normalization(self):
        assert preprocess_term("  double  space  ") == "double space"


class TestLeadingArticles:
    """Test article detection"""

    def setup_method(self):
        self.validator = create_default_validator()

    def test_reject_the(self):
        assert not self.validator.is_valid_term("The Development")
        assert not self.validator.is_valid_term("the approach")

    def test_reject_a(self):
        assert not self.validator.is_valid_term("A Promising Approach")

    def test_reject_an(self):
        assert not self.validator.is_valid_term("An Additional Way")

    def test_accept_without_article(self):
        assert self.validator.is_valid_term("Development")
        assert self.validator.is_valid_term("Approach")


class TestDemonstratives:
    """Test demonstrative detection"""

    def setup_method(self):
        self.validator = create_default_validator()

    def test_reject_these(self):
        assert not self.validator.is_valid_term("These Plants")

    def test_reject_those(self):
        assert not self.validator.is_valid_term("Those Methods")

    def test_accept_without_demonstrative(self):
        assert self.validator.is_valid_term("Plants")
        assert self.validator.is_valid_term("Methods")


class TestQuestionWords:
    """Test question word detection"""

    def setup_method(self):
        self.validator = create_default_validator()

    def test_reject_which(self):
        assert not self.validator.is_valid_term("Which Execution Approach")

    def test_reject_what(self):
        assert not self.validator.is_valid_term("What Process")

    def test_accept_without_question(self):
        assert self.validator.is_valid_term("Execution Approach")


class TestOCRArtifacts:
    """Test OCR error detection"""

    def setup_method(self):
        self.validator = create_default_validator()

    def test_reject_doubled_chars(self):
        assert not self.validator.is_valid_term("Tthhee Ssttiirrrreerr")
        assert not self.validator.is_valid_term("Bbeeyyoonndd")
        assert not self.validator.is_valid_term("Ffoorr Tthhee")

    def test_accept_normal_doubles(self):
        # Normal words with doubled letters should pass
        assert self.validator.is_valid_term("Stirrer")
        assert self.validator.is_valid_term("Pressure")


class TestDocumentArtifacts:
    """Test document structure detection"""

    def setup_method(self):
        self.validator = create_default_validator()

    def test_reject_section_numbers(self):
        assert not self.validator.is_valid_term("5.4 Example D")
        assert not self.validator.is_valid_term("6 3. Overview")

    def test_reject_equations(self):
        assert not self.validator.is_valid_term("= Eq")
        assert not self.validator.is_valid_term("Dt Eq")

    def test_reject_data_table(self):
        assert not self.validator.is_valid_term("Run 1 2.0")
        assert not self.validator.is_valid_term("Test 3")


class TestGoodTerms:
    """Test that valid technical terms pass"""

    def setup_method(self):
        self.validator = create_default_validator()

    def test_accept_technical_terms(self):
        good_terms = [
            "Mass Transfer Coefficient",
            "Particle Image Velocimetry",
            "Oxygen Transfer Rate",
            "Reynolds Number",
            "Construction Phase",
            "Single-Use Bioreactor",
            "Biotechnical Processes",
            "NAMUR",
            "ISO 9001",
        ]

        for term in good_terms:
            assert self.validator.is_valid_term(term), f"Should accept: {term}"
```

**Run tests:**
```bash
pytest tests/unit/test_term_validator.py -v
```

---

## Integration Testing

### Before/After Quality Comparison

1. **Backup current database:**
   ```bash
   cp data/glossary.db data/glossary_before_fixes.db
   ```

2. **Implement fixes**

3. **Reset database and re-extract:**
   ```bash
   python src/backend/reset_database.py
   # Re-upload PDFs via frontend
   ```

4. **Compare quality:**
   ```python
   # Count terms before/after
   before_count = get_term_count('data/glossary_before_fixes.db')
   after_count = get_term_count('data/glossary.db')

   reduction = (before_count - after_count) / before_count * 100
   print(f"Term reduction: {reduction:.1f}%")
   # Target: 30-40% reduction (filtering out bad terms)
   ```

5. **Manual review of sample:**
   - Same reviewer
   - Same 80-term sample size
   - Compare bad/questionable/good/excellent percentages

**Expected Results:**
- Before: 42.5% bad, 7.5% excellent
- After:  5-10% bad, 40-50% excellent
- Overall grade improvement: D+ → B+

---

## Deployment Checklist

### Pre-Deployment
- [ ] Implement all CRITICAL (P0) fixes
- [ ] Implement all HIGH (P1) fixes
- [ ] Add unit tests (minimum 80% coverage)
- [ ] Run full test suite: `pytest tests/`
- [ ] Backup production database

### Deployment
- [ ] Deploy updated `term_validator.py`
- [ ] Update `create_default_validator()` config
- [ ] Clear existing glossary (or migrate)
- [ ] Re-extract terms from all documents
- [ ] Monitor extraction logs for errors

### Post-Deployment
- [ ] Review random sample of 100 terms
- [ ] Check quality distribution (excellent/good/questionable/bad)
- [ ] Verify no regression (good terms still passing)
- [ ] Document actual results vs. expected
- [ ] User acceptance testing

---

## Monitoring & Feedback

### Quality Metrics to Track

```python
# Add to extraction pipeline
validation_stats = {
    "total_extracted": 0,
    "passed_validation": 0,
    "rejected_by_rule": {
        "leading_article": 0,
        "ocr_artifact": 0,
        "document_artifact": 0,
        "line_breaks": 0,
        # ... etc
    }
}
```

### Weekly Quality Review
- Sample 50 random terms
- Manually categorize (excellent/good/questionable/bad)
- Track percentage distribution over time
- Identify new patterns to filter

### User Feedback Loop
- Add "Report Term" button in UI
- Users can mark terms as "not a term" or "good term"
- Use feedback to tune validation rules
- Build allowlist of confirmed good terms

---

## Future Enhancements (Post-P2)

### Phase 2: Semantic Validation
- Use spaCy NLP to detect parts of speech
- Reject terms that are purely verbs or adjectives
- Identify noun phrases vs. sentence fragments
- Estimate: 2-3 weeks development

### Phase 3: LLM-Based Validation
- Use lightweight LLM to score term quality
- "Is this a valid technical term for an engineering glossary?"
- Threshold: >0.7 score to accept
- Estimate: 1-2 weeks development

### Phase 4: Domain-Specific Dictionaries
- Maintain allowlist of known engineering terms
- Import from industry standards (ISO, ASME, etc.)
- Auto-accept terms on allowlist
- Estimate: 1 week development + ongoing curation

---

## Success Criteria

### Minimum Acceptable (MVP)
- ✅ Bad terms: <15% (currently 42.5%)
- ✅ Excellent terms: >25% (currently 7.5%)
- ✅ Overall grade: C or better

### Target (Good Quality)
- ✅ Bad terms: <10%
- ✅ Excellent terms: >40%
- ✅ Overall grade: B+ or better

### Stretch Goal (Production Ready)
- ✅ Bad terms: <5%
- ✅ Excellent terms: >50%
- ✅ Overall grade: A or better

---

## Contact & Questions

**Review Author:** Technical Documentation Specialist
**Date:** 2025-10-18
**Next Review:** After P0/P1 fixes implemented

For questions about this review, consult:
- Full quality report: `docs/TERM_VALIDATION_QUALITY_REVIEW.md`
- Detailed examples: `docs/TERM_QUALITY_EXAMPLES.md`
- Implementation guide: This document
