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

    # Article lists for English and German
    ENGLISH_ARTICLES = {'the', 'a', 'an'}
    GERMAN_ARTICLES = {'der', 'die', 'das', 'ein', 'eine', 'einer', 'eines', 'einem', 'einen'}

    @staticmethod
    def strip_leading_articles(term: str, language: str = 'en') -> str:
        """
        Strip leading articles from terms

        This prevents terms like "The Sensor" or "Die Temperatur" from being
        extracted. Articles are removed DURING extraction to prevent bad data.

        Args:
            term: Term that may start with article
            language: 'en' for English or 'de' for German

        Returns:
            Term with leading article removed

        Examples:
            >>> TermExtractor.strip_leading_articles("The Sensor", "en")
            "Sensor"
            >>> TermExtractor.strip_leading_articles("Die Temperatur", "de")
            "Temperatur"
            >>> TermExtractor.strip_leading_articles("A Process Flow", "en")
            "Process Flow"
        """
        if not term:
            return term

        # Select article set based on language
        articles = (TermExtractor.ENGLISH_ARTICLES if language == 'en'
                   else TermExtractor.GERMAN_ARTICLES)

        # Split into words
        words = term.split()

        # If first word is an article and there's more than one word, remove it
        if len(words) > 1 and words[0].lower() in articles:
            return ' '.join(words[1:])

        return term

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
            # ✅ STRIP ARTICLES DURING EXTRACTION
            term = self.strip_leading_articles(term, self.language)
            if term and min_term_length <= len(term) <= max_term_length:
                candidates.add(term.lower())

        # Named entities (technical terms often appear as entities)
        for ent in doc.ents:
            term = self.clean_term(ent.text)
            # ✅ STRIP ARTICLES DURING EXTRACTION
            term = self.strip_leading_articles(term, self.language)
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
                # ✅ STRIP ARTICLES DURING EXTRACTION (pattern-based too)
                cleaned_match = self.strip_leading_articles(cleaned_match, self.language)
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

    def _extract_definition_from_context(self, term: str, text: str, complete_sentence: str = "") -> Optional[Dict[str, any]]:
        """
        Use NLP patterns to intelligently extract definitions from text

        Phase 2: NLP-based definition extraction using linguistic patterns

        Looks for:
        - Definitional verbs: "term is...", "term means...", "term refers to..."
        - Appositive phrases: "term, definition, ..."
        - Parenthetical definitions: "term (definition)"
        - Colon-based definitions: "term: definition"

        Args:
            term: The term to find definition for
            text: Full text to search
            complete_sentence: The sentence containing the term

        Returns:
            Dict with 'definition', 'confidence', 'pattern' or None if not found
        """
        if not text:
            return None

        term_lower = term.lower()
        candidates = []

        # Pattern 1: Definitional verbs - "Term is/means/refers to..."
        definitional_patterns = [
            (r'\b' + re.escape(term_lower) + r'\s+is\s+(?:the\s+)?(.+?)(?:[.!?]|$)', 0.95, 'is-definition'),
            (r'\b' + re.escape(term_lower) + r'\s+are\s+(?:the\s+)?(.+?)(?:[.!?]|$)', 0.95, 'are-definition'),
            (r'\b' + re.escape(term_lower) + r'\s+means\s+(.+?)(?:[.!?]|$)', 0.90, 'means-definition'),
            (r'\b' + re.escape(term_lower) + r'\s+refers?\s+to\s+(.+?)(?:[.!?]|$)', 0.90, 'refers-to'),
            (r'\b' + re.escape(term_lower) + r'\s+represents?\s+(.+?)(?:[.!?]|$)', 0.85, 'represents'),
            (r'\b' + re.escape(term_lower) + r'\s+denotes?\s+(.+?)(?:[.!?]|$)', 0.85, 'denotes'),
            (r'\b' + re.escape(term_lower) + r'\s+describes?\s+(.+?)(?:[.!?]|$)', 0.80, 'describes'),
            (r'\b' + re.escape(term_lower) + r'\s+defines?\s+(.+?)(?:[.!?]|$)', 0.90, 'defines'),
        ]

        text_lower = text.lower()

        for pattern, confidence, pattern_type in definitional_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                definition = match.group(1).strip()
                # Get the original case version from the text
                start_pos = match.start(1)
                end_pos = match.end(1)
                definition_original = text[start_pos:end_pos].strip()

                # Clean up common artifacts
                definition_original = definition_original.rstrip('.!?,;:')

                # Skip if definition is too short or just a continuation
                if len(definition_original) < 10:
                    continue

                candidates.append({
                    'definition': definition_original,
                    'confidence': confidence,
                    'pattern': pattern_type,
                    'full_match': match.group(0)
                })

        # Pattern 2: Parenthetical definitions - "Term (definition)"
        paren_pattern = r'\b' + re.escape(term) + r'\s*\(([^)]{10,150})\)'
        paren_matches = re.finditer(paren_pattern, text, re.IGNORECASE)
        for match in paren_matches:
            definition = match.group(1).strip()
            # Skip if it looks like an acronym expansion in wrong direction
            if not definition.isupper() or len(definition) > 10:
                candidates.append({
                    'definition': definition,
                    'confidence': 0.75,
                    'pattern': 'parenthetical',
                    'full_match': match.group(0)
                })

        # Pattern 3: Colon-based definitions - "Term: definition"
        colon_pattern = r'\b' + re.escape(term) + r'\s*:\s*(.{10,200})(?:[.!?]|$)'
        colon_matches = re.finditer(colon_pattern, text, re.IGNORECASE)
        for match in colon_matches:
            definition = match.group(1).strip().rstrip('.!?,;:')
            candidates.append({
                'definition': definition,
                'confidence': 0.85,
                'pattern': 'colon-definition',
                'full_match': match.group(0)
            })

        # Pattern 4: Appositive phrases with spaCy (if available)
        if self.nlp and SPACY_AVAILABLE:
            try:
                doc = self.nlp(complete_sentence if complete_sentence else text[:1000])

                for token in doc:
                    # Find the term's token
                    if token.text.lower() == term.split()[0].lower():
                        # Look for appositive children
                        for child in token.children:
                            if child.dep_ in ['appos', 'attr']:  # Appositive or attribute
                                # Extract the appositive subtree
                                appos_tokens = [t.text for t in child.subtree]
                                definition = ' '.join(appos_tokens)

                                if len(definition) >= 10:
                                    candidates.append({
                                        'definition': definition,
                                        'confidence': 0.88,
                                        'pattern': 'appositive-spacy',
                                        'full_match': definition
                                    })
            except Exception as e:
                logger.debug(f"spaCy appositive extraction failed: {e}")

        # Return highest confidence candidate
        if candidates:
            best = max(candidates, key=lambda x: x['confidence'])

            # Only return if confidence is above threshold
            if best['confidence'] >= 0.75:
                logger.info(f"NLP definition found for '{term}': pattern={best['pattern']}, confidence={best['confidence']:.2f}")
                return best

        return None

    def generate_definition(self, term: str, context: str, complete_sentence: str = "", page_numbers: Optional[List[int]] = None, full_text: str = "") -> str:
        """
        Generate definition using NLP patterns (Phase 2) with fallback to context (Phase 1)

        Tries NLP-based definition extraction first, then falls back to complete sentence.

        Args:
            term: The term to define
            context: Context where term appears (for backward compatibility)
            complete_sentence: Complete sentence containing the term
            page_numbers: List of page numbers where term appears
            full_text: Full document text for NLP pattern matching (Phase 2)

        Returns:
            Generated definition with page numbers
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

        # Phase 2: Try NLP-based definition extraction
        if full_text:
            nlp_result = self._extract_definition_from_context(term, full_text, complete_sentence)
            if nlp_result:
                confidence_indicator = "✓" if nlp_result['confidence'] >= 0.9 else "~"
                return f"Definition{page_text}:\n\n{nlp_result['definition']}\n\n{confidence_indicator} Extracted using {nlp_result['pattern']} pattern"

        # Phase 1 fallback: Use complete sentence if available
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
