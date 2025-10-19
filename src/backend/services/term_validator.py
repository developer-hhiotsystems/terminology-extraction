"""
Term Validation Service
Provides comprehensive validation logic to filter out low-quality glossary entries.

This module implements multi-layered validation including:
- Length validation (minimum character count)
- Number and percentage filtering
- Symbol and punctuation ratio checks
- Stop word filtering
- Capitalization pattern validation
- Word count validation for compound terms
"""
import re
import string
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import logging

from src.backend.constants import (
    MIN_TERM_LENGTH,
    MAX_TERM_LENGTH,
    MIN_WORD_COUNT,
    MAX_WORD_COUNT,
    MAX_SYMBOL_RATIO,
    MIN_ACRONYM_LENGTH,
    MAX_ACRONYM_LENGTH,
    REJECT_PURE_NUMBERS,
    REJECT_PERCENTAGES,
    ALLOW_ALL_UPPERCASE,
    LANG_ENGLISH,
    LANG_GERMAN,
    PATTERN_DUPLICATE_CHARS,
    PATTERN_ALTERNATING_DUPLICATES,
    PATTERN_PDF_ENCODING,
    PATTERN_ET_AL,
    PATTERN_IBID,
    PATTERN_YEAR_ONLY,
    PATTERN_PAGE_REF,
    PATTERN_SCIENTIFIC_NOTATION,
    # Strict validator constants
    STRICT_MIN_TERM_LENGTH,
    STRICT_MAX_TERM_LENGTH,
    STRICT_MIN_WORD_COUNT,
    STRICT_MAX_WORD_COUNT,
    STRICT_MAX_SYMBOL_RATIO,
    STRICT_MIN_ACRONYM_LENGTH,
    STRICT_MAX_ACRONYM_LENGTH,
    # Lenient validator constants
    LENIENT_MIN_TERM_LENGTH,
    LENIENT_MAX_TERM_LENGTH,
    LENIENT_MIN_WORD_COUNT,
    LENIENT_MAX_WORD_COUNT,
    LENIENT_MAX_SYMBOL_RATIO,
    LENIENT_MIN_ACRONYM_LENGTH,
    LENIENT_MAX_ACRONYM_LENGTH
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Configuration for term validation rules"""

    # Length constraints
    min_term_length: int = MIN_TERM_LENGTH
    max_term_length: int = MAX_TERM_LENGTH

    # Word count constraints (for compound terms)
    min_word_count: int = MIN_WORD_COUNT
    max_word_count: int = MAX_WORD_COUNT

    # Symbol/punctuation constraints
    max_symbol_ratio: float = MAX_SYMBOL_RATIO

    # Capitalization rules
    allow_all_uppercase: bool = ALLOW_ALL_UPPERCASE
    min_acronym_length: int = MIN_ACRONYM_LENGTH
    max_acronym_length: int = MAX_ACRONYM_LENGTH

    # Number filtering
    reject_pure_numbers: bool = REJECT_PURE_NUMBERS
    reject_percentages: bool = REJECT_PERCENTAGES

    # Stop words - common English words that shouldn't be glossary terms
    stop_words: set = None

    # Language-specific settings
    language: str = LANG_ENGLISH

    def __post_init__(self):
        """Initialize stop words if not provided"""
        if self.stop_words is None:
            self.stop_words = self._get_default_stop_words()

    def _get_default_stop_words(self) -> set:
        """Get default stop words based on language"""
        if self.language == LANG_ENGLISH:
            return {
                # Articles
                "a", "an", "the",
                # Conjunctions
                "and", "or", "but", "nor", "yet", "so",
                # Prepositions
                "of", "in", "on", "at", "to", "for", "with", "from", "by",
                "about", "into", "through", "during", "before", "after",
                "above", "below", "between", "under", "over",
                # Pronouns
                "i", "you", "he", "she", "it", "we", "they",
                "me", "him", "her", "us", "them",
                "this", "that", "these", "those",
                # Common verbs
                "is", "are", "was", "were", "be", "been", "being",
                "have", "has", "had", "do", "does", "did",
                "will", "would", "should", "could", "may", "might",
                # Common adjectives/adverbs
                "all", "any", "both", "each", "few", "more", "most",
                "other", "some", "such", "no", "not", "only", "own",
                "same", "than", "too", "very",
                # Numbers as words
                "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine", "ten",
            }
        elif self.language == LANG_GERMAN:
            return {
                # German articles
                "der", "die", "das", "den", "dem", "des",
                "ein", "eine", "einen", "einem", "einer", "eines",
                # German prepositions
                "in", "auf", "an", "von", "zu", "mit", "bei", "nach",
                "über", "unter", "durch", "für", "um", "aus",
                # German conjunctions
                "und", "oder", "aber", "denn", "dass", "wenn", "weil",
                # German pronouns
                "ich", "du", "er", "sie", "es", "wir", "ihr",
                "mich", "dich", "ihn", "uns", "euch",
                "dieser", "diese", "dieses", "jener", "jene", "jenes",
                # Common German verbs
                "ist", "sind", "war", "waren", "sein", "haben", "werden",
                "kann", "könnte", "soll", "sollte", "muss", "müssen",
                # Common German words
                "alle", "einige", "mehr", "weniger", "sehr", "nicht",
            }
        else:
            return set()


class TermValidator:
    """
    Comprehensive term validation service.

    Validates glossary terms against multiple quality criteria to ensure
    only meaningful, well-formed terms are accepted.
    """

    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize the term validator

        Args:
            config: Validation configuration. Uses defaults if not provided.
        """
        self.config = config or ValidationConfig()
        logger.info(f"TermValidator initialized with language: {self.config.language}")

    def is_valid_term(self, term: str) -> bool:
        """
        Check if a term is valid

        Args:
            term: The term to validate

        Returns:
            True if term passes all validation checks, False otherwise
        """
        if not term or not isinstance(term, str):
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
            self._validate_word_count,
            self._validate_not_fragment,
            # ✅ NEW: PDF artifact rejection
            self._validate_no_pdf_artifacts,
            self._validate_no_citations,
            self._validate_no_broken_hyphens,
            self._validate_no_ocr_corruption,
            self._validate_capitalization,
        ]

        for validator in validators:
            is_valid, _ = validator(term)
            if not is_valid:
                return False

        return True

    def get_rejection_reason(self, term: str) -> str:
        """
        Get the reason why a term was rejected

        Args:
            term: The term to validate

        Returns:
            Rejection reason string, or empty string if term is valid
        """
        if not term or not isinstance(term, str):
            return "Term is empty or not a string"

        # Run all validation checks in order
        validators = [
            self._validate_length,
            self._validate_not_empty_or_whitespace,
            self._validate_not_pure_number,
            self._validate_not_percentage,
            self._validate_not_pure_symbols,
            self._validate_symbol_ratio,
            self._validate_not_stop_word,
            self._validate_word_count,
            self._validate_not_fragment,
            self._validate_no_leading_article,
            # ✅ NEW: PDF artifact rejection
            self._validate_no_pdf_artifacts,
            self._validate_no_citations,
            self._validate_no_broken_hyphens,
            self._validate_no_ocr_corruption,
            self._validate_capitalization,
        ]

        for validator in validators:
            is_valid, reason = validator(term)
            if not is_valid:
                return reason

        return ""  # All checks passed

    def validate_with_details(self, term: str) -> Dict[str, any]:
        """
        Validate a term and return detailed results

        Args:
            term: The term to validate

        Returns:
            Dictionary with validation results:
            {
                "valid": bool,
                "term": str,
                "rejection_reason": str,
                "details": {
                    "length": bool,
                    "not_number": bool,
                    "not_percentage": bool,
                    "not_symbols": bool,
                    "symbol_ratio": bool,
                    "not_stop_word": bool,
                    "word_count": bool,
                    "not_fragment": bool,
                    "capitalization": bool
                }
            }
        """
        details = {}

        validators = {
            "length": self._validate_length,
            "not_empty": self._validate_not_empty_or_whitespace,
            "not_number": self._validate_not_pure_number,
            "not_percentage": self._validate_not_percentage,
            "not_symbols": self._validate_not_pure_symbols,
            "symbol_ratio": self._validate_symbol_ratio,
            "not_stop_word": self._validate_not_stop_word,
            "word_count": self._validate_word_count,
            "not_fragment": self._validate_not_fragment,
            "no_leading_article": self._validate_no_leading_article,
            "no_pdf_artifacts": self._validate_no_pdf_artifacts,
            "no_citations": self._validate_no_citations,
            "no_broken_hyphens": self._validate_no_broken_hyphens,
            "no_ocr_corruption": self._validate_no_ocr_corruption,
            "capitalization": self._validate_capitalization,
        }

        rejection_reason = ""
        all_valid = True

        for check_name, validator in validators.items():
            is_valid, reason = validator(term)
            details[check_name] = is_valid

            if not is_valid and all_valid:
                rejection_reason = reason
                all_valid = False

        return {
            "valid": all_valid,
            "term": term,
            "rejection_reason": rejection_reason,
            "details": details
        }

    # Individual validation methods

    def _validate_length(self, term: str) -> Tuple[bool, str]:
        """Validate term length"""
        term_len = len(term.strip())
        if term_len < self.config.min_term_length:
            return False, f"Term too short (minimum {self.config.min_term_length} characters)"
        if term_len > self.config.max_term_length:
            return False, f"Term too long (maximum {self.config.max_term_length} characters)"
        return True, ""

    def _validate_not_empty_or_whitespace(self, term: str) -> Tuple[bool, str]:
        """Validate term is not empty or only whitespace"""
        if not term.strip():
            return False, "Term is empty or only whitespace"
        return True, ""

    def _validate_not_pure_number(self, term: str) -> Tuple[bool, str]:
        """Validate term is not a pure number"""
        if not self.config.reject_pure_numbers:
            return True, ""

        # Remove common separators and check if it's a number
        cleaned = term.strip().replace(",", "").replace(".", "").replace(" ", "")

        # Check if it's purely numeric (with optional decimals/separators)
        if cleaned.isdigit():
            return False, "Term is a pure number"

        # Check for scientific notation (e.g., "1.5e10")
        if re.match(PATTERN_SCIENTIFIC_NOTATION, term.strip().lower()):
            return False, "Term is a number in scientific notation"

        return True, ""

    def _validate_not_percentage(self, term: str) -> Tuple[bool, str]:
        """Validate term is not a percentage"""
        if not self.config.reject_percentages:
            return True, ""

        # Check for percentage patterns: "70%", "70 %", "70 percent"
        percentage_patterns = [
            r'^\d+\.?\d*\s*%$',
            r'^\d+\.?\d*\s+percent$',
            r'^\d+\.?\d*\s+per\s+cent$',
        ]

        term_lower = term.strip().lower()
        for pattern in percentage_patterns:
            if re.match(pattern, term_lower):
                return False, "Term is a percentage"

        return True, ""

    def _validate_not_pure_symbols(self, term: str) -> Tuple[bool, str]:
        """Validate term is not purely symbols/punctuation"""
        cleaned = term.strip()

        # Check if term consists only of punctuation and symbols
        if all(c in string.punctuation or c in string.whitespace for c in cleaned):
            return False, "Term consists only of symbols/punctuation"

        return True, ""

    def _validate_symbol_ratio(self, term: str) -> Tuple[bool, str]:
        """Validate symbol-to-character ratio"""
        cleaned = term.strip()
        if not cleaned:
            return False, "Empty term"

        # Count symbols (punctuation excluding hyphens and apostrophes which are valid in terms)
        valid_punctuation = {'-', "'"}  # Hyphens and apostrophes are OK
        symbols = sum(1 for c in cleaned if c in string.punctuation and c not in valid_punctuation)

        symbol_ratio = symbols / len(cleaned)

        if symbol_ratio > self.config.max_symbol_ratio:
            return False, f"Too many symbols ({symbol_ratio:.1%} > {self.config.max_symbol_ratio:.1%})"

        return True, ""

    def _validate_not_stop_word(self, term: str) -> Tuple[bool, str]:
        """Validate term is not a stop word"""
        term_lower = term.strip().lower()

        # Check if entire term is a stop word
        if term_lower in self.config.stop_words:
            return False, f"Term is a stop word: '{term_lower}'"

        # For single-word terms, reject if it's a stop word
        words = term_lower.split()
        if len(words) == 1 and words[0] in self.config.stop_words:
            return False, f"Single-word term is a stop word: '{words[0]}'"

        return True, ""

    def _validate_word_count(self, term: str) -> Tuple[bool, str]:
        """Validate word count for compound terms"""
        # Split on whitespace and hyphens for word counting
        words = re.split(r'[\s\-]+', term.strip())
        words = [w for w in words if w]  # Remove empty strings

        word_count = len(words)

        if word_count < self.config.min_word_count:
            return False, f"Too few words ({word_count} < {self.config.min_word_count})"

        if word_count > self.config.max_word_count:
            return False, f"Too many words ({word_count} > {self.config.max_word_count})"

        return True, ""

    def _validate_not_fragment(self, term: str) -> Tuple[bool, str]:
        """Validate term is not a word fragment"""
        cleaned = term.strip()

        # Check for trailing hyphens (word fragments like "Mem-")
        if cleaned.endswith('-'):
            return False, "Term ends with hyphen (likely a fragment)"

        # Check for leading hyphens
        if cleaned.startswith('-'):
            return False, "Term starts with hyphen (likely a fragment)"

        # Check for incomplete words (very short with hyphen)
        if '-' in cleaned and len(cleaned) <= 3:
            return False, "Term appears to be a fragment"

        return True, ""

    def _validate_no_leading_article(self, term: str) -> Tuple[bool, str]:
        """
        Reject terms that start with common articles (the, a, an)

        Technical glossary terms should be in base form without articles.
        Examples:
            ✓ "Pressure Transmitter"
            ✗ "The Pressure Transmitter"
            ✓ "Algorithm"
            ✗ "An Algorithm"

        Args:
            term: The term to validate

        Returns:
            (is_valid, rejection_reason)
        """
        term_lower = term.lower().strip()

        # Check for leading articles
        if term_lower.startswith(('the ', 'a ', 'an ')):
            return False, "Starts with article (the/a/an) - terms should be in base form"

        return True, ""

    def _validate_no_pdf_artifacts(self, term: str) -> Tuple[bool, str]:
        """
        Reject PDF encoding artifacts and technical junk from PDF extraction

        PDFs sometimes contain encoding artifacts that shouldn't be terms.

        Args:
            term: The term to validate

        Returns:
            (is_valid, rejection_reason)
        """
        term_lower = term.lower().strip()

        # PDF font encoding references (cid:31, cid:128, etc.)
        if re.match(PATTERN_PDF_ENCODING, term_lower) or 'cid:' in term_lower:
            return False, "PDF encoding artifact (cid:XX)"

        # PDF internal references
        if term_lower.startswith(('obj', 'endobj', 'stream', 'endstream')):
            return False, "PDF internal reference"

        return True, ""

    def _validate_no_citations(self, term: str) -> Tuple[bool, str]:
        """
        Reject bibliographic citations that aren't glossary terms

        Args:
            term: The term to validate

        Returns:
            (is_valid, rejection_reason)
        """
        term_lower = term.lower().strip()

        # Common citation patterns
        citation_patterns = [
            PATTERN_ET_AL,
            r'^etal$',          # "etal"
            PATTERN_IBID,
            PATTERN_YEAR_ONLY,
            PATTERN_PAGE_REF,
        ]

        for pattern in citation_patterns:
            if re.search(pattern, term_lower):
                return False, "Bibliographic citation (et al/ibid/page ref)"

        return True, ""

    def _validate_no_broken_hyphens(self, term: str) -> Tuple[bool, str]:
        """
        Reject words broken by hyphens from PDF line breaks

        PDFs often break words across lines with hyphens, resulting in fragments.

        Examples to reject:
            "-tion" (end of "calculation" from previous line)
            "comple-" (beginning of "complete" continued on next line)

        Args:
            term: The term to validate

        Returns:
            (is_valid, rejection_reason)
        """
        # Starts with hyphen (likely end of previous line's word)
        if term.startswith('-') and len(term) > 1:
            return False, "Broken word fragment (starts with hyphen)"

        # Ends with hyphen (likely beginning of next line's word)
        if term.endswith('-') and len(term) > 1:
            return False, "Broken word fragment (ends with hyphen)"

        return True, ""

    def _validate_no_ocr_corruption(self, term: str) -> Tuple[bool, str]:
        """
        Reject terms with excessive OCR corruption patterns

        This is a backup check in case PDF normalization missed something.
        OCR errors often result in excessive character duplication.

        Examples to reject:
            "Pplloottttiinngg" (should be "Plotting")
            "Oonn" (should be "On")

        Args:
            term: The term to validate

        Returns:
            (is_valid, rejection_reason)
        """
        # Check for excessive duplicate characters (4+ in a row)
        # This indicates OCR corruption that wasn't normalized
        if re.search(PATTERN_DUPLICATE_CHARS, term, re.IGNORECASE):
            return False, "OCR corruption (excessive duplicate characters)"

        # Check for alternating duplicate pattern (aabbccdd)
        # Pattern: at least 3 different characters each duplicated
        if re.search(PATTERN_ALTERNATING_DUPLICATES, term, re.IGNORECASE):
            return False, "OCR corruption (alternating duplicates)"

        return True, ""

    def _validate_capitalization(self, term: str) -> Tuple[bool, str]:
        """Validate capitalization patterns"""
        cleaned = term.strip()

        # Check for single character (only allow if uppercase and it's a valid acronym)
        if len(cleaned) == 1:
            if not cleaned.isupper():
                return False, "Single character must be uppercase"
            return True, ""

        # Check for all uppercase (acronyms)
        if cleaned.isupper():
            if not self.config.allow_all_uppercase:
                return False, "All-uppercase terms not allowed"

            # Validate acronym length
            if len(cleaned) < self.config.min_acronym_length:
                return False, f"Acronym too short (minimum {self.config.min_acronym_length} characters)"

            if len(cleaned) > self.config.max_acronym_length:
                return False, f"Acronym too long (maximum {self.config.max_acronym_length} characters)"

        # Check for alternating case or random capitalization (like "HeLLo", "DaTaBaSe")
        # Allow: Title Case, UPPERCASE, lowercase, camelCase/PascalCase, but reject random patterns
        if not (cleaned.isupper() or cleaned.islower() or cleaned.istitle()):
            # Check if it's a valid compound with Title Case Words
            words = cleaned.split()
            if len(words) > 1:
                # Each word should be title case or uppercase
                if not all(word.istitle() or word.isupper() for word in words):
                    return False, "Invalid capitalization pattern"
            else:
                # Single word with mixed case that's not title case
                # Check if it has alternating caps (more than 3 case changes)
                case_changes = 0
                for i in range(len(cleaned) - 1):
                    if cleaned[i].isupper() != cleaned[i + 1].isupper():
                        case_changes += 1

                # Allow camelCase/PascalCase (1-3 changes) but reject random patterns (4+ changes)
                # Examples: JavaScript (2), PostgreSQL (3), DaTaBaSe (4 - reject)
                if case_changes >= 4:
                    return False, "Invalid capitalization pattern (random case)"

        return True, ""

    def batch_validate(self, terms: List[str]) -> Dict[str, List[str]]:
        """
        Validate multiple terms and categorize them

        Args:
            terms: List of terms to validate

        Returns:
            Dictionary with "valid" and "invalid" lists, plus rejection reasons
        """
        valid_terms = []
        invalid_terms = []
        rejection_reasons = {}

        for term in terms:
            if self.is_valid_term(term):
                valid_terms.append(term)
            else:
                invalid_terms.append(term)
                rejection_reasons[term] = self.get_rejection_reason(term)

        return {
            "valid": valid_terms,
            "invalid": invalid_terms,
            "rejection_reasons": rejection_reasons,
            "total": len(terms),
            "valid_count": len(valid_terms),
            "invalid_count": len(invalid_terms)
        }


# Factory functions for common configurations

def create_strict_validator(language: str = LANG_ENGLISH) -> TermValidator:
    """
    Create a validator with strict rules

    Args:
        language: Language code ('en' or 'de')

    Returns:
        TermValidator with strict configuration
    """
    config = ValidationConfig(
        min_term_length=STRICT_MIN_TERM_LENGTH,
        max_term_length=STRICT_MAX_TERM_LENGTH,
        min_word_count=STRICT_MIN_WORD_COUNT,
        max_word_count=STRICT_MAX_WORD_COUNT,
        max_symbol_ratio=STRICT_MAX_SYMBOL_RATIO,
        reject_pure_numbers=REJECT_PURE_NUMBERS,
        reject_percentages=REJECT_PERCENTAGES,
        allow_all_uppercase=ALLOW_ALL_UPPERCASE,
        min_acronym_length=STRICT_MIN_ACRONYM_LENGTH,
        max_acronym_length=STRICT_MAX_ACRONYM_LENGTH,
        language=language
    )
    return TermValidator(config)


def create_lenient_validator(language: str = LANG_ENGLISH) -> TermValidator:
    """
    Create a validator with lenient rules

    Args:
        language: Language code ('en' or 'de')

    Returns:
        TermValidator with lenient configuration
    """
    config = ValidationConfig(
        min_term_length=LENIENT_MIN_TERM_LENGTH,
        max_term_length=LENIENT_MAX_TERM_LENGTH,
        min_word_count=LENIENT_MIN_WORD_COUNT,
        max_word_count=LENIENT_MAX_WORD_COUNT,
        max_symbol_ratio=LENIENT_MAX_SYMBOL_RATIO,
        reject_pure_numbers=REJECT_PURE_NUMBERS,
        reject_percentages=REJECT_PERCENTAGES,
        allow_all_uppercase=ALLOW_ALL_UPPERCASE,
        min_acronym_length=LENIENT_MIN_ACRONYM_LENGTH,
        max_acronym_length=LENIENT_MAX_ACRONYM_LENGTH,
        language=language
    )
    return TermValidator(config)


def create_default_validator(language: str = LANG_ENGLISH) -> TermValidator:
    """
    Create a validator with default balanced rules

    Args:
        language: Language code ('en' or 'de')

    Returns:
        TermValidator with default configuration
    """
    config = ValidationConfig(language=language)
    return TermValidator(config)
