# Linguistic Quality Improvements - Implementation Guide

## Executive Summary

This document provides **ready-to-implement** code for linguistic quality enhancements to the glossary extraction system, based on the comprehensive linguistic assessment.

**Quick Stats:**
- **Current Quality Score:** 42/100
- **Target Quality Score:** 85/100
- **Implementation Time:** 2-4 hours for Priority 1
- **Impact:** ~1,800 term improvements immediately

---

## Phase 1: Critical Fixes (Immediate - 2 hours)

### 1. Enhanced Term Validator with Linguistic Rules

**File:** `src/backend/services/term_validator.py`

Add these new validation methods to the `TermValidator` class:

```python
def _validate_no_article_prefix(self, term: str) -> Tuple[bool, str]:
    """Validate term doesn't start with an article"""
    ARTICLES = ['the', 'a', 'an']
    first_word = term.strip().lower().split()[0] if term.strip().split() else ''

    if first_word in ARTICLES:
        return False, f"Term starts with article '{first_word}' (should be removed)"

    return True, ""


def _validate_no_ocr_errors(self, term: str) -> Tuple[bool, str]:
    """Detect OCR duplication errors"""
    # Pattern: 3+ consecutive duplicate characters (e.g., 'Ssooddiiuumm')
    if re.search(r'([a-z])\1{2,}', term, re.IGNORECASE):
        return False, "OCR error detected (duplicate characters)"

    return True, ""


def _validate_no_sentence_fragment(self, term: str) -> Tuple[bool, str]:
    """Reject incomplete sentence fragments"""
    FRAGMENT_STARTERS = {
        'and', 'or', 'but', 'at', 'in', 'on', 'for',
        'with', 'from', 'by', 'to', 'into', 'through'
    }

    first_word = term.strip().lower().split()[0] if term.strip().split() else ''

    if first_word in FRAGMENT_STARTERS:
        return False, f"Incomplete fragment (starts with '{first_word}')"

    return True, ""


def _validate_no_morpheme_fragment(self, term: str) -> Tuple[bool, str]:
    """Reject standalone suffixes/prefixes"""
    SUFFIXES = {
        'tion', 'sion', 'ment', 'ness', 'ing', 'ed', 'ly',
        'er', 'est', 'ful', 'less', 'able', 'ible', 'ize',
        'ify', 'ous', 'ive', 'al', 'ance', 'ence', 'ity'
    }

    PREFIXES = {
        'un', 're', 'pre', 'dis', 'mis', 'non', 'anti',
        'de', 'over', 'under', 'sub', 'super', 'inter'
    }

    cleaned = term.lower().strip('-')

    if cleaned in SUFFIXES:
        return False, f"Standalone suffix '{cleaned}' (not a complete word)"

    if cleaned in PREFIXES:
        return False, f"Standalone prefix '{cleaned}' (not a complete word)"

    return True, ""


def _validate_no_generic_single_word(self, term: str) -> Tuple[bool, str]:
    """Reject overly generic single words"""
    GENERIC_WORDS = {
        'gas', 'air', 'end', 'day', 'time', 'way', 'thing',
        'part', 'use', 'case', 'type', 'kind', 'sort', 'tip',
        'bag', 'film', 'pea', 'res', 'tech', 'ions'
    }

    words = term.lower().strip().split()

    # Only apply to single-word terms
    if len(words) == 1 and words[0] in GENERIC_WORDS:
        return False, f"Too generic for technical glossary: '{words[0]}'"

    return True, ""


def _validate_no_math_notation(self, term: str) -> Tuple[bool, str]:
    """Reject pure mathematical notation"""
    MATH_SYMBOLS = '±×÷∑∏∫∂√Π≤≥≈≠'

    # Check if term contains math symbols
    has_math = any(sym in term for sym in MATH_SYMBOLS)

    if has_math:
        # Allow if it's part of a longer technical term (>10 chars)
        if len(term) < 10:
            return False, "Mathematical notation (not a glossary term)"

    return True, ""


def _validate_no_embedded_newlines(self, term: str) -> Tuple[bool, str]:
    """Reject terms with embedded newlines/tabs"""
    if '\n' in term or '\t' in term or '\r' in term:
        return False, "Term contains embedded newlines/tabs (formatting error)"

    return True, ""
```

### 2. Update Validator Constructor

Add these new validators to the validation chain:

```python
def is_valid_term(self, term: str) -> bool:
    """Check if a term is valid (ENHANCED VERSION)"""
    if not term or not isinstance(term, str):
        return False

    # Run all validation checks
    validators = [
        self._validate_length,
        self._validate_not_empty_or_whitespace,
        self._validate_no_embedded_newlines,      # NEW
        self._validate_no_ocr_errors,             # NEW
        self._validate_no_article_prefix,         # NEW
        self._validate_no_sentence_fragment,      # NEW
        self._validate_no_morpheme_fragment,      # NEW
        self._validate_not_pure_number,
        self._validate_not_percentage,
        self._validate_not_pure_symbols,
        self._validate_symbol_ratio,
        self._validate_no_math_notation,          # NEW
        self._validate_not_stop_word,
        self._validate_no_generic_single_word,    # NEW
        self._validate_word_count,
        self._validate_not_fragment,
        self._validate_capitalization,
    ]

    for validator in validators:
        is_valid, _ = validator(term)
        if not is_valid:
            return False

    return True
```

Update `get_rejection_reason()` and `validate_with_details()` similarly.

---

### 3. Term Pre-Processing Function

Add this utility function to clean terms BEFORE validation:

```python
def preprocess_term(term: str) -> str:
    """
    Pre-process term to normalize formatting and remove common issues

    Args:
        term: Raw extracted term

    Returns:
        Cleaned term ready for validation
    """
    # 1. Normalize whitespace (replace newlines, tabs, multiple spaces)
    term = term.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    term = re.sub(r'\s+', ' ', term)

    # 2. Strip leading/trailing whitespace
    term = term.strip()

    # 3. Remove leading articles
    term = re.sub(r'^(The|the|A|a|An|an)\s+', '', term)

    # 4. Remove trailing/leading hyphens (fragments)
    term = term.strip('-')

    # 5. Final cleanup
    term = term.strip()

    return term
```

**Usage in `term_extractor.py`:**

```python
# In _extract_with_spacy() and _extract_with_patterns()
for term in candidates:
    # PRE-PROCESS before validation
    cleaned_term = preprocess_term(term)

    if not cleaned_term:
        continue

    count = text.count(cleaned_term)

    if count >= min_frequency:
        if enable_validation:
            if self.validator.is_valid_term(cleaned_term):
                term_freq[cleaned_term] = count
            else:
                rejected_count += 1
                rejection_reasons[cleaned_term] = self.validator.get_rejection_reason(cleaned_term)
        else:
            term_freq[cleaned_term] = count
```

---

### 4. Database Cleanup Script

**File:** `src/backend/scripts/cleanup_glossary.py` (NEW FILE)

```python
"""
Database Cleanup Script
Removes low-quality terms based on enhanced linguistic validation
"""
import sqlite3
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.term_validator import TermValidator, ValidationConfig, create_default_validator
from services.term_extractor import preprocess_term

def cleanup_database(db_path: str = "data/glossary.db", dry_run: bool = True):
    """
    Clean up low-quality terms from database

    Args:
        db_path: Path to SQLite database
        dry_run: If True, only report what would be deleted (don't actually delete)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all entries
    cursor.execute("SELECT id, term FROM glossary_entries")
    all_entries = cursor.fetchall()

    validator = create_default_validator("en")

    to_delete = []
    to_update = []
    stats = {
        'total': len(all_entries),
        'invalid': 0,
        'updated': 0,
        'deleted': 0,
        'valid': 0,
        'rejection_reasons': {}
    }

    print(f"Analyzing {stats['total']} terms...")
    print()

    for entry_id, term in all_entries:
        # Pre-process term
        cleaned_term = preprocess_term(term)

        # Check if pre-processing changed the term
        if cleaned_term != term:
            # Term can be updated
            if cleaned_term and validator.is_valid_term(cleaned_term):
                to_update.append((entry_id, term, cleaned_term))
                stats['updated'] += 1
            else:
                # Even after cleaning, term is invalid
                reason = validator.get_rejection_reason(cleaned_term) if cleaned_term else "Empty after cleaning"
                to_delete.append((entry_id, term, reason))
                stats['invalid'] += 1
                stats['rejection_reasons'][reason] = stats['rejection_reasons'].get(reason, 0) + 1
        else:
            # Term unchanged by pre-processing, validate as-is
            if validator.is_valid_term(term):
                stats['valid'] += 1
            else:
                reason = validator.get_rejection_reason(term)
                to_delete.append((entry_id, term, reason))
                stats['invalid'] += 1
                stats['rejection_reasons'][reason] = stats['rejection_reasons'].get(reason, 0) + 1

    # Print report
    print("=" * 80)
    print("CLEANUP ANALYSIS REPORT")
    print("=" * 80)
    print()
    print(f"Total Terms: {stats['total']}")
    print(f"Valid Terms: {stats['valid']} ({stats['valid']/stats['total']*100:.1f}%)")
    print(f"Terms to Update: {stats['updated']} ({stats['updated']/stats['total']*100:.1f}%)")
    print(f"Terms to Delete: {stats['invalid']} ({stats['invalid']/stats['total']*100:.1f}%)")
    print()

    print("REJECTION REASONS:")
    for reason, count in sorted(stats['rejection_reasons'].items(), key=lambda x: -x[1]):
        print(f"  - {reason}: {count}")
    print()

    # Sample deletions
    print("SAMPLE DELETIONS (first 20):")
    for i, (entry_id, term, reason) in enumerate(to_delete[:20], 1):
        print(f"  {i}. [{entry_id}] '{term[:60]}' - {reason}")
    print()

    # Sample updates
    print("SAMPLE UPDATES (first 20):")
    for i, (entry_id, old_term, new_term) in enumerate(to_update[:20], 1):
        print(f"  {i}. [{entry_id}] '{old_term[:40]}' → '{new_term[:40]}'")
    print()

    if dry_run:
        print("=" * 80)
        print("DRY RUN MODE - No changes made to database")
        print("Run with dry_run=False to apply changes")
        print("=" * 80)
    else:
        # Apply updates
        print("Applying updates...")
        for entry_id, old_term, new_term in to_update:
            cursor.execute("UPDATE glossary_entries SET term = ? WHERE id = ?", (new_term, entry_id))
        stats['deleted'] = stats['updated']

        # Apply deletions
        print("Applying deletions...")
        for entry_id, term, reason in to_delete:
            cursor.execute("DELETE FROM glossary_entries WHERE id = ?", (entry_id,))
        stats['deleted'] += stats['invalid']

        conn.commit()
        print(f"✓ Updated {stats['updated']} terms")
        print(f"✓ Deleted {stats['invalid']} invalid terms")
        print(f"✓ Total changes: {stats['deleted']}")

    conn.close()

    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean up glossary database")
    parser.add_argument("--db", default="data/glossary.db", help="Database path")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default is dry-run)")

    args = parser.parse_args()

    cleanup_database(args.db, dry_run=not args.execute)
```

**Usage:**
```bash
# Dry run (report only)
python src/backend/scripts/cleanup_glossary.py

# Actually execute cleanup
python src/backend/scripts/cleanup_glossary.py --execute
```

---

## Phase 2: Definition Quality (Short-term - 4 hours)

### 5. Enhanced Definition Generation

**File:** `src/backend/services/term_extractor.py`

Replace the current `generate_definition()` method:

```python
def generate_definition(
    self,
    term: str,
    context: str,
    complete_sentence: str = "",
    page_numbers: Optional[List[int]] = None
) -> str:
    """
    Generate a basic definition from context (ENHANCED VERSION)

    Args:
        term: The term to define
        context: Context where term appears
        complete_sentence: Complete sentence containing the term
        page_numbers: List of page numbers where term appears

    Returns:
        Generated definition
    """
    # Build page number text
    page_text = ""
    if page_numbers and len(page_numbers) > 0:
        if len(page_numbers) == 1:
            page_text = f" (Page {page_numbers[0]})"
        elif len(page_numbers) <= 3:
            page_text = f" (Pages {', '.join(map(str, page_numbers))})"
        else:
            page_text = f" (Pages {', '.join(map(str, page_numbers[:3]))}, +{len(page_numbers) - 3} more)"

    # Enhanced: Try to extract a better definition
    definition = self._extract_best_definition(term, complete_sentence, context)

    if definition:
        return f"{definition}{page_text}"
    else:
        # Fallback to context-based
        if complete_sentence:
            return f"Term found in context{page_text}:\n\n{complete_sentence}"
        elif context:
            return f"Term found in context{page_text}:\n\n{context[:250]}"
        else:
            return f"Technical term: {term}"


def _extract_best_definition(
    self,
    term: str,
    complete_sentence: str,
    context: str
) -> Optional[str]:
    """
    Extract the best possible definition from available text

    Args:
        term: The term to define
        complete_sentence: Complete sentence containing term
        context: Context excerpt

    Returns:
        Best definition found, or None
    """
    # Look for definition patterns in sentence
    if complete_sentence:
        sentence = complete_sentence.strip()

        # Pattern 1: "Term is [definition]"
        pattern1 = rf"{re.escape(term)}\s+is\s+(.+?)[\.\!\?]"
        match = re.search(pattern1, sentence, re.IGNORECASE)
        if match:
            definition = match.group(1).strip()
            if len(definition) > 10:  # Ensure meaningful definition
                return f"{term} is {definition}."

        # Pattern 2: "Term: [definition]"
        pattern2 = rf"{re.escape(term)}\s*:\s*(.+?)[\.\!\?]"
        match = re.search(pattern2, sentence, re.IGNORECASE)
        if match:
            definition = match.group(1).strip()
            if len(definition) > 10:
                return f"{term}: {definition}."

        # Pattern 3: "Term, [definition],"
        pattern3 = rf"{re.escape(term)},\s+(.+?),"
        match = re.search(pattern3, sentence, re.IGNORECASE)
        if match:
            definition = match.group(1).strip()
            if len(definition) > 10:
                return f"{term}, {definition}."

        # Pattern 4: "[definition] called/known as Term"
        pattern4 = rf"(.+?)\s+(?:called|known as|referred to as)\s+{re.escape(term)}"
        match = re.search(pattern4, sentence, re.IGNORECASE)
        if match:
            definition = match.group(1).strip()
            if len(definition) > 10:
                return f"{term} is {definition}."

    # No pattern matched, return None (will use fallback)
    return None
```

---

## Phase 3: AI-Enhanced Definitions (Optional - 2 hours)

### 6. GPT-Based Definition Generator (Optional)

**File:** `src/backend/services/ai_definition_generator.py` (NEW FILE)

```python
"""
AI-Based Definition Generator
Uses OpenAI GPT or Anthropic Claude to generate professional definitions
"""
import os
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Optional: requires openai or anthropic package
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for AI definitions")


class AIDefinitionGenerator:
    """Generate professional glossary definitions using AI"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI definition generator

        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
            logger.info("AI definition generator initialized")
        else:
            logger.warning("AI definitions not available (missing API key or package)")

    def generate_definition(
        self,
        term: str,
        contexts: List[str],
        domain: str = "engineering"
    ) -> Optional[str]:
        """
        Generate a professional definition using AI

        Args:
            term: The term to define
            contexts: List of context sentences where term appears
            domain: Technical domain (e.g., "engineering", "biotechnology")

        Returns:
            AI-generated definition, or None if unavailable
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            return None

        try:
            # Build prompt
            prompt = self._build_prompt(term, contexts, domain)

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" for better quality
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical glossary expert. Generate concise, accurate definitions for technical terms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3  # Lower temperature for factual definitions
            )

            definition = response.choices[0].message.content.strip()
            return definition

        except Exception as e:
            logger.error(f"AI definition generation failed: {e}")
            return None

    def _build_prompt(self, term: str, contexts: List[str], domain: str) -> str:
        """Build prompt for AI definition generation"""
        # Limit to 3 most relevant contexts
        context_text = "\n".join([f"- {ctx[:200]}" for ctx in contexts[:3]])

        prompt = f"""Based on these contexts where '{term}' appears in {domain} documentation:

{context_text}

Generate a concise, professional glossary definition for '{term}'.

Requirements:
- Use format: "{term} is [genus] that [differentia]."
- 1-2 complete sentences maximum
- Technically accurate
- Clear and professional
- Suitable for an engineering glossary
- No marketing language or fluff

Definition:"""

        return prompt
```

**Integration in `term_extractor.py`:**

```python
from .ai_definition_generator import AIDefinitionGenerator

class TermExtractor:
    def __init__(self, language: str = "en", validator: Optional[TermValidator] = None):
        # ... existing code ...
        self.ai_generator = AIDefinitionGenerator()  # Optional

    def generate_definition(self, term: str, context: str, complete_sentence: str = "",
                           page_numbers: Optional[List[int]] = None,
                           use_ai: bool = False) -> str:
        """Generate definition with optional AI enhancement"""

        # Try AI generation first if enabled
        if use_ai and self.ai_generator:
            contexts = [complete_sentence] if complete_sentence else [context]
            ai_def = self.ai_generator.generate_definition(term, contexts)
            if ai_def:
                return ai_def

        # Fallback to existing logic
        # ... (existing code)
```

---

## Testing & Validation

### 7. Unit Tests

**File:** `tests/unit/test_term_validator_enhanced.py` (NEW FILE)

```python
"""
Unit tests for enhanced term validation
"""
import pytest
from src.backend.services.term_validator import TermValidator, ValidationConfig
from src.backend.services.term_extractor import preprocess_term


class TestEnhancedValidation:
    """Test enhanced validation rules"""

    @pytest.fixture
    def validator(self):
        return TermValidator(ValidationConfig())

    def test_article_prefix_rejection(self, validator):
        """Test that article-prefixed terms are rejected"""
        assert not validator.is_valid_term("The Mixing Time")
        assert not validator.is_valid_term("A Bioreactor")
        assert not validator.is_valid_term("An Example")

    def test_ocr_error_rejection(self, validator):
        """Test OCR error detection"""
        assert not validator.is_valid_term("Ssooddiiuumm")
        assert not validator.is_valid_term("Pplloottttiinngg")
        assert not validator.is_valid_term("Aaddddiittiioonn")

    def test_fragment_rejection(self, validator):
        """Test sentence fragment rejection"""
        assert not validator.is_valid_term("And Then The Measurements")
        assert not validator.is_valid_term("At Least 6")
        assert not validator.is_valid_term("In Order To")

    def test_morpheme_rejection(self, validator):
        """Test suffix/prefix rejection"""
        assert not validator.is_valid_term("Ing")
        assert not validator.is_valid_term("Tion")
        assert not validator.is_valid_term("Pre")

    def test_newline_rejection(self, validator):
        """Test embedded newline rejection"""
        assert not validator.is_valid_term("L\nP")
        assert not validator.is_valid_term("Power\nInput")

    def test_valid_terms_acceptance(self, validator):
        """Test that valid terms are accepted"""
        assert validator.is_valid_term("Pressure Transmitter")
        assert validator.is_valid_term("Bioreactor")
        assert validator.is_valid_term("Volumetric Mass Transfer")
        assert validator.is_valid_term("API")
        assert validator.is_valid_term("Single-Use Technology")

    def test_preprocessing(self):
        """Test term preprocessing"""
        assert preprocess_term("The Mixing Time") == "Mixing Time"
        assert preprocess_term("L\nP") == "L P"
        assert preprocess_term("  A  Sensor  ") == "Sensor"
        assert preprocess_term("-Fragment-") == "Fragment"


class TestDefinitionExtraction:
    """Test enhanced definition extraction"""

    def test_is_pattern_extraction(self):
        """Test 'is' pattern extraction"""
        from src.backend.services.term_extractor import TermExtractor
        extractor = TermExtractor()

        sentence = "A bioreactor is a vessel used to grow cells or organisms."
        definition = extractor._extract_best_definition("bioreactor", sentence, "")

        assert definition is not None
        assert "is a vessel" in definition.lower()
```

---

## Deployment Checklist

### Before Deployment

- [ ] Back up current database: `data/glossary.db`
- [ ] Run unit tests: `pytest tests/unit/test_term_validator_enhanced.py`
- [ ] Run cleanup script in dry-run mode
- [ ] Review sample deletions/updates
- [ ] Get approval for changes

### Deployment Steps

1. **Deploy code changes:**
   ```bash
   # Update validator
   git add src/backend/services/term_validator.py
   # Add cleanup script
   git add src/backend/scripts/cleanup_glossary.py
   # Update extractor
   git add src/backend/services/term_extractor.py
   git commit -m "Add enhanced linguistic validation"
   ```

2. **Run database cleanup:**
   ```bash
   # Dry run first
   python src/backend/scripts/cleanup_glossary.py

   # Review output, then execute
   python src/backend/scripts/cleanup_glossary.py --execute
   ```

3. **Verify results:**
   ```bash
   # Check term count
   sqlite3 data/glossary.db "SELECT COUNT(*) FROM glossary_entries"

   # Sample remaining terms
   sqlite3 data/glossary.db "SELECT term FROM glossary_entries ORDER BY RANDOM() LIMIT 20"
   ```

4. **Re-process documents (optional):**
   - Upload PDFs again with new validation
   - Compare old vs new extraction quality

### Post-Deployment

- [ ] Monitor error logs for validation issues
- [ ] Collect user feedback on glossary quality
- [ ] Track linguistic quality metrics
- [ ] Plan Phase 2 (AI definitions) if approved

---

## Expected Results

### Before Enhancements
```
Total Terms: 4,511
Valid Quality: 1,971 (43.7%)
Article Prefix: 1,197 (26.5%)
OCR Errors: 22 (0.5%)
Formatting Errors: 682 (15.1%)
Fragments: 14 (0.3%)
```

### After Phase 1 (Critical Fixes)
```
Total Terms: ~2,600 (42% reduction)
Valid Quality: ~2,200 (85%+)
Article Prefix: 0 (100% removed)
OCR Errors: 0 (100% removed)
Formatting Errors: 0 (100% cleaned)
Fragments: 0 (100% rejected)
```

### Quality Score Improvement
```
Before: 42/100
After Phase 1: 72/100
After Phase 2: 85/100
```

---

## Maintenance & Future Work

### Continuous Improvement

1. **Regular Quality Audits**
   - Run cleanup script monthly
   - Review rejection logs
   - Update blacklists as needed

2. **User Feedback Loop**
   - Collect feedback on definition quality
   - Manual corrections feed back into AI training
   - Build domain-specific term databases

3. **AI Enhancement (Phase 2)**
   - Implement GPT-based definition generation
   - Quality scoring system
   - A/B testing for definition quality

4. **Domain Expansion**
   - Build biotechnology term database
   - Engineering standards integration
   - Multi-language support (German)

---

## Support & Questions

For questions or issues with implementation:

1. Review the main linguistic assessment: `docs/LINGUISTIC_QUALITY_ASSESSMENT.md`
2. Check unit tests for examples: `tests/unit/test_term_validator_enhanced.py`
3. Review validation logs for debugging
4. Contact development team

---

**Document Version:** 1.0
**Last Updated:** 2025-10-18
**Status:** Ready for Implementation
