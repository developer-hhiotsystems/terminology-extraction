"""
NLP-based term extraction service using spaCy
Extracts technical terminology from text for glossary creation
"""
import re
from typing import List, Dict, Set, Optional
from collections import Counter
import logging

from .term_validator import TermValidator, ValidationConfig, create_default_validator

logger = logging.getLogger(__name__)

# Will use spaCy when available, fallback to pattern matching for now
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available, using pattern-based extraction")


class TermExtractor:
    """Service for extracting technical terms from text"""

    @staticmethod
    def clean_term(term: str) -> str:
        """
        Clean and normalize a term to fix formatting issues

        Removes embedded newlines, tabs, carriage returns, and normalizes spaces.

        Args:
            term: The term to clean

        Returns:
            Cleaned term with normalized whitespace

        Examples:
            >>> TermExtractor.clean_term("Plant\\nDesign")
            "Plant Design"
            >>> TermExtractor.clean_term("Process  Flow\\tDiagram")
            "Process Flow Diagram"
        """
        if not term:
            return term

        # Remove embedded newlines, tabs, carriage returns
        term = re.sub(r'[\n\t\r]+', ' ', term)

        # Normalize multiple spaces to single space
        term = ' '.join(term.split())

        return term.strip()

    def __init__(self, language: str = "en", validator: Optional[TermValidator] = None):
        """
        Initialize term extractor

        Args:
            language: Language code ('en' or 'de')
            validator: Optional term validator. If not provided, uses default validator.
        """
        self.language = language
        self.nlp = None
        self.validator = validator or create_default_validator(language)

        if SPACY_AVAILABLE:
            try:
                # Load spaCy model based on language
                model_name = "en_core_web_sm" if language == "en" else "de_core_news_sm"
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}, using pattern-based extraction")
                self.nlp = None

    def extract_terms(
        self,
        text: str,
        min_term_length: int = 3,
        max_term_length: int = 50,
        min_frequency: int = 2,
        include_compound: bool = True,
        pages_data: Optional[List[Dict[str, any]]] = None,
        enable_validation: bool = True
    ) -> List[Dict[str, any]]:
        """
        Extract technical terms from text

        Args:
            text: Input text
            min_term_length: Minimum term length in characters
            max_term_length: Maximum term length in characters
            min_frequency: Minimum frequency for a term to be included
            include_compound: Include compound terms (multi-word)
            pages_data: Optional list of page data with page_num and text
            enable_validation: Enable term validation to filter low-quality terms

        Returns:
            List of dictionaries with term, frequency, context, and page numbers
        """
        if self.nlp:
            return self._extract_with_spacy(text, min_term_length, max_term_length, min_frequency, include_compound, pages_data, enable_validation)
        else:
            return self._extract_with_patterns(text, min_term_length, max_term_length, min_frequency, pages_data, enable_validation)

    def _extract_with_spacy(
        self,
        text: str,
        min_term_length: int,
        max_term_length: int,
        min_frequency: int,
        include_compound: bool,
        pages_data: Optional[List[Dict[str, any]]] = None,
        enable_validation: bool = True
    ) -> List[Dict[str, any]]:
        """Extract terms using spaCy NLP"""
        doc = self.nlp(text)

        # Extract noun phrases and named entities
        candidates = set()

        # Noun phrases
        for chunk in doc.noun_chunks:
            term = self.clean_term(chunk.text)
            if term and min_term_length <= len(term) <= max_term_length:
                candidates.add(term.lower())

        # Named entities (technical terms often appear as entities)
        for ent in doc.ents:
            term = self.clean_term(ent.text)
            if term and min_term_length <= len(term) <= max_term_length:
                candidates.add(term.lower())

        # Count frequencies
        term_freq = Counter()
        text_lower = text.lower()
        rejected_count = 0
        rejection_reasons = {}

        for term in candidates:
            count = text_lower.count(term)
            if count >= min_frequency:
                # Validate term if validation is enabled
                if enable_validation:
                    if self.validator.is_valid_term(term):
                        term_freq[term] = count
                    else:
                        rejected_count += 1
                        rejection_reasons[term] = self.validator.get_rejection_reason(term)
                else:
                    term_freq[term] = count

        # Log validation results
        if enable_validation and rejected_count > 0:
            logger.info(f"Validation filtered out {rejected_count} low-quality terms")
            logger.debug(f"Rejection reasons: {rejection_reasons}")

        # Build result with context, complete sentences, and page numbers
        results = []
        for term, freq in term_freq.most_common():
            # Find first occurrence for context
            context = self._extract_context(text, term)
            complete_sentence = self._extract_complete_sentence(text, term)

            # Find pages where term appears
            page_numbers = self._find_term_pages(term, pages_data) if pages_data else []

            results.append({
                "term": term.title(),  # Capitalize for presentation
                "frequency": freq,
                "context": context,
                "complete_sentence": complete_sentence,
                "pages": page_numbers,
                "length": len(term)
            })

        return results

    def _extract_with_patterns(
        self,
        text: str,
        min_term_length: int,
        max_term_length: int,
        min_frequency: int,
        pages_data: Optional[List[Dict[str, any]]] = None,
        enable_validation: bool = True
    ) -> List[Dict[str, any]]:
        """Extract terms using pattern matching (fallback when spaCy unavailable)"""

        # Pattern for technical terms: capitalized words, compound terms, acronyms
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized terms
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)+\b',  # Hyphenated terms
        ]

        candidates = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                cleaned_match = self.clean_term(match)
                if cleaned_match and min_term_length <= len(cleaned_match) <= max_term_length:
                    candidates.add(cleaned_match)

        # Count frequencies
        term_freq = Counter()
        rejected_count = 0
        rejection_reasons = {}

        for term in candidates:
            count = text.count(term)
            if count >= min_frequency:
                # Validate term if validation is enabled
                if enable_validation:
                    if self.validator.is_valid_term(term):
                        term_freq[term] = count
                    else:
                        rejected_count += 1
                        rejection_reasons[term] = self.validator.get_rejection_reason(term)
                else:
                    term_freq[term] = count

        # Log validation results
        if enable_validation and rejected_count > 0:
            logger.info(f"Validation filtered out {rejected_count} low-quality terms")
            logger.debug(f"Rejection reasons: {rejection_reasons}")

        # Build results with page numbers
        results = []
        for term, freq in term_freq.most_common():
            context = self._extract_context(text, term)
            complete_sentence = self._extract_complete_sentence(text, term)

            # Find pages where term appears
            page_numbers = self._find_term_pages(term, pages_data) if pages_data else []

            results.append({
                "term": term,
                "frequency": freq,
                "context": context,
                "complete_sentence": complete_sentence,
                "pages": page_numbers,
                "length": len(term)
            })

        return results

    def _extract_context(self, text: str, term: str, context_length: int = 100) -> str:
        """Extract context around the first occurrence of a term"""
        text_lower = text.lower()
        term_lower = term.lower()

        pos = text_lower.find(term_lower)
        if pos == -1:
            return ""

        start = max(0, pos - context_length // 2)
        end = min(len(text), pos + len(term) + context_length // 2)

        context = text[start:end].strip()
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context

    def _extract_complete_sentence(self, text: str, term: str) -> str:
        """
        Extract complete sentence(s) containing the term

        Args:
            text: Full text to search
            term: Term to find

        Returns:
            Complete sentence(s) containing the term
        """
        text_lower = text.lower()
        term_lower = term.lower()

        pos = text_lower.find(term_lower)
        if pos == -1:
            return ""

        # Find sentence boundaries (., !, ?, or newline)
        # Look backward for sentence start
        sentence_start = 0
        for i in range(pos - 1, -1, -1):
            if text[i] in '.!?\n':
                sentence_start = i + 1
                break

        # Look forward for sentence end
        sentence_end = len(text)
        for i in range(pos + len(term), len(text)):
            if text[i] in '.!?':
                sentence_end = i + 1
                break
            elif text[i] == '\n' and i - pos > 50:  # New line after reasonable distance
                sentence_end = i
                break

        sentence = text[sentence_start:sentence_end].strip()

        # If sentence is too long (> 300 chars), try to find a better break point
        if len(sentence) > 300:
            # Look for semicolon or comma after the term
            term_end_pos = pos + len(term) - sentence_start
            for i in range(term_end_pos, min(term_end_pos + 150, len(sentence))):
                if sentence[i] in '.!?;':
                    sentence = sentence[:i + 1]
                    break

        return sentence

    def generate_definition(self, term: str, context: str, complete_sentence: str = "", page_numbers: Optional[List[int]] = None) -> str:
        """
        Generate a basic definition from context
        (Placeholder for future ML-based definition generation)

        Args:
            term: The term to define
            context: Context where term appears (for backward compatibility)
            complete_sentence: Complete sentence containing the term
            page_numbers: List of page numbers where term appears

        Returns:
            Generated definition
        """
        # Build page number text if available
        page_text = ""
        if page_numbers and len(page_numbers) > 0:
            if len(page_numbers) == 1:
                page_text = f" (Page {page_numbers[0]})"
            elif len(page_numbers) <= 3:
                page_text = f" (Pages {', '.join(map(str, page_numbers))})"
            else:
                page_text = f" (Pages {', '.join(map(str, page_numbers[:3]))}, +{len(page_numbers) - 3} more)"

        # Use complete sentence if available, otherwise fall back to context
        if complete_sentence:
            return f"Term found in context{page_text}:\n\n{complete_sentence}"
        elif context:
            return f"Term found in context{page_text}:\n\n{context[:250]}"
        else:
            return f"Technical term: {term}"

    def _find_term_pages(self, term: str, pages_data: Optional[List[Dict[str, any]]]) -> List[int]:
        """
        Find which pages contain a given term

        Args:
            term: The term to search for
            pages_data: List of dicts with page_num and text

        Returns:
            List of page numbers where the term appears
        """
        if not pages_data:
            return []

        page_numbers = []
        term_lower = term.lower()

        for page in pages_data:
            page_text = page.get("text", "").lower()
            if term_lower in page_text:
                page_numbers.append(page.get("page_num"))

        return sorted(page_numbers)
