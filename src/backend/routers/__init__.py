# Makes routers a Python package
# Explicit imports to ensure proper loading
from . import glossary, documents, admin

__all__ = ['glossary', 'documents', 'admin']
