# Technical Term Extraction: NLP Best Practices & Implementation Guide

## Executive Summary

This document provides research-based recommendations for extracting high-quality technical terms from English and German technical documentation. Based on recent academic research (2024-2025) and industry best practices, this guide addresses filtering criteria, validation rules, and implementation strategies for the Glossary APP.

**Current Implementation Status:**
- Uses spaCy for NLP-based extraction with fallback to pattern matching
- Extracts noun chunks and named entities
- Basic frequency filtering (min_frequency=2)
- Length filtering (min_term_length=3, max_term_length=50)

**Recommended Improvements:**
1. Enhanced filtering with POS tagging
2. Domain-specific technical stopwords
3. Improved single-character and number handling
4. Better compound term validation
5. Acronym detection and validation

---

## 1. What Makes a Good Technical Term vs. Noise?

### 1.1 Characteristics of Valid Technical Terms

**Good Technical Terms:**
- **Noun-centric**: Technical terms are predominantly nouns or noun phrases
- **Domain-specific**: Appear more frequently in technical texts than general language
- **Meaningful**: Convey specific technical concepts, processes, or entities
- **Consistent**: Used consistently throughout the document
- **Complete units**: Represent complete semantic concepts, not fragments

**Examples:**
```
GOOD TERMS:
- "control valve"
- "pressure transmitter"
- "API endpoint"
- "SQL injection"
- "PID controller"
- "ISO 9001"

BAD TERMS (Noise):
- "the system" (too generic + article)
- "very important" (adjective phrase, not a term)
- "etc." (abbreviation without meaning)
- "page 5" (reference, not a term)
- "see above" (navigational text)
```

### 1.2 Noise Patterns to Filter

**Systematic Noise Sources:**
1. **Generic phrases**: "the following", "as mentioned", "for example"
2. **Document structure**: "Chapter 3", "Section 2.1", "Figure 5"
3. **Incomplete fragments**: Single prepositions, articles, conjunctions
4. **Overly generic nouns**: "thing", "item", "stuff", "system" (when used alone)
5. **Meta-references**: "this document", "above table", "see page"

---

## 2. Industry-Standard Filtering Criteria

### 2.1 Length-Based Filtering

**Character Length:**
```python
MIN_TERM_LENGTH = 2  # Changed from 3 to include "ID", "IO"
MAX_TERM_LENGTH = 50  # Reasonable for compound technical terms
```

**Rationale:**
- Minimum of 2 characters allows valid 2-letter acronyms (IO, ID, OS, AI)
- Maximum of 50 characters prevents extraction of entire sentences
- Research shows n-grams with n ≤ 6 words are most effective

**Word Count Filtering:**
```python
MIN_WORD_COUNT = 1   # Allow single-word technical terms
MAX_WORD_COUNT = 5   # Limit compound terms to 5 words
```

**Rationale:**
- Single technical terms like "sensor", "valve", "compiler" are valid
- Terms beyond 5 words are usually full phrases, not terms
- Research: 80% of technical terms are 1-3 words long

### 2.2 Frequency-Based Filtering

**Adaptive Frequency Thresholds:**

```python
def calculate_min_frequency(document_size: int) -> int:
    """
    Calculate minimum frequency based on document size

    Research basis: Frequency thresholds should scale with corpus size
    """
    if document_size < 1000:      # Short documents (< 1 page)
        return 1  # Keep single occurrences
    elif document_size < 5000:    # Medium documents (1-5 pages)
        return 2  # Require at least 2 occurrences
    elif document_size < 20000:   # Long documents (5-20 pages)
        return 3  # Require at least 3 occurrences
    else:                         # Very long documents (> 20 pages)
        return 4  # Require at least 4 occurrences
```

**Rationale:**
- Short documents: Single occurrence may be significant (e.g., key specification)
- Long documents: Higher threshold reduces noise from casual mentions
- Research shows exponential decrease in term occurrences with corpus size

### 2.3 Statistical Quality Measures

**TF-IDF Scoring (Recommended Addition):**
```python
def calculate_term_quality_score(
    term: str,
    frequency: int,
    document_freq: int,
    total_documents: int
) -> float:
    """
    Calculate quality score combining multiple factors

    Returns score 0.0-1.0, higher = better quality term
    """
    # TF-IDF component
    tf = frequency
    idf = log(total_documents / (1 + document_freq))
    tfidf_score = tf * idf

    # Length bonus (2-4 words are optimal)
    word_count = len(term.split())
    length_score = 1.0 if 2 <= word_count <= 4 else 0.7

    # Capitalization bonus (indicates proper nouns/acronyms)
    cap_score = 1.2 if term[0].isupper() else 1.0

    # Combined score
    return min(1.0, (tfidf_score * length_score * cap_score) / 10)
```

---

## 3. Stop Word Lists for Technical Documentation

### 3.1 Standard Stop Words (Base List)

**Generic English Stop Words:**
```python
GENERIC_STOPWORDS = {
    # Articles
    "a", "an", "the",

    # Pronouns
    "i", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them",
    "my", "your", "his", "her", "its", "our", "their",
    "this", "that", "these", "those",

    # Prepositions
    "in", "on", "at", "to", "for", "of", "with", "from",
    "by", "about", "as", "into", "through", "over",

    # Conjunctions
    "and", "or", "but", "if", "because", "while", "although",

    # Common verbs
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might",

    # Adverbs
    "very", "really", "quite", "rather", "too", "also",
    "just", "only", "even", "still", "already",
}
```

### 3.2 Technical Documentation Stop Words

**Domain-Specific Technical Stop Words:**
Based on research from "Stopwords in Technical Language Processing" (PLOS One, 2021)

```python
TECHNICAL_STOPWORDS = {
    # Document structure
    "section", "chapter", "page", "figure", "table", "appendix",
    "part", "paragraph", "clause", "subsection",

    # Meta-references
    "above", "below", "following", "previous", "next",
    "herein", "thereof", "whereby", "wherein",

    # Generic technical terms (too broad)
    "system", "method", "device", "apparatus", "means",
    "process", "mechanism", "structure", "component" (when alone),

    # Measurement units (should be extracted separately)
    "mm", "cm", "kg", "lb", "psi", "bar" (when alone without number),

    # Vague quantifiers
    "some", "any", "each", "every", "all", "both", "few", "many",
    "several", "various", "certain", "such",

    # Deictic expressions
    "here", "there", "where", "when", "how", "why",

    # Generic actions
    "use", "using", "used", "see", "refer", "according",
    "include", "including", "included", "comprise", "consist",
}
```

### 3.3 Engineering-Specific Stop Words

```python
ENGINEERING_STOPWORDS = {
    # Process indicators (too generic alone)
    "step", "stage", "phase", "operation", "procedure",

    # Generic descriptions
    "type", "kind", "sort", "example", "instance",
    "way", "manner", "form", "case",

    # Comparative/qualitative
    "high", "low", "good", "bad", "better", "worse",
    "small", "large", "big", "little" (when alone),

    # Temporal
    "time", "period", "duration", "interval" (when alone),

    # Result indicators
    "result", "outcome", "effect", "impact",
}
```

### 3.4 Combined Stop Word Strategy

```python
# Combine all stop word lists
ALL_STOPWORDS = GENERIC_STOPWORDS | TECHNICAL_STOPWORDS | ENGINEERING_STOPWORDS

def is_stopword(term: str, stopwords: set = ALL_STOPWORDS) -> bool:
    """
    Check if term is a stop word

    Special rules:
    - Multi-word terms: check if ALL words are stopwords
    - Single words: direct lookup
    """
    term_lower = term.lower().strip()
    words = term_lower.split()

    # Single word: direct check
    if len(words) == 1:
        return term_lower in stopwords

    # Multi-word: accept if at least one word is NOT a stopword
    return all(word in stopwords for word in words)
```

---

## 4. Part-of-Speech (POS) Tagging Strategies

### 4.1 Valid POS Patterns for Technical Terms

**Recommended POS Patterns:**

```python
VALID_TERM_PATTERNS = {
    # Single nouns
    "NOUN": True,
    "PROPN": True,  # Proper nouns (e.g., "Siemens", "ISO")

    # Noun phrases (most common)
    "ADJ NOUN": True,          # e.g., "analog input"
    "NOUN NOUN": True,         # e.g., "pressure sensor"
    "ADJ NOUN NOUN": True,     # e.g., "digital pressure sensor"
    "NOUN NOUN NOUN": True,    # e.g., "safety relief valve"

    # With prepositions (less common but valid)
    "NOUN ADP NOUN": True,     # e.g., "point of sale"

    # Compound terms
    "NOUN PUNCT NOUN": True,   # e.g., "client-server"

    # Acronyms and abbreviations
    "X": True,  # spaCy marks unknown tokens/acronyms as X
}

INVALID_TERM_PATTERNS = {
    # Pure verb phrases
    "VERB": False,
    "VERB NOUN": False,

    # Pure adjectives/adverbs
    "ADJ": False,
    "ADV": False,

    # Determiners + noun (too generic)
    "DET NOUN": False,  # e.g., "the system"

    # Pronouns
    "PRON": False,
}
```

### 4.2 Implementation with spaCy

```python
def validate_term_pos(term: str, nlp) -> bool:
    """
    Validate term using POS tagging

    Args:
        term: Candidate term to validate
        nlp: spaCy language model

    Returns:
        True if POS pattern is valid for technical term
    """
    doc = nlp(term)

    # Extract POS pattern
    pos_pattern = " ".join([token.pos_ for token in doc])

    # Check against valid patterns
    if pos_pattern in VALID_TERM_PATTERNS:
        return True

    # Check if matches invalid patterns
    if pos_pattern in INVALID_TERM_PATTERNS:
        return False

    # Default: Accept if contains at least one noun
    has_noun = any(token.pos_ in ["NOUN", "PROPN"] for token in doc)
    has_verb_only = all(token.pos_ in ["VERB", "AUX"] for token in doc)

    return has_noun and not has_verb_only
```

### 4.3 Advanced: Dependency Parsing

```python
def extract_compound_terms(doc) -> List[str]:
    """
    Extract compound terms using dependency parsing

    Targets noun compounds and modifier relationships
    """
    compounds = []

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            # Find all modifiers and compounds
            modifiers = []

            # Get compounds (noun + noun)
            for child in token.children:
                if child.dep_ == "compound":
                    modifiers.append(child)

            # Get adjective modifiers
            for child in token.children:
                if child.dep_ == "amod" and child.pos_ == "ADJ":
                    modifiers.append(child)

            # Build compound term
            if modifiers:
                term_parts = sorted(modifiers, key=lambda x: x.i)
                term_parts.append(token)
                compound = " ".join([t.text for t in term_parts])
                compounds.append(compound)

    return compounds
```

---

## 5. Minimum Viable Term Characteristics

### 5.1 Validation Checklist

```python
def is_valid_technical_term(
    term: str,
    frequency: int,
    context: str,
    nlp=None
) -> Tuple[bool, str]:
    """
    Comprehensive term validation

    Returns:
        (is_valid, rejection_reason)
    """
    term_clean = term.strip()

    # 1. Length validation
    if len(term_clean) < 2:
        return False, "Too short (< 2 characters)"

    if len(term_clean) > 50:
        return False, "Too long (> 50 characters)"

    # 2. Word count validation
    word_count = len(term_clean.split())
    if word_count > 5:
        return False, "Too many words (> 5)"

    # 3. Stop word validation
    if is_stopword(term_clean):
        return False, "Stop word or generic phrase"

    # 4. Single character validation (special rules)
    if len(term_clean) == 1:
        # Only allow uppercase letters (abbreviations)
        if term_clean.isupper() and term_clean.isalpha():
            return True, ""
        return False, "Single character (not valid abbreviation)"

    # 5. Numbers validation (see section 5.3)
    if term_clean.replace(".", "").replace("%", "").isdigit():
        return False, "Pure number (extract as data, not term)"

    # 6. Capitalization patterns (see section 5.2)
    if not has_valid_capitalization(term_clean):
        return False, "Invalid capitalization pattern"

    # 7. POS validation (if NLP available)
    if nlp and not validate_term_pos(term_clean, nlp):
        return False, "Invalid POS pattern"

    # 8. Contains at least one alphabetic character
    if not any(c.isalpha() for c in term_clean):
        return False, "No alphabetic characters"

    return True, ""
```

### 5.2 Capitalization Pattern Validation

```python
def has_valid_capitalization(term: str) -> bool:
    """
    Validate capitalization patterns

    Valid patterns:
    - Title Case: "Control Valve"
    - All Caps: "API" (acronyms)
    - Sentence case: "pressure sensor" (extracted from text)
    - Mixed: "pH sensor" (domain conventions)

    Invalid patterns:
    - rAnDoM CaSe: "pReSsUrE sEnSoR"
    """
    words = term.split()

    for word in words:
        # Skip very short words (articles, prepositions)
        if len(word) <= 2:
            continue

        # Check if all lowercase (acceptable)
        if word.islower():
            continue

        # Check if all uppercase (acronym - acceptable)
        if word.isupper():
            continue

        # Check if title case (acceptable)
        if word[0].isupper() and word[1:].islower():
            continue

        # Check for known patterns (pH, eLearning, etc.)
        if word.lower() in ["ph", "elearning", "iot", "ios"]:
            continue

        # Mixed case within word (suspicious)
        has_upper = any(c.isupper() for c in word[1:])
        has_lower = any(c.islower() for c in word[1:])
        if has_upper and has_lower:
            # Could be camelCase or acronym combo (e.g., "JSONParser")
            # Accept if starts with uppercase
            if word[0].isupper():
                continue
            return False

    return True
```

### 5.3 Number and Percentage Handling

**Decision Matrix:**

| Pattern | Example | Valid Term? | Reason |
|---------|---------|-------------|---------|
| Pure number | "100" | NO | Extract as data point, not term |
| Number + unit | "100 psi" | YES | Technical measurement |
| Percentage alone | "95%" | NO | Extract as data point |
| Term + number | "Stage 2" | YES | Named component/phase |
| Model number | "Model X-500" | YES | Product identifier |
| Standard number | "ISO 9001" | YES | Standard reference |
| Version number | "Version 2.5" | MAYBE | Context-dependent |

```python
def should_extract_numeric_term(term: str) -> bool:
    """
    Determine if numeric-containing term should be extracted
    """
    # Pure number or percentage: NO
    if re.match(r'^\d+\.?\d*%?$', term):
        return False

    # Standard numbers (ISO, DIN, ASME, etc.): YES
    if re.match(r'^(ISO|DIN|ASME|IEC|ANSI|EN)\s+\d+', term, re.IGNORECASE):
        return True

    # Model numbers: YES
    if re.match(r'^(Model|Type|Series)\s+[A-Z0-9\-]+', term, re.IGNORECASE):
        return True

    # Measurement with unit: YES
    if re.match(r'^\d+\.?\d*\s*(psi|bar|mm|cm|kg|lb|mph|kph)', term, re.IGNORECASE):
        return True

    # Version numbers: NO (usually metadata, not terms)
    if re.match(r'^(Version|Ver\.?|v\.?)\s*\d', term, re.IGNORECASE):
        return False

    # Mixed alphanumeric (likely product code): YES
    alpha_count = sum(c.isalpha() for c in term)
    digit_count = sum(c.isdigit() for c in term)
    if alpha_count >= 2 and digit_count >= 1:
        return True

    return False
```

---

## 6. Compound Terms vs. Fragments

### 6.1 Identifying Complete Compound Terms

**Valid Compound Term Patterns:**

```python
COMPOUND_PATTERNS = {
    # Noun compounds (most common in technical docs)
    "noun_noun": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # "Control Valve"

    # Adjective + noun
    "adj_noun": r'\b[A-Z][a-z]+\s+[A-Z]?[a-z]+\b',  # "Digital Signal"

    # Hyphenated compounds
    "hyphenated": r'\b[A-Z][a-z]+-[A-Z]?[a-z]+\b',  # "Client-Server"

    # Three-word compounds
    "three_word": r'\b[A-Z][a-z]+\s+[A-Z]?[a-z]+\s+[A-Z]?[a-z]+\b',

    # Acronym compounds
    "acronym_compound": r'\b[A-Z]{2,}\s+[A-Z][a-z]+\b',  # "API Gateway"
}
```

### 6.2 Detecting Fragments (Anti-patterns)

```python
def is_fragment(term: str, full_text: str) -> bool:
    """
    Detect if term is a fragment of a larger compound

    Args:
        term: Candidate term
        full_text: Full document text

    Returns:
        True if term appears to be a fragment
    """
    term_lower = term.lower()

    # Check if term frequently appears as part of longer phrases
    # Example: "valve" might be fragment of "control valve"

    # Pattern: term preceded by adjective or noun
    before_pattern = r'\b(\w+)\s+' + re.escape(term_lower) + r'\b'
    before_matches = re.findall(before_pattern, full_text.lower())

    # Pattern: term followed by noun
    after_pattern = r'\b' + re.escape(term_lower) + r'\s+(\w+)\b'
    after_matches = re.findall(after_pattern, full_text.lower())

    # If term appears more often in compounds than alone, it's a fragment
    standalone_count = len(re.findall(r'\b' + re.escape(term_lower) + r'\b', full_text.lower()))
    compound_count = len(before_matches) + len(after_matches)

    # Fragment if appears in compounds >70% of the time
    if standalone_count > 0:
        fragment_ratio = compound_count / standalone_count
        return fragment_ratio > 0.7

    return False
```

### 6.3 Extracting Complete Compounds

```python
def extract_complete_compounds(
    candidates: List[str],
    full_text: str,
    nlp
) -> List[str]:
    """
    Expand fragments into complete compound terms

    Example: "valve" -> "control valve", "safety valve"
    """
    doc = nlp(full_text)
    complete_compounds = set()

    for noun_chunk in doc.noun_chunks:
        chunk_text = noun_chunk.text.strip()

        # Check if chunk contains any of our candidate terms
        for candidate in candidates:
            if candidate.lower() in chunk_text.lower():
                # Extract the full noun chunk as a complete compound
                if len(chunk_text.split()) >= 2:  # Multi-word compound
                    complete_compounds.add(chunk_text)

    return list(complete_compounds)
```

---

## 7. Best Practices for Acronym Detection

### 7.1 Acronym Identification Patterns

```python
def is_acronym(term: str) -> bool:
    """
    Identify if term is an acronym

    Criteria:
    - All uppercase letters
    - 2-6 characters long
    - May contain numbers (e.g., "4G", "H2O")
    - May contain hyphens (e.g., "RS-232")
    """
    term_clean = term.strip()

    # Remove hyphens and periods for checking
    term_check = term_clean.replace("-", "").replace(".", "")

    # Must be 2-6 characters
    if not (2 <= len(term_check) <= 6):
        return False

    # Must be mostly uppercase
    upper_count = sum(c.isupper() for c in term_check)
    total_alpha = sum(c.isalpha() for c in term_check)

    if total_alpha == 0:
        return False

    # At least 75% uppercase
    return (upper_count / total_alpha) >= 0.75
```

### 7.2 Acronym Validation Rules

```python
COMMON_FALSE_POSITIVE_ACRONYMS = {
    # Articles/prepositions that might appear as uppercase
    "A", "I", "IN", "ON", "AT", "TO", "OF", "OR", "AN",

    # Roman numerals (not acronyms)
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",

    # Common abbreviations (not technical terms)
    "ETC", "E.G.", "I.E.", "VS", "VIZ",
}

def validate_acronym(
    acronym: str,
    context: str,
    frequency: int
) -> Tuple[bool, str]:
    """
    Validate if acronym is a genuine technical term

    Returns:
        (is_valid, expansion_if_found)
    """
    acronym_upper = acronym.upper()

    # Check false positives
    if acronym_upper in COMMON_FALSE_POSITIVE_ACRONYMS:
        return False, ""

    # Try to find expansion in context
    expansion = find_acronym_expansion(acronym, context)

    # Valid if:
    # 1. Expansion found, OR
    # 2. Appears frequently (>= 3 times), OR
    # 3. Known technical acronym

    if expansion:
        return True, expansion

    if frequency >= 3:
        return True, ""

    if is_known_technical_acronym(acronym):
        return True, ""

    return False, ""
```

### 7.3 Acronym Expansion Detection

```python
def find_acronym_expansion(
    acronym: str,
    context: str,
    window_size: int = 200
) -> Optional[str]:
    """
    Find the expansion of an acronym in context

    Pattern: "Supervisory Control And Data Acquisition (SCADA)"
    """
    acronym_upper = acronym.upper()

    # Pattern 1: Expansion followed by acronym in parentheses
    # "Full Term (ACRONYM)"
    pattern1 = r'([A-Z][a-z\s]+?)\s*\(' + re.escape(acronym_upper) + r'\)'
    matches1 = re.finditer(pattern1, context)

    for match in matches1:
        candidate = match.group(1).strip()
        if validate_expansion(acronym_upper, candidate):
            return candidate

    # Pattern 2: Acronym followed by expansion
    # "ACRONYM (Full Term)"
    pattern2 = re.escape(acronym_upper) + r'\s*\(([A-Z][a-z\s]+?)\)'
    matches2 = re.finditer(pattern2, context)

    for match in matches2:
        candidate = match.group(1).strip()
        if validate_expansion(acronym_upper, candidate):
            return candidate

    return None


def validate_expansion(acronym: str, candidate: str) -> bool:
    """
    Validate if candidate is genuine expansion of acronym

    Rules:
    - First letters of words should match acronym letters
    - Number of words should roughly match acronym length
    """
    words = candidate.split()

    # Must have at least as many words as acronym letters
    if len(words) < len(acronym):
        return False

    # Check if first letters match
    first_letters = ''.join(word[0].upper() for word in words if word)

    # Exact match
    if first_letters == acronym:
        return True

    # Partial match (allows for articles/prepositions)
    match_count = sum(1 for a, b in zip(acronym, first_letters) if a == b)
    match_ratio = match_count / len(acronym)

    return match_ratio >= 0.7
```

### 7.4 Known Technical Acronym Database

```python
KNOWN_TECHNICAL_ACRONYMS = {
    # Networking
    "API", "HTTP", "HTTPS", "TCP", "IP", "DNS", "VPN", "LAN", "WAN",

    # Software
    "SQL", "XML", "JSON", "REST", "SOAP", "CRUD", "OOP", "MVC",

    # Industrial/Control Systems
    "PLC", "HMI", "SCADA", "DCS", "PID", "RTU", "I/O", "IO",

    # Standards
    "ISO", "IEC", "ANSI", "ASME", "DIN", "IEEE", "NAMUR",

    # Engineering
    "CAD", "CAM", "FEM", "CFD", "BOM", "P&ID",

    # Quality/Safety
    "QA", "QC", "SIL", "HAZOP", "FMEA",
}

def is_known_technical_acronym(acronym: str) -> bool:
    """Check against known technical acronym database"""
    return acronym.upper() in KNOWN_TECHNICAL_ACRONYMS
```

---

## 8. Frequency-Based Filtering Strategy

### 8.1 Adaptive Thresholds

```python
class FrequencyFilter:
    """Adaptive frequency-based term filtering"""

    def __init__(self, corpus_size: int):
        self.corpus_size = corpus_size
        self.min_frequency = self._calculate_min_frequency()

    def _calculate_min_frequency(self) -> int:
        """Calculate minimum frequency threshold based on corpus size"""
        if self.corpus_size < 1000:
            return 1
        elif self.corpus_size < 5000:
            return 2
        elif self.corpus_size < 20000:
            return 3
        else:
            return 4

    def should_include_term(
        self,
        term: str,
        frequency: int,
        is_acronym: bool = False,
        is_proper_noun: bool = False
    ) -> bool:
        """
        Determine if term should be included based on frequency

        Special cases:
        - Acronyms: Lower threshold (may appear less frequently)
        - Proper nouns: Lower threshold (company names, products)
        - Technical compounds: Standard threshold
        """
        # Acronyms and proper nouns can have lower threshold
        if is_acronym or is_proper_noun:
            adjusted_threshold = max(1, self.min_frequency - 1)
            return frequency >= adjusted_threshold

        return frequency >= self.min_frequency
```

### 8.2 Relative Frequency Analysis

```python
def calculate_relative_frequency(
    term: str,
    term_freq: int,
    total_terms: int,
    background_freq: Optional[int] = None
) -> float:
    """
    Calculate relative frequency score

    Higher score = more domain-specific
    """
    # Basic relative frequency
    rel_freq = term_freq / total_terms

    # If background frequency available (from general corpus)
    if background_freq is not None:
        # Technical specificity score
        specificity = term_freq / (background_freq + 1)
        return rel_freq * specificity

    return rel_freq
```

### 8.3 Top-K Selection

```python
def select_top_terms(
    candidates: Dict[str, int],
    k: int = 1000,
    min_score: float = 0.5
) -> List[Tuple[str, float]]:
    """
    Select top K terms based on combined scoring

    Args:
        candidates: Dict of {term: frequency}
        k: Maximum number of terms to return
        min_score: Minimum quality score threshold

    Returns:
        List of (term, score) tuples, sorted by score
    """
    scored_terms = []

    for term, freq in candidates.items():
        # Calculate combined quality score
        score = calculate_term_quality_score(
            term, freq,
            document_freq=1,  # Would need actual corpus stats
            total_documents=1
        )

        if score >= min_score:
            scored_terms.append((term, score))

    # Sort by score, take top K
    scored_terms.sort(key=lambda x: x[1], reverse=True)
    return scored_terms[:k]
```

---

## 9. Code-Ready Validation Rules (Implementation)

### 9.1 Complete Validation Pipeline

```python
class TechnicalTermValidator:
    """
    Complete validation pipeline for technical term extraction
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.nlp = None

        # Load spaCy if available
        try:
            import spacy
            model = "en_core_web_sm" if language == "en" else "de_core_news_sm"
            self.nlp = spacy.load(model)
        except:
            pass

    def validate_term(
        self,
        term: str,
        frequency: int,
        full_text: str,
        context: str = ""
    ) -> Dict[str, any]:
        """
        Comprehensive term validation

        Returns:
            {
                "valid": bool,
                "term": str,
                "confidence": float (0-1),
                "category": str (noun/acronym/compound),
                "rejection_reasons": List[str],
                "metadata": Dict
            }
        """
        result = {
            "valid": False,
            "term": term,
            "confidence": 0.0,
            "category": "unknown",
            "rejection_reasons": [],
            "metadata": {}
        }

        term_clean = term.strip()

        # Validation checks (in order of importance)

        # 1. Length check
        if len(term_clean) < 2:
            result["rejection_reasons"].append("Too short")
            return result

        if len(term_clean) > 50:
            result["rejection_reasons"].append("Too long")
            return result

        # 2. Stop word check
        if is_stopword(term_clean):
            result["rejection_reasons"].append("Stop word")
            return result

        # 3. Single character special handling
        if len(term_clean) == 1:
            if term_clean.isupper() and term_clean.isalpha():
                result["valid"] = True
                result["category"] = "acronym"
                result["confidence"] = 0.6
                return result
            else:
                result["rejection_reasons"].append("Invalid single character")
                return result

        # 4. Check if acronym
        is_acro = is_acronym(term_clean)
        if is_acro:
            valid, expansion = validate_acronym(term_clean, full_text, frequency)
            if valid:
                result["valid"] = True
                result["category"] = "acronym"
                result["confidence"] = 0.9 if expansion else 0.7
                result["metadata"]["expansion"] = expansion
                return result
            else:
                result["rejection_reasons"].append("Invalid acronym")
                return result

        # 5. Numeric term check
        if not should_extract_numeric_term(term_clean):
            result["rejection_reasons"].append("Pure numeric value")
            return result

        # 6. Capitalization pattern check
        if not has_valid_capitalization(term_clean):
            result["rejection_reasons"].append("Invalid capitalization")
            return result

        # 7. Fragment detection
        if is_fragment(term_clean, full_text):
            result["rejection_reasons"].append("Fragment of compound term")
            return result

        # 8. POS validation (if NLP available)
        if self.nlp:
            if not validate_term_pos(term_clean, self.nlp):
                result["rejection_reasons"].append("Invalid POS pattern")
                return result

        # 9. Frequency check
        corpus_size = len(full_text)
        filter = FrequencyFilter(corpus_size)

        is_proper = self._is_proper_noun(term_clean)
        if not filter.should_include_term(term_clean, frequency, is_acro, is_proper):
            result["rejection_reasons"].append(f"Frequency too low (< {filter.min_frequency})")
            return result

        # All checks passed
        result["valid"] = True
        result["confidence"] = self._calculate_confidence(term_clean, frequency, context)
        result["category"] = self._classify_term(term_clean)

        return result

    def _is_proper_noun(self, term: str) -> bool:
        """Check if term is a proper noun"""
        if not self.nlp:
            # Fallback: check capitalization
            return term[0].isupper()

        doc = self.nlp(term)
        return any(token.pos_ == "PROPN" for token in doc)

    def _calculate_confidence(
        self,
        term: str,
        frequency: int,
        context: str
    ) -> float:
        """
        Calculate confidence score (0-1)

        Factors:
        - Frequency (higher = more confident)
        - Capitalization (proper case = more confident)
        - Context quality
        - Term length (2-4 words = optimal)
        """
        score = 0.5  # Base score

        # Frequency bonus (up to +0.3)
        freq_bonus = min(0.3, frequency * 0.05)
        score += freq_bonus

        # Capitalization bonus (+0.1 for proper case)
        if term[0].isupper():
            score += 0.1

        # Optimal length bonus (+0.1 for 2-4 words)
        word_count = len(term.split())
        if 2 <= word_count <= 4:
            score += 0.1

        return min(1.0, score)

    def _classify_term(self, term: str) -> str:
        """Classify term type"""
        if is_acronym(term):
            return "acronym"
        elif len(term.split()) == 1:
            return "single_noun"
        elif len(term.split()) >= 2:
            return "compound"
        else:
            return "unknown"
```

### 9.2 Batch Validation

```python
def validate_term_batch(
    candidates: List[Dict[str, any]],
    full_text: str,
    validator: TechnicalTermValidator
) -> List[Dict[str, any]]:
    """
    Validate a batch of term candidates

    Args:
        candidates: List of {term, frequency, context}
        full_text: Full document text
        validator: TechnicalTermValidator instance

    Returns:
        List of validated terms with scores and metadata
    """
    results = []

    for candidate in candidates:
        term = candidate["term"]
        frequency = candidate["frequency"]
        context = candidate.get("context", "")

        validation = validator.validate_term(
            term, frequency, full_text, context
        )

        if validation["valid"]:
            results.append({
                **candidate,
                **validation
            })

    # Sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)

    return results
```

---

## 10. Examples: Good vs. Bad Terms

### 10.1 Engineering/Industrial Terms

```python
GOOD_EXAMPLES = {
    "control_valve": {
        "term": "control valve",
        "why_good": "Complete compound noun, domain-specific",
        "frequency": 15,
        "confidence": 0.95
    },

    "pressure_transmitter": {
        "term": "pressure transmitter",
        "why_good": "Technical compound, clear semantic meaning",
        "frequency": 8,
        "confidence": 0.90
    },

    "plc": {
        "term": "PLC",
        "why_good": "Well-known acronym, high frequency",
        "frequency": 12,
        "confidence": 0.92,
        "expansion": "Programmable Logic Controller"
    },

    "safety_instrumented_system": {
        "term": "safety instrumented system",
        "why_good": "Multi-word technical term, domain-specific",
        "frequency": 6,
        "confidence": 0.88
    },

    "iso_9001": {
        "term": "ISO 9001",
        "why_good": "Standard reference with number, widely recognized",
        "frequency": 4,
        "confidence": 0.85
    },

    "pid_controller": {
        "term": "PID controller",
        "why_good": "Acronym + noun compound, technical",
        "frequency": 10,
        "confidence": 0.93
    },
}

BAD_EXAMPLES = {
    "the_system": {
        "term": "the system",
        "why_bad": "Contains article, too generic",
        "rejection": "Contains stop word 'the'"
    },

    "100": {
        "term": "100",
        "why_bad": "Pure number, should be data point",
        "rejection": "Pure numeric value"
    },

    "very_important": {
        "term": "very important",
        "why_bad": "Adjective phrase, not a noun term",
        "rejection": "Invalid POS pattern (ADV + ADJ)"
    },

    "page": {
        "term": "page",
        "why_bad": "Document structure reference",
        "rejection": "Technical stop word"
    },

    "etc": {
        "term": "etc.",
        "why_bad": "Generic abbreviation, no semantic content",
        "rejection": "Stop word"
    },

    "a": {
        "term": "a",
        "why_bad": "Article, single character",
        "rejection": "Invalid single character"
    },

    "see_above": {
        "term": "see above",
        "why_bad": "Meta-reference, navigational text",
        "rejection": "Technical stop word phrase"
    },
}
```

### 10.2 Software/IT Terms

```python
IT_GOOD_EXAMPLES = {
    "api_endpoint": {
        "term": "API endpoint",
        "why_good": "Technical compound, widely used in domain",
        "confidence": 0.91
    },

    "rest_api": {
        "term": "REST API",
        "why_good": "Acronym compound, standard terminology",
        "confidence": 0.94
    },

    "database_schema": {
        "term": "database schema",
        "why_good": "Technical compound, clear meaning",
        "confidence": 0.89
    },

    "json": {
        "term": "JSON",
        "why_good": "Standard data format acronym",
        "confidence": 0.95,
        "expansion": "JavaScript Object Notation"
    },
}

IT_BAD_EXAMPLES = {
    "click_here": {
        "term": "click here",
        "why_bad": "UI instruction, not a technical term",
        "rejection": "Invalid verb phrase"
    },

    "version_2": {
        "term": "version 2",
        "why_bad": "Metadata, not technical concept",
        "rejection": "Version number pattern"
    },
}
```

---

## 11. Implementation Roadmap

### Phase 1: Enhanced Filtering (Immediate)

**Priority: HIGH**

```python
# File: src/backend/services/term_validator.py

1. Implement stop word filtering
   - Add GENERIC_STOPWORDS, TECHNICAL_STOPWORDS, ENGINEERING_STOPWORDS
   - Implement is_stopword() function

2. Implement single character validation
   - Allow uppercase single letters (A, I, O)
   - Reject lowercase single letters

3. Implement number validation
   - Add should_extract_numeric_term()
   - Filter pure numbers but keep "ISO 9001", "Model X500"

4. Add capitalization validation
   - Implement has_valid_capitalization()
```

**Estimated effort: 4-6 hours**

### Phase 2: POS Tagging Enhancement (Next Sprint)

**Priority: MEDIUM**

```python
# Enhance: src/backend/services/term_extractor.py

1. Implement POS pattern validation
   - Add VALID_TERM_PATTERNS dictionary
   - Implement validate_term_pos()

2. Add dependency parsing for compounds
   - Implement extract_compound_terms()
   - Use spaCy's dependency parser

3. Fragment detection
   - Implement is_fragment()
   - Expand fragments to complete compounds
```

**Estimated effort: 8-10 hours**

### Phase 3: Acronym Detection (Following Sprint)

**Priority: MEDIUM**

```python
# New file: src/backend/services/acronym_detector.py

1. Implement acronym detection
   - Add is_acronym()
   - Add validate_acronym()

2. Acronym expansion detection
   - Implement find_acronym_expansion()
   - Pattern matching for "Term (ACRONYM)" format

3. Known acronym database
   - Add KNOWN_TECHNICAL_ACRONYMS set
   - Domain-specific lists (industrial, IT, standards)
```

**Estimated effort: 6-8 hours**

### Phase 4: Adaptive Frequency Filtering (Optional)

**Priority: LOW**

```python
# Enhance: src/backend/services/term_extractor.py

1. Implement FrequencyFilter class
   - Adaptive thresholds based on document size
   - Special handling for acronyms and proper nouns

2. TF-IDF scoring (if multiple documents)
   - Implement calculate_term_quality_score()
   - Relative frequency analysis
```

**Estimated effort: 8-10 hours**

---

## 12. Testing Strategy

### 12.1 Unit Tests

```python
# File: tests/unit/test_term_validation.py

import pytest
from src.backend.services.term_validator import (
    is_stopword,
    has_valid_capitalization,
    should_extract_numeric_term,
    is_acronym,
    validate_term_pos
)

class TestStopWordFiltering:
    """Test stop word filtering"""

    def test_generic_stopwords_rejected(self):
        assert is_stopword("the") == True
        assert is_stopword("and") == True
        assert is_stopword("very") == True

    def test_technical_stopwords_rejected(self):
        assert is_stopword("page") == True
        assert is_stopword("section") == True
        assert is_stopword("figure") == True

    def test_valid_terms_accepted(self):
        assert is_stopword("control valve") == False
        assert is_stopword("API") == False
        assert is_stopword("pressure sensor") == False

    def test_multi_word_with_stopwords(self):
        # "the system" should be rejected
        assert is_stopword("the system") == True
        # "control system" should be accepted
        assert is_stopword("control system") == False


class TestCapitalizationValidation:
    """Test capitalization pattern validation"""

    def test_valid_patterns(self):
        assert has_valid_capitalization("Control Valve") == True
        assert has_valid_capitalization("API") == True
        assert has_valid_capitalization("pressure sensor") == True

    def test_invalid_patterns(self):
        assert has_valid_capitalization("pReSsUrE sEnSoR") == False


class TestNumericTerms:
    """Test numeric term handling"""

    def test_pure_numbers_rejected(self):
        assert should_extract_numeric_term("100") == False
        assert should_extract_numeric_term("95%") == False

    def test_valid_numeric_terms(self):
        assert should_extract_numeric_term("ISO 9001") == True
        assert should_extract_numeric_term("Model X500") == True
        assert should_extract_numeric_term("100 psi") == True

    def test_version_numbers_rejected(self):
        assert should_extract_numeric_term("Version 2.5") == False


class TestAcronymDetection:
    """Test acronym identification and validation"""

    def test_valid_acronyms(self):
        assert is_acronym("API") == True
        assert is_acronym("HTTP") == True
        assert is_acronym("PLC") == True

    def test_invalid_acronyms(self):
        assert is_acronym("the") == False
        assert is_acronym("A") == False  # Single letter
        assert is_acronym("VERYLONGACRONYM") == False  # Too long

    def test_false_positive_filtering(self):
        from src.backend.services.acronym_detector import validate_acronym

        # "OR" should be rejected (conjunction)
        assert validate_acronym("OR", "text with OR keyword", frequency=1)[0] == False

        # "API" should be accepted
        assert validate_acronym("API", "text with API endpoint", frequency=3)[0] == True
```

### 12.2 Integration Tests

```python
# File: tests/integration/test_term_extraction.py

class TestCompleteExtractionPipeline:
    """Test complete term extraction pipeline with validation"""

    def test_extract_from_sample_engineering_doc(self):
        """Test extraction from engineering document"""

        sample_text = """
        The control valve regulates the flow of process fluid through
        the pipeline. Each control valve is equipped with a pressure
        transmitter and a PID controller for precise control.

        The system complies with ISO 9001 standards and NAMUR NE 107
        recommendations for self-monitoring.
        """

        extractor = TermExtractor(language="en")
        validator = TechnicalTermValidator(language="en")

        # Extract candidates
        candidates = extractor.extract_terms(
            sample_text,
            min_frequency=1,
            min_term_length=2
        )

        # Validate
        validated = validate_term_batch(candidates, sample_text, validator)

        # Expected terms
        expected_terms = {
            "control valve",
            "pressure transmitter",
            "PID controller",
            "ISO 9001",
            "NAMUR NE 107"
        }

        extracted_terms = {t["term"].lower() for t in validated}

        # Check that expected terms are found
        for expected in expected_terms:
            assert expected in extracted_terms, f"Missing term: {expected}"

        # Check that bad terms are filtered
        bad_terms = {"the", "of", "for", "and", "the system"}
        for bad_term in bad_terms:
            assert bad_term not in extracted_terms, f"Should reject: {bad_term}"
```

### 12.3 Test Data Sets

Create test documents in `tests/fixtures/`:

```
tests/fixtures/
├── sample_engineering_doc.txt      # Industrial/engineering terms
├── sample_it_doc.txt                # Software/IT terms
├── sample_standards_doc.txt         # ISO, DIN, ASME references
├── sample_noisy_doc.txt             # Document with lots of noise
└── expected_results/
    ├── engineering_terms.json
    ├── it_terms.json
    └── standards_terms.json
```

---

## 13. Performance Optimization

### 13.1 Caching Strategies

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def is_stopword_cached(term: str) -> bool:
    """Cached stop word lookup"""
    return term.lower() in ALL_STOPWORDS

@lru_cache(maxsize=5000)
def validate_term_pos_cached(term: str, lang: str) -> bool:
    """Cache POS validation results"""
    nlp = get_nlp_model(lang)
    return validate_term_pos(term, nlp)
```

### 13.2 Batch Processing

```python
def extract_terms_batch(
    documents: List[Dict[str, str]],
    batch_size: int = 50
) -> List[Dict[str, any]]:
    """
    Process multiple documents in batches

    More efficient than processing one at a time
    """
    results = []

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        # Process batch with spaCy pipe (more efficient)
        texts = [doc["text"] for doc in batch]
        nlp_docs = nlp.pipe(texts, batch_size=batch_size)

        for doc, nlp_doc in zip(batch, nlp_docs):
            terms = extract_from_nlp_doc(nlp_doc)
            results.append({
                "document_id": doc["id"],
                "terms": terms
            })

    return results
```

---

## 14. Configuration File

Create a configuration file for easy tuning:

```python
# config/term_extraction_config.yaml

term_extraction:
  # Length constraints
  min_term_length: 2
  max_term_length: 50
  min_word_count: 1
  max_word_count: 5

  # Frequency thresholds
  adaptive_frequency: true
  frequency_thresholds:
    small_doc: 1      # < 1000 chars
    medium_doc: 2     # 1000-5000 chars
    large_doc: 3      # 5000-20000 chars
    xlarge_doc: 4     # > 20000 chars

  # Validation rules
  require_pos_validation: true
  detect_fragments: true
  expand_compounds: true
  extract_acronyms: true
  find_acronym_expansions: true

  # Filtering
  use_stopwords: true
  stopword_lists:
    - generic
    - technical
    - engineering

  validate_capitalization: true
  filter_pure_numbers: true

  # Quality scoring
  min_confidence_score: 0.5
  max_results: 1000

  # Language models
  spacy_models:
    en: "en_core_web_sm"
    de: "de_core_news_sm"
```

---

## 15. Summary and Quick Reference

### 15.1 Decision Matrix

| Question | Answer | Threshold/Rule |
|----------|--------|---------------|
| Minimum term length? | 2 characters | Allows "IO", "ID" |
| Maximum term length? | 50 characters | Prevents full sentences |
| Single-character terms? | ONLY uppercase letters | "A", "I", "O" accepted |
| Pure numbers? | NO | Extract as data, not terms |
| Numbers with text? | YES | "ISO 9001", "100 psi" |
| Percentages alone? | NO | Extract as data |
| Stop words? | NO | Use combined stop list |
| Minimum frequency? | Adaptive (1-4) | Based on document size |
| POS validation? | YES | Noun-centric patterns |
| Acronyms? | YES | 2-6 chars, mostly uppercase |
| Compound terms? | YES | Prefer complete compounds |
| Fragments? | NO | Expand to complete terms |

### 15.2 Critical Validation Checklist

```
✓ Length: 2-50 characters
✓ Not a stop word (generic, technical, or domain-specific)
✓ Valid capitalization pattern
✓ Not a pure number or percentage (unless part of standard/model)
✓ Meets minimum frequency threshold
✓ Valid POS pattern (noun-centric)
✓ Not a fragment of larger compound
✓ Contains at least one alphabetic character
✓ Acronyms validated with expansion or frequency
✓ Confidence score >= 0.5
```

### 15.3 Quick Implementation Guide

**Week 1: Basic Filtering**
- Add stop word lists
- Implement basic validation (length, stopwords, numbers)
- Add single-character filtering

**Week 2: POS Enhancement**
- Add POS validation with spaCy
- Implement compound term detection
- Add fragment filtering

**Week 3: Acronym Detection**
- Implement acronym identification
- Add acronym expansion detection
- Build known acronym database

**Week 4: Testing & Optimization**
- Write comprehensive unit tests
- Add integration tests with real documents
- Performance optimization and caching

---

## 16. References and Further Reading

### Academic Papers

1. **"Stopwords in Technical Language Processing"** - Sarica & Luo (2021)
   - PLOS ONE: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254937
   - Key contribution: Domain-specific technical stopwords identification

2. **"Survey on terminology extraction from texts"** - Journal of Big Data (2025)
   - SpringerOpen: https://journalofbigdata.springeropen.com/articles/10.1186/s40537-025-01077-x
   - Comprehensive survey of terminology extraction methods

3. **"Evaluation of cutoff policies for term extraction"** - Journal of the Brazilian Computer Society (2015)
   - Focus on frequency threshold optimization

### Tools and Libraries

1. **spaCy** - Industrial-strength NLP
   - Documentation: https://spacy.io/usage/linguistic-features
   - Noun chunks, POS tagging, dependency parsing

2. **textacy** - Higher-level NLP built on spaCy
   - Documentation: https://textacy.readthedocs.io/
   - Advanced term extraction utilities

3. **NLTK** - Natural Language Toolkit
   - Stop words lists, text processing utilities

### Industry Resources

1. **TerminOrgs Term Extraction Guide**
   - Practical guide for terminology extraction workflows

2. **Sketch Engine** - Term Extraction Best Practices
   - Commercial tool with research-backed methods

---

## 17. Contact and Maintenance

**Document Version:** 1.0
**Last Updated:** 2025-01-XX
**Author:** Claude (Research Agent)
**Project:** Glossary APP - Term Extraction Enhancement

**Change Log:**
- v1.0 (2025-01-XX): Initial research and recommendations based on 2024-2025 academic research

**Next Review:** After Phase 1 implementation (estimated 2-3 weeks)

---

## Appendix A: Sample Stop Words File

```python
# File: src/backend/services/stopwords.py

"""
Technical stop words for term extraction
Based on PLOS One 2021 research and NLTK stop words
"""

GENERIC_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "while",
    "of", "at", "by", "for", "with", "about", "into", "through", "during",
    "before", "after", "above", "below", "to", "from", "up", "down", "in",
    "out", "on", "off", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "can", "will",
    "just", "should", "now", "i", "you", "he", "she", "it", "we", "they",
    "them", "their", "what", "which", "who", "whom", "this", "that", "these",
    "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "doing", "would", "should",
    "could", "ought", "might", "must", "shall",
}

TECHNICAL_STOPWORDS = {
    "section", "chapter", "page", "figure", "fig", "table", "appendix",
    "part", "paragraph", "clause", "subsection", "item", "note", "example",
    "above", "below", "following", "previous", "next", "herein", "thereof",
    "whereby", "wherein", "system", "method", "device", "apparatus", "means",
    "process", "mechanism", "structure", "use", "using", "used", "see",
    "refer", "according", "include", "including", "included", "comprise",
    "consist", "type", "kind", "sort", "instance", "way", "manner", "form",
    "case", "result", "outcome", "effect", "impact", "step", "stage",
    "phase", "operation", "procedure",
}

ENGINEERING_STOPWORDS = {
    "small", "large", "big", "little", "high", "low", "good", "bad",
    "better", "worse", "best", "worst", "new", "old", "first", "second",
    "third", "last", "several", "various", "certain", "different", "similar",
    "particular", "specific", "general", "common", "standard", "typical",
    "normal", "regular", "special", "unique",
}

# Combined set
ALL_STOPWORDS = GENERIC_STOPWORDS | TECHNICAL_STOPWORDS | ENGINEERING_STOPWORDS
```

---

## Appendix B: Known Technical Acronyms Database

```python
# File: src/backend/services/technical_acronyms.py

"""
Database of known technical acronyms across domains
Regularly updated based on usage patterns
"""

NETWORKING_ACRONYMS = {
    "API", "HTTP", "HTTPS", "FTP", "SFTP", "TCP", "IP", "UDP", "DNS",
    "DHCP", "VPN", "LAN", "WAN", "MAN", "SSH", "SSL", "TLS", "SMTP",
    "POP", "IMAP", "REST", "SOAP", "RPC", "P2P", "CDN", "NAT", "MAC",
}

SOFTWARE_ACRONYMS = {
    "SQL", "NoSQL", "XML", "JSON", "YAML", "CSV", "HTML", "CSS", "JS",
    "CRUD", "OOP", "MVC", "MVP", "MVVM", "CI", "CD", "TDD", "BDD",
    "GUI", "CLI", "IDE", "SDK", "API", "OS", "VM", "JIT", "AOT",
}

INDUSTRIAL_CONTROL_ACRONYMS = {
    "PLC", "HMI", "SCADA", "DCS", "PID", "RTU", "I/O", "IO", "MOD",
    "VFD", "VSD", "PWM", "ADC", "DAC", "CAN", "HART", "OPC", "MTU",
    "SIS", "ESD", "BMS", "HVAC", "PAC",
}

STANDARDS_ACRONYMS = {
    "ISO", "IEC", "ANSI", "ASME", "DIN", "IEEE", "NIST", "API", "ASTM",
    "BS", "EN", "CEN", "UL", "CSA", "NAMUR", "ISA", "OSHA", "EPA",
}

QUALITY_SAFETY_ACRONYMS = {
    "QA", "QC", "SIL", "HAZOP", "FMEA", "FMECA", "FTA", "ETA", "RCA",
    "LOPA", "SIF", "SRS", "PHA", "JSA", "MSDS", "SDS", "PPE", "OSHA",
}

ENGINEERING_ACRONYMS = {
    "CAD", "CAM", "CAE", "FEM", "FEA", "CFD", "BOM", "ECN", "ECO",
    "P&ID", "PFD", "GA", "DWG", "GD&T", "CNC", "CMM", "NDT",
}

# Combined database
KNOWN_TECHNICAL_ACRONYMS = (
    NETWORKING_ACRONYMS |
    SOFTWARE_ACRONYMS |
    INDUSTRIAL_CONTROL_ACRONYMS |
    STANDARDS_ACRONYMS |
    QUALITY_SAFETY_ACRONYMS |
    ENGINEERING_ACRONYMS
)

def is_known_acronym(acronym: str, domain: str = "all") -> bool:
    """
    Check if acronym is in known database

    Args:
        acronym: Acronym to check
        domain: Specific domain to check ("networking", "software", etc.) or "all"

    Returns:
        True if acronym is known in specified domain
    """
    acronym_upper = acronym.upper()

    if domain == "all":
        return acronym_upper in KNOWN_TECHNICAL_ACRONYMS

    domain_map = {
        "networking": NETWORKING_ACRONYMS,
        "software": SOFTWARE_ACRONYMS,
        "industrial": INDUSTRIAL_CONTROL_ACRONYMS,
        "standards": STANDARDS_ACRONYMS,
        "quality": QUALITY_SAFETY_ACRONYMS,
        "engineering": ENGINEERING_ACRONYMS,
    }

    return acronym_upper in domain_map.get(domain, set())
```

---

**End of Document**
