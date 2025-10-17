"""
NLP-based term extraction service using spaCy
Extracts technical terminology from text for glossary creation
"""
import re
from typing import List, Dict, Set, Optional
from collections import Counter
import logging

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

    def __init__(self, language: str = "en"):
        """
        Initialize term extractor

        Args:
            language: Language code ('en' or 'de')
        """
        self.language = language
        self.nlp = None

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
        include_compound: bool = True
    ) -> List[Dict[str, any]]:
        """
        Extract technical terms from text

        Args:
            text: Input text
            min_term_length: Minimum term length in characters
            max_term_length: Maximum term length in characters
            min_frequency: Minimum frequency for a term to be included
            include_compound: Include compound terms (multi-word)

        Returns:
            List of dictionaries with term, frequency, and context
        """
        if self.nlp:
            return self._extract_with_spacy(text, min_term_length, max_term_length, min_frequency, include_compound)
        else:
            return self._extract_with_patterns(text, min_term_length, max_term_length, min_frequency)

    def _extract_with_spacy(
        self,
        text: str,
        min_term_length: int,
        max_term_length: int,
        min_frequency: int,
        include_compound: bool
    ) -> List[Dict[str, any]]:
        """Extract terms using spaCy NLP"""
        doc = self.nlp(text)

        # Extract noun phrases and named entities
        candidates = set()

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

        # Count frequencies
        term_freq = Counter()
        text_lower = text.lower()
        for term in candidates:
            count = text_lower.count(term)
            if count >= min_frequency:
                term_freq[term] = count

        # Build result with context
        results = []
        for term, freq in term_freq.most_common():
            # Find first occurrence for context
            context = self._extract_context(text, term)
            results.append({
                "term": term.title(),  # Capitalize for presentation
                "frequency": freq,
                "context": context,
                "length": len(term)
            })

        return results

    def _extract_with_patterns(
        self,
        text: str,
        min_term_length: int,
        max_term_length: int,
        min_frequency: int
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
                if min_term_length <= len(match) <= max_term_length:
                    candidates.add(match)

        # Count frequencies
        term_freq = Counter()
        for term in candidates:
            count = text.count(term)
            if count >= min_frequency:
                term_freq[term] = count

        # Build results
        results = []
        for term, freq in term_freq.most_common():
            context = self._extract_context(text, term)
            results.append({
                "term": term,
                "frequency": freq,
                "context": context,
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

    def generate_definition(self, term: str, context: str) -> str:
        """
        Generate a basic definition from context
        (Placeholder for future ML-based definition generation)

        Args:
            term: The term to define
            context: Context where term appears

        Returns:
            Generated definition
        """
        # Basic implementation: use context as definition
        if context:
            return f"Technical term found in context: {context[:200]}"
        else:
            return f"Technical term: {term}"
