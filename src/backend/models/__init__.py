"""
Models package for the Glossary API
Contains additional SQLAlchemy ORM models

Note: This is models/ directory. The main models (Base, GlossaryEntry, etc.)
are in base_models.py file at the parent level.
"""

# TermRelationship is defined in this package
# It imports Base from ../base_models.py
from .relationship import TermRelationship

__all__ = ['TermRelationship']
