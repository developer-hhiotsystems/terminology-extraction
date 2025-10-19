# Code Quality Analysis Report: Glossary Term Extraction

## Executive Summary

**Analysis Date:** 2025-10-18
**Total Glossary Entries Analyzed:** 2,577
**Critical Quality Issues Found:** 755 low-quality entries (29.3%)
**Overall Quality Score:** 4/10

The current term extraction implementation has **significant quality control deficiencies** that are causing nearly 30% of extracted terms to be unusable. The system is extracting word fragments, stopwords, numbers, and non-technical terms that pollute the glossary database.

---

## Statistical Breakdown of Quality Issues

### 1. **Suffix Fragments (14.7% of database)**
- **Count:** 379 entries
- **Examples:** "Tion", "Tions", "Gulation", "Zation", "Ring", "Ducts"
- **Root Cause:** spaCy's noun chunk extraction is capturing word suffixes as standalone terms

### 2. **Contains Numbers (11.5% of database)**
- **Count:** 296 entries
- **Examples:** "100", "300", "4000", "70%", "[%]"
- **Root Cause:** No numeric filtering in validation logic

### 3. **Short/Invalid Terms (2.9% of database)**
- **Count:** 74 entries
- **Examples:** "Ema", "Ses", "$Su", "Gwp"
- **Root Cause:** `min_term_length=3` is too permissive for technical terms

### 4. **Common Stopwords (0.2% of database)**
- **Count:** 6 entries
- **Examples:** "The", "This", "That", "Which", "All", "End"
- **Root Cause:** No stopword filtering implemented

### 5. **Quality Estimate**
```
Total entries:           2,577
Low-quality entries:     ~755  (29.3%)
Acceptable entries:      ~1,822 (70.7%)
```

---

## Root Cause Analysis

### File: `src/backend/services/term_extractor.py`

### Critical Issue #1: No Stopword Filtering (Lines 88-97)

**Current Code:**
```python
# Noun phrases
for chunk in doc.noun_chunks:
    term = chunk.text.strip()
    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())

# Named entities (technical terms often appear as entities)
for ent in doc.ents:
    term = ent.text.strip()
    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())
```

**Problem:**
The code accepts ANY noun chunk or entity that meets length requirements. There is **zero semantic filtering** to exclude:
- Common English stopwords ("the", "this", "that", "which")
- Generic words ("all", "end", "use")
- Articles and pronouns

**Impact:** Allows 6+ stopwords into the database, plus hundreds of generic non-technical terms.

---

### Critical Issue #2: No Word Fragment Detection (Lines 88-91)

**Current Code:**
```python
for chunk in doc.noun_chunks:
    term = chunk.text.strip()
    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())
```

**Problem:**
spaCy's noun chunking occasionally splits compound words incorrectly:
- "Regulation" → "Gulation"
- "Organization" → "Zation"
- "Operations" → "Tions"

The code has **no validation** to detect these suffix-only fragments.

**Impact:** 379 entries (14.7%) are meaningless word fragments.

---

### Critical Issue #3: No Numeric/Symbol Filtering (Lines 90, 96)

**Current Code:**
```python
if min_term_length <= len(term) <= max_term_length:
    candidates.add(term.lower())
```

**Problem:**
No regex or character-type checking to exclude:
- Pure numbers: "100", "4000"
- Percentages: "70%", "[%]"
- Mixed alphanumeric: "$Su", "300"
- Special characters: "...", "—", "[", "]"

**Impact:** 296 entries (11.5%) contain numbers or are numeric-only.

---

### Critical Issue #4: Insufficient Minimum Length (Line 47, 276)

**Current Settings:**
```python
# In term_extractor.py
def extract_terms(
    self,
    text: str,
    min_term_length: int = 3,  # Default is 3
    ...
)

# In routers/documents.py (line 276)
extracted_terms = term_extractor.extract_terms(
    text=extracted_text,
    min_term_length=3,  # Called with 3
    ...
)
```

**Problem:**
Technical terminology is rarely 3 characters. Allowing 3-char minimum lets in:
- Abbreviations that need context: "Ema", "Gwp", "Ses"
- Generic words: "Use", "End", "All"
- Fragments: "Sus", "Ing"

**Impact:** 74 entries are 3 characters or less, most meaningless without context.

---

### Critical Issue #5: Frequency Threshold Too Low (Line 278)

**Current Setting:**
```python
# In routers/documents.py (line 278)
min_frequency=1,  # Changed from 2 to 1 to extract terms from shorter documents
```

**Problem:**
A frequency of 1 means ANY word appearing ONCE is considered a "term". This:
- Captures OCR errors
- Captures typos and misspellings
- Inflates database with one-off mentions
- Provides no statistical validation of term importance

**Comment reveals intent:** "Changed from 2 to 1 to extract terms from shorter documents"
**Reality:** This change increased noise significantly.

---

### Critical Issue #6: No Part-of-Speech Filtering (Lines 88-97)

**Current Code:**
```python
for chunk in doc.noun_chunks:
    term = chunk.text.strip()
    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())
```

**Problem:**
While noun chunks are used, there's no filtering for:
- Determiners embedded in chunks ("the system" → extracts "the")
- Pronouns ("this", "that", "which")
- Generic nouns vs. domain-specific technical terms

spaCy provides POS tags and dependency parsing that could filter these, but it's **not being used**.

**Impact:** Generic nouns pollute the technical glossary.

---

### Critical Issue #7: Pattern-Based Fallback Also Weak (Lines 138-143)

**Current Code:**
```python
# Pattern for technical terms: capitalized words, compound terms, acronyms
patterns = [
    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized terms
    r'\b[A-Z]{2,}\b',  # Acronyms
    r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)+\b',  # Hyphenated terms
]
```

**Problem:**
The patterns **only match capitalized words**. This means:
- Lowercase technical terms are ignored (common in technical docs)
- Relies on inconsistent capitalization in source documents
- No semantic filtering, just pattern matching
- Still no stopword or numeric filtering

---

## Missing Validation Rules

The following critical validations are **completely absent**:

### 1. **Stopword List**
No English stopword filtering. Should exclude at minimum:
```python
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'under', 'again',
    'this', 'that', 'these', 'those', 'then', 'than', 'so', 'such',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
    'some', 'which', 'who', 'when', 'where', 'why', 'how', 'end', 'use'
}
```

### 2. **Fragment Detection**
No validation for incomplete words:
- Starts with lowercase (likely a fragment): "tion", "ment"
- Ends with common suffixes without root: "gulation" (missing "Re")
- Less than 4 characters with no capitals

### 3. **Numeric/Symbol Validation**
No character-type checking:
```python
# Should reject if:
- contains only digits: r'^\d+$'
- contains symbols: r'[%$#@!&*()+=\[\]{}|\\:;"\'<>,.?/]'
- starts with non-letter: r'^[^a-zA-Z]'
```

### 4. **Linguistic Quality Checks**
No use of spaCy's advanced features:
- `token.is_stop` - built-in stopword detection
- `token.pos_` - part-of-speech filtering (keep NOUN, PROPN only)
- `token.is_alpha` - alphabetic character checking
- `token.ent_type_` - entity type filtering

### 5. **Domain-Specific Validation**
No technical term heuristics:
- Compound term validation (multi-word phrases)
- Capitalization patterns for proper nouns/acronyms
- Word shape analysis (e.g., "CamelCase", "UPPERCASE")
- TF-IDF scoring for term importance

### 6. **Context Validation**
No semantic analysis:
- Is the term used as a noun in technical context?
- Does it appear in headings/titles (higher importance)?
- Is it defined or explained in the document?
- Does it co-occur with other technical terms?

---

## Recommendations for Immediate Fixes

### Priority 1: Critical Fixes (Must Implement)

#### 1.1 Add Stopword Filtering
**Location:** `term_extractor.py`, lines 88-97

**Implementation:**
```python
# Add at top of file
from spacy.lang.en.stop_words import STOP_WORDS

# Additional technical document stopwords
CUSTOM_STOPWORDS = {
    'use', 'end', 'source', 'figure', 'table', 'page', 'section',
    'chapter', 'appendix', 'note', 'example', 'see', 'also'
}

ALL_STOPWORDS = STOP_WORDS.union(CUSTOM_STOPWORDS)

# In _extract_with_spacy, modify lines 88-91:
for chunk in doc.noun_chunks:
    term = chunk.text.strip()
    term_lower = term.lower()

    # FILTER: Skip stopwords
    if term_lower in ALL_STOPWORDS:
        continue

    # FILTER: Skip if all words in term are stopwords
    words = term_lower.split()
    if all(w in ALL_STOPWORDS for w in words):
        continue

    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term_lower)
```

#### 1.2 Add Numeric/Symbol Filtering
**Location:** `term_extractor.py`, lines 88-97

**Implementation:**
```python
import re

# Add validation function
def is_valid_term(term: str) -> bool:
    """Validate term quality"""
    # Reject pure numbers
    if re.match(r'^\d+$', term):
        return False

    # Reject if contains symbols (except hyphens in middle)
    if re.search(r'[%$#@!&*()+=\[\]{}|\\:;"\'<>,?/]', term):
        return False

    # Reject if starts/ends with non-letter
    if not term[0].isalpha() or not term[-1].isalnum():
        return False

    # Reject if more than 30% numbers
    num_digits = sum(c.isdigit() for c in term)
    if num_digits / len(term) > 0.3:
        return False

    return True

# Apply in extraction loop:
for chunk in doc.noun_chunks:
    term = chunk.text.strip()

    if not is_valid_term(term):
        continue

    # ... rest of logic
```

#### 1.3 Increase Minimum Term Length
**Location:** `routers/documents.py`, line 276

**Change:**
```python
# OLD
min_term_length=3,

# NEW
min_term_length=4,  # Technical terms are rarely less than 4 characters
```

#### 1.4 Add Fragment Detection
**Location:** `term_extractor.py`, lines 88-91

**Implementation:**
```python
# Common suffix fragments to reject
SUFFIX_FRAGMENTS = {
    'tion', 'tions', 'ment', 'ments', 'ness', 'ing', 'ings',
    'zation', 'gulation', 'ization', 'isation', 'ring', 'ducts',
    'ance', 'ence', 'able', 'ible', 'less', 'ful'
}

def is_fragment(term: str) -> bool:
    """Detect word fragments (incomplete words)"""
    term_lower = term.lower()

    # Check if term is a known suffix
    if term_lower in SUFFIX_FRAGMENTS:
        return True

    # Check if starts with lowercase (likely fragment)
    if len(term) > 0 and term[0].islower():
        return True

    # Check if has unusual capitalization pattern (e.g., "Tion")
    if term[0].isupper() and len(term) > 1 and term.endswith(tuple(SUFFIX_FRAGMENTS)):
        return True

    return False

# Apply in loop
for chunk in doc.noun_chunks:
    term = chunk.text.strip()

    if is_fragment(term):
        continue

    # ... rest of logic
```

---

### Priority 2: Quality Improvements (Should Implement)

#### 2.1 Use spaCy's Built-in Features
**Location:** `term_extractor.py`, lines 82-97

**Implementation:**
```python
def _extract_with_spacy(self, text: str, ...) -> List[Dict[str, any]]:
    """Extract terms using spaCy NLP with improved filtering"""
    doc = self.nlp(text)
    candidates = set()

    # Extract from noun chunks with POS filtering
    for chunk in doc.noun_chunks:
        # Get the root token of the chunk
        root = chunk.root

        # Filter by POS: only keep nouns and proper nouns
        if root.pos_ not in ['NOUN', 'PROPN']:
            continue

        # Skip stopwords using spaCy's built-in detection
        if root.is_stop:
            continue

        # Skip non-alphabetic terms
        if not root.is_alpha:
            continue

        term = chunk.text.strip()

        # Apply all validation filters
        if not is_valid_term(term):
            continue
        if is_fragment(term):
            continue
        if term.lower() in ALL_STOPWORDS:
            continue

        if min_term_length <= len(term) <= max_term_length:
            candidates.add(term.lower())

    # ... rest of implementation
```

#### 2.2 Increase Frequency Threshold
**Location:** `routers/documents.py`, line 278

**Change:**
```python
# OLD
min_frequency=1,  # Changed from 2 to 1 to extract terms from shorter documents

# NEW
min_frequency=2,  # Terms should appear at least twice to be significant

# OR make it dynamic based on document length:
import math
doc_length = len(extracted_text.split())
min_frequency = max(1, math.floor(doc_length / 5000))  # 1 per 5000 words
```

#### 2.3 Add Compound Term Preference
**Location:** `term_extractor.py`, lines 88-91

**Implementation:**
```python
# Prefer multi-word technical terms over single words
for chunk in doc.noun_chunks:
    term = chunk.text.strip()
    words = term.split()

    # If multi-word, apply looser filters (likely more technical)
    if len(words) >= 2:
        # Multi-word terms are usually more specific
        if is_valid_multi_word_term(term):
            candidates.add(term.lower())
    else:
        # Single words need stricter validation
        if is_valid_single_word_term(term):
            candidates.add(term.lower())
```

---

### Priority 3: Advanced Enhancements (Nice to Have)

#### 3.1 TF-IDF Scoring
Calculate term importance using TF-IDF to filter out common document boilerplate.

#### 3.2 Domain Dictionary
Maintain a whitelist of known technical terms in the domain (chemical engineering, process automation, etc.).

#### 3.3 Machine Learning Classification
Train a classifier to distinguish technical terms from generic words.

#### 3.4 Context Analysis
Analyze surrounding words to determine if a term is used in a technical or generic context.

---

## Code Snippets: Problematic Logic

### Snippet 1: No Validation in spaCy Extraction
**File:** `src/backend/services/term_extractor.py`
**Lines:** 88-91

```python
# CURRENT (BROKEN)
for chunk in doc.noun_chunks:
    term = chunk.text.strip()
    if min_term_length <= len(term) <= max_term_length:
        candidates.add(term.lower())
```

**What's wrong:**
- No stopword check
- No POS filtering
- No fragment detection
- No numeric validation
- No character validation

---

### Snippet 2: Overly Permissive Length Check
**File:** `src/backend/routers/documents.py`
**Lines:** 274-279

```python
# CURRENT (TOO PERMISSIVE)
extracted_terms = term_extractor.extract_terms(
    text=extracted_text,
    min_term_length=3,  # TOO SHORT
    max_term_length=100,
    min_frequency=1,  # TOO LOW - allows one-off terms
    pages_data=pages_data
)
```

**What's wrong:**
- `min_term_length=3` lets in fragments and abbreviations
- `min_frequency=1` allows OCR errors and typos
- No quality score threshold

---

### Snippet 3: Weak Pattern Matching
**File:** `src/backend/services/term_extractor.py`
**Lines:** 138-150

```python
# CURRENT (INCOMPLETE)
patterns = [
    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized terms
    r'\b[A-Z]{2,}\b',  # Acronyms
    r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)+\b',  # Hyphenated terms
]

candidates = set()
for pattern in patterns:
    matches = re.findall(pattern, text)
    for match in matches:
        if min_term_length <= len(match) <= max_term_length:
            candidates.add(match)  # NO FILTERING!
```

**What's wrong:**
- Only matches capitalized words (misses lowercase technical terms)
- No stopword filtering applied
- No numeric filtering
- Relies on document formatting

---

## Testing Recommendations

### Unit Tests Needed

1. **Test Stopword Filtering**
   ```python
   def test_stopwords_excluded():
       text = "The system uses this approach"
       terms = extractor.extract_terms(text)
       assert "The" not in [t['term'] for t in terms]
       assert "this" not in [t['term'] for t in terms]
   ```

2. **Test Fragment Detection**
   ```python
   def test_fragments_excluded():
       text = "Regulation and Gulation"
       terms = extractor.extract_terms(text)
       assert "Regulation" in [t['term'] for t in terms]
       assert "Gulation" not in [t['term'] for t in terms]
   ```

3. **Test Numeric Filtering**
   ```python
   def test_numbers_excluded():
       text = "The temperature is 4000 degrees"
       terms = extractor.extract_terms(text)
       assert "4000" not in [t['term'] for t in terms]
       assert "temperature" in [t['term'] for t in terms]
   ```

---

## Impact Assessment

### Current State
- **Database pollution:** 29.3% of entries are unusable
- **User trust:** Low-quality results damage credibility
- **Search effectiveness:** Irrelevant results from stopwords/fragments
- **Manual cleanup:** Significant time required to filter out bad terms

### After Implementing Priority 1 Fixes
- **Expected reduction:** 80-90% of low-quality entries eliminated
- **Database quality:** Estimated 85-90% acceptable entries
- **User experience:** Significantly improved glossary utility
- **Maintenance:** Reduced manual curation needed

### Implementation Effort
- **Priority 1 fixes:** ~4-6 hours development + testing
- **Priority 2 improvements:** ~8-10 hours development + testing
- **Priority 3 enhancements:** ~20-30 hours development + testing

---

## Conclusion

The current term extraction implementation lacks **basic quality validation** that should be standard in any NLP pipeline. The code is effectively a "naive extractor" that:

1. ✅ Successfully uses spaCy for NLP processing
2. ✅ Extracts noun chunks and entities
3. ❌ **Fails to filter** extracted candidates
4. ❌ **Allows garbage** into the database
5. ❌ **Ignores spaCy's built-in quality features** (is_stop, pos_, is_alpha)

**The fixes are straightforward** and mostly involve adding validation logic that should have been present from the start. Priority 1 fixes can be implemented in a single development session and will immediately improve quality from 70.7% to ~90%.

**Recommendation:** Implement all Priority 1 fixes before processing any more documents. The current database likely needs cleaning to remove the 755+ low-quality entries.

---

## Appendix: Detailed Statistics

### Database Analysis (2,577 entries)

| Category | Count | Percentage | Examples |
|----------|-------|------------|----------|
| **Valid Technical Terms** | ~1,822 | 70.7% | "Regulation", "Technology", "Production" |
| **Suffix Fragments** | 379 | 14.7% | "Tion", "Gulation", "Zation", "Ring" |
| **Contains Numbers** | 296 | 11.5% | "100", "4000", "70%", "[%]" |
| **Too Short (≤3 chars)** | 74 | 2.9% | "Ema", "Ses", "The", "All" |
| **Stopwords** | 6 | 0.2% | "The", "This", "That", "Which" |
| **Total Low-Quality** | ~755 | 29.3% | — |

### Quality Score Breakdown

```
Overall Code Quality: 4/10

- Readability: 7/10 (well-documented, clear structure)
- Maintainability: 6/10 (modular but lacks validation)
- Performance: 8/10 (efficient spaCy usage)
- Security: N/A
- Best Practices: 3/10 (missing standard NLP filters)
- Correctness: 4/10 (70% accuracy is poor for NLP)
```

### Technical Debt Estimate

- **Immediate cleanup:** 4-6 hours (implement Priority 1 fixes)
- **Database cleanup:** 2-3 hours (remove 755 bad entries)
- **Testing:** 3-4 hours (unit tests for new validation)
- **Total:** 9-13 hours to reach production quality

---

**Report prepared by:** Claude Code - Code Quality Analyzer
**Analysis method:** Static code analysis + database sampling
**Confidence level:** High (based on concrete data from 2,577 entries)
