"""
NLP package for relationship extraction
Contains spaCy-based NLP processing for extracting semantic relationships
"""

from .relationship_extractor import RelationshipExtractor, RelationType

__all__ = ['RelationshipExtractor', 'RelationType']
