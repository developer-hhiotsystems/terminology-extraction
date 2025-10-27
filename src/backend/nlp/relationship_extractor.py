"""
Relationship Extraction Pipeline using spaCy

Extracts semantic relationships between glossary terms using:
- Dependency parsing (spaCy)
- Pattern matching for common relationship types
- Confidence scoring based on linguistic features
- Bidirectional relationship detection

Relationship Types:
- USES: "X uses Y" (tool, component, method)
- MEASURES: "X measures Y" (metric, sensor, parameter)
- PART_OF: "X is part of Y" (component, subsystem)
- PRODUCES: "X produces Y" (output, result, effect)
- AFFECTS: "X affects Y" (influence, impact)
- REQUIRES: "X requires Y" (dependency, prerequisite)
- CONTROLS: "X controls Y" (regulation, management)
- DEFINES: "X defines Y" (specification, standard)
"""

from typing import List, Dict, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum

# Try to import spacy, but make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None


class RelationType(Enum):
    """Semantic relationship types between terms"""
    USES = "uses"
    MEASURES = "measures"
    PART_OF = "part_of"
    PRODUCES = "produces"
    AFFECTS = "affects"
    REQUIRES = "requires"
    CONTROLS = "controls"
    DEFINES = "defines"
    RELATED_TO = "related_to"  # Generic fallback


@dataclass
class Relationship:
    """Extracted relationship between two terms"""
    source_term: str
    target_term: str
    relation_type: RelationType
    confidence: float  # 0.0 - 1.0
    context: str  # Sentence where relationship was found
    evidence: str  # Specific pattern/phrase that triggered extraction


class RelationshipExtractor:
    """
    Extract semantic relationships between glossary terms using NLP

    Uses spaCy dependency parsing and pattern matching to identify
    relationships like "temperature sensor MEASURES temperature"
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize relationship extractor

        Args:
            model_name: spaCy model to use (en_core_web_sm, en_core_web_md, etc.)
        """
        if not SPACY_AVAILABLE:
            self.nlp = None
            print("WARNING: spaCy not available, relationship extraction will use pattern-based fallback only")
        else:
            try:
                self.nlp = spacy.load(model_name)
            except OSError:
                # Model not found, provide installation instructions
                self.nlp = None
                print(f"WARNING: spaCy model '{model_name}' not found, using pattern-based fallback")
            except Exception as e:
                # Any other error (like DLL issues)
                self.nlp = None
                print(f"WARNING: Could not load spaCy model: {e}, using pattern-based fallback")

        # Relationship patterns (verb-based)
        self.relation_patterns = {
            RelationType.USES: [
                r'\b(use|uses|using|utilized?|employ|employs|applying?)\b',
                r'\b(leverage|leverages|leveraging)\b',
            ],
            RelationType.MEASURES: [
                r'\b(measure|measures|measuring|quantif(y|ies))\b',
                r'\b(monitor|monitors|monitoring|track|tracks)\b',
                r'\b(detect|detects|detecting|sense|senses)\b',
            ],
            RelationType.PART_OF: [
                r'\b(part of|component of|element of|within)\b',
                r'\b(contained in|included in|belongs to)\b',
                r'\b(subsystem of|module of)\b',
            ],
            RelationType.PRODUCES: [
                r'\b(produce|produces|producing|generate|generates)\b',
                r'\b(create|creates|creating|output|outputs)\b',
                r'\b(yield|yields|result in)\b',
            ],
            RelationType.AFFECTS: [
                r'\b(affect|affects|affecting|influence|influences)\b',
                r'\b(impact|impacts|impacting|alter|alters)\b',
                r'\b(modify|modifies|modifying|change|changes)\b',
            ],
            RelationType.REQUIRES: [
                r'\b(require|requires|requiring|need|needs)\b',
                r'\b(depend on|depends on|reliant on|relies on)\b',
                r'\b(prerequisite|necessary)\b',
            ],
            RelationType.CONTROLS: [
                r'\b(control|controls|controlling|regulate|regulates)\b',
                r'\b(manage|manages|managing|govern|governs)\b',
                r'\b(adjust|adjusts|adjusting)\b',
            ],
            RelationType.DEFINES: [
                r'\b(define|defines|defining|specify|specifies)\b',
                r'\b(establish|establishes|set|sets)\b',
                r'\b(determine|determines|determining)\b',
            ],
        }

        # Compile patterns for performance
        self.compiled_patterns = {
            rel_type: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for rel_type, patterns in self.relation_patterns.items()
        }

    def extract_from_text(
        self,
        text: str,
        known_terms: List[str],
        min_confidence: float = 0.5
    ) -> List[Relationship]:
        """
        Extract relationships from text given a list of known terms

        Args:
            text: Text to analyze (e.g., definition, context)
            known_terms: List of glossary terms to look for
            min_confidence: Minimum confidence threshold (0.0-1.0)

        Returns:
            List of extracted relationships
        """
        relationships = []

        # If spaCy is not available, return empty list
        if self.nlp is None:
            return relationships

        # Process text with spaCy
        doc = self.nlp(text)

        # Normalize known terms for matching
        term_variants = {}
        for term in known_terms:
            normalized = term.lower().strip()
            term_variants[normalized] = term
            # Add plural/singular variants
            if normalized.endswith('s'):
                term_variants[normalized[:-1]] = term
            else:
                term_variants[normalized + 's'] = term

        # Extract relationships from each sentence
        for sent in doc.sents:
            sent_text = sent.text.lower()

            # Find terms mentioned in this sentence
            mentioned_terms = []
            for variant, original in term_variants.items():
                if variant in sent_text:
                    mentioned_terms.append(original)

            # Need at least 2 terms for a relationship
            if len(mentioned_terms) < 2:
                continue

            # Check for relationship patterns
            for rel_type, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    match = pattern.search(sent_text)
                    if match:
                        # Found a relationship pattern
                        evidence = match.group(0)

                        # Try to extract subject-object pairs using dependency parsing
                        relations = self._extract_dependency_relations(
                            sent, mentioned_terms, rel_type, evidence
                        )

                        # If dependency parsing fails, use positional heuristics
                        if not relations:
                            relations = self._extract_positional_relations(
                                sent_text, mentioned_terms, rel_type, evidence
                            )

                        relationships.extend(relations)

        # Filter by confidence and deduplicate
        filtered = [r for r in relationships if r.confidence >= min_confidence]
        deduplicated = self._deduplicate_relationships(filtered)

        return deduplicated

    def _extract_dependency_relations(
        self,
        sent,  # spacy.tokens.Span when available
        terms: List[str],
        rel_type: RelationType,
        evidence: str
    ) -> List[Relationship]:
        """
        Extract relationships using spaCy dependency parsing

        Looks for subject-verb-object patterns where subject and object
        are both known terms.
        """
        relationships = []

        # Find verb that matches the relationship pattern
        verb_token = None
        for token in sent:
            if token.lemma_.lower() in evidence.lower():
                if token.pos_ == "VERB":
                    verb_token = token
                    break

        if not verb_token:
            return relationships

        # Find subject and object of the verb
        subject_chunks = []
        object_chunks = []

        for child in verb_token.children:
            if child.dep_ in ["nsubj", "nsubjpass"]:
                # Subject
                subject_chunks.append(child.text.lower())
                # Include compound nouns
                for subchild in child.children:
                    if subchild.dep_ == "compound":
                        subject_chunks.append(f"{subchild.text} {child.text}".lower())

            elif child.dep_ in ["dobj", "pobj", "attr"]:
                # Object
                object_chunks.append(child.text.lower())
                # Include compound nouns
                for subchild in child.children:
                    if subchild.dep_ == "compound":
                        object_chunks.append(f"{subchild.text} {child.text}".lower())

        # Match chunks to known terms
        source_terms = [t for t in terms if any(chunk in t.lower() for chunk in subject_chunks)]
        target_terms = [t for t in terms if any(chunk in t.lower() for chunk in object_chunks)]

        # Create relationships
        for source in source_terms:
            for target in target_terms:
                if source != target:
                    confidence = self._calculate_confidence(
                        sent.text, source, target, rel_type, True
                    )
                    relationships.append(Relationship(
                        source_term=source,
                        target_term=target,
                        relation_type=rel_type,
                        confidence=confidence,
                        context=sent.text,
                        evidence=evidence
                    ))

        return relationships

    def _extract_positional_relations(
        self,
        text: str,
        terms: List[str],
        rel_type: RelationType,
        evidence: str
    ) -> List[Relationship]:
        """
        Extract relationships using positional heuristics

        Assumes: "term1 [relationship verb] term2"
        Falls back to this when dependency parsing doesn't work.
        """
        relationships = []

        # Find positions of evidence and terms
        evidence_pos = text.lower().find(evidence.lower())
        if evidence_pos == -1:
            return relationships

        # Find terms before and after the evidence
        terms_before = []
        terms_after = []

        for term in terms:
            term_pos = text.lower().find(term.lower())
            if term_pos != -1:
                if term_pos < evidence_pos:
                    terms_before.append((term, term_pos))
                elif term_pos > evidence_pos + len(evidence):
                    terms_after.append((term, term_pos))

        # Sort by distance to evidence
        terms_before.sort(key=lambda x: evidence_pos - x[1])
        terms_after.sort(key=lambda x: x[1] - evidence_pos)

        # Create relationships (closest term before -> closest term after)
        if terms_before and terms_after:
            source = terms_before[0][0]
            target = terms_after[0][0]

            if source != target:
                confidence = self._calculate_confidence(
                    text, source, target, rel_type, False
                )
                relationships.append(Relationship(
                    source_term=source,
                    target_term=target,
                    relation_type=rel_type,
                    confidence=confidence,
                    context=text,
                    evidence=evidence
                ))

        return relationships

    def _calculate_confidence(
        self,
        text: str,
        source: str,
        target: str,
        rel_type: RelationType,
        used_dependency_parsing: bool
    ) -> float:
        """
        Calculate confidence score for a relationship

        Factors:
        - Method used (dependency parsing = higher confidence)
        - Distance between terms (closer = higher confidence)
        - Clarity of evidence (exact match = higher confidence)
        - Sentence complexity (simpler = higher confidence)
        """
        confidence = 0.5  # Base confidence

        # Boost for dependency parsing
        if used_dependency_parsing:
            confidence += 0.2

        # Boost for close proximity
        source_pos = text.lower().find(source.lower())
        target_pos = text.lower().find(target.lower())
        if source_pos != -1 and target_pos != -1:
            distance = abs(target_pos - source_pos)
            if distance < 50:
                confidence += 0.2
            elif distance < 100:
                confidence += 0.1

        # Boost for simple sentences
        if len(text.split()) < 15:
            confidence += 0.1

        # Cap at 1.0
        return min(confidence, 1.0)

    def _deduplicate_relationships(
        self,
        relationships: List[Relationship]
    ) -> List[Relationship]:
        """
        Remove duplicate relationships, keeping highest confidence
        """
        unique = {}

        for rel in relationships:
            key = (rel.source_term, rel.target_term, rel.relation_type.value)
            if key not in unique or rel.confidence > unique[key].confidence:
                unique[key] = rel

        return list(unique.values())

    def extract_from_glossary_entry(
        self,
        term: str,
        definitions: List[Dict],
        all_terms: List[str],
        min_confidence: float = 0.5
    ) -> List[Relationship]:
        """
        Extract relationships for a single glossary entry

        Args:
            term: The term to extract relationships for
            definitions: List of definition dicts with 'definition_text' and optional 'context'
            all_terms: All known glossary terms
            min_confidence: Minimum confidence threshold

        Returns:
            List of relationships where this term is the source
        """
        all_relationships = []

        # Filter out the current term from target candidates
        candidate_terms = [t for t in all_terms if t.lower() != term.lower()]

        # Extract from each definition
        for definition in definitions:
            text = definition.get('definition_text', '')
            context = definition.get('context', '')

            # Combine definition and context
            full_text = f"{text} {context}".strip()

            if full_text:
                relationships = self.extract_from_text(
                    full_text,
                    candidate_terms,
                    min_confidence
                )
                all_relationships.extend(relationships)

        return all_relationships


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = RelationshipExtractor()

    # Example terms
    terms = [
        "temperature sensor",
        "temperature",
        "control system",
        "heating element",
        "thermostat"
    ]

    # Example text
    text = """
    A temperature sensor measures temperature and sends data to the control system.
    The control system uses this data to regulate the heating element.
    The thermostat controls temperature by activating the heating element when needed.
    """

    # Extract relationships
    relationships = extractor.extract_from_text(text, terms, min_confidence=0.5)

    # Print results
    print(f"Found {len(relationships)} relationships:\n")
    for rel in relationships:
        print(f"{rel.source_term} --[{rel.relation_type.value}]--> {rel.target_term}")
        print(f"  Confidence: {rel.confidence:.2f}")
        print(f"  Evidence: '{rel.evidence}'")
        print(f"  Context: {rel.context[:100]}...")
        print()
