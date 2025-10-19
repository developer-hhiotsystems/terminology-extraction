"""
Application Constants Module

Central repository for all application constants to eliminate magic strings
and provide a single source of truth for configuration values.

This module is organized into logical sections for easy maintenance.
"""

# =============================================================================
# LANGUAGE CONSTANTS
# =============================================================================

LANG_ENGLISH = "en"
LANG_GERMAN = "de"
SUPPORTED_LANGUAGES = [LANG_ENGLISH, LANG_GERMAN]
DEFAULT_LANGUAGE = LANG_ENGLISH

# Language regex pattern for validation
LANGUAGE_PATTERN = f"^({'|'.join(SUPPORTED_LANGUAGES)})$"  # "^(de|en)$"


# =============================================================================
# SOURCE CONSTANTS
# =============================================================================

SOURCE_INTERNAL = "internal"
SOURCE_NAMUR = "NAMUR"
SOURCE_DIN = "DIN"
SOURCE_ASME = "ASME"
SOURCE_IEC = "IEC"
SOURCE_IATE = "IATE"
SOURCE_PDF = "pdf"
SOURCE_MANUAL = "manual"

ALLOWED_SOURCES = [
    SOURCE_INTERNAL,
    SOURCE_NAMUR,
    SOURCE_DIN,
    SOURCE_ASME,
    SOURCE_IEC,
    SOURCE_IATE
]

DEFAULT_SOURCE = SOURCE_INTERNAL


# =============================================================================
# STATUS CONSTANTS
# =============================================================================

# Validation status
VALIDATION_STATUS_PENDING = "pending"
VALIDATION_STATUS_VALIDATED = "validated"
VALIDATION_STATUS_REJECTED = "rejected"

VALIDATION_STATUSES = [
    VALIDATION_STATUS_PENDING,
    VALIDATION_STATUS_VALIDATED,
    VALIDATION_STATUS_REJECTED
]

VALIDATION_STATUS_PATTERN = f"^({'|'.join(VALIDATION_STATUSES)})$"

# Sync status
SYNC_STATUS_PENDING = "pending_sync"
SYNC_STATUS_SYNCED = "synced"
SYNC_STATUS_FAILED = "sync_failed"

SYNC_STATUSES = [
    SYNC_STATUS_PENDING,
    SYNC_STATUS_SYNCED,
    SYNC_STATUS_FAILED
]

SYNC_STATUS_PATTERN = f"^({'|'.join(SYNC_STATUSES)})$"

# Upload/Processing status
UPLOAD_STATUS_PENDING = "pending"
UPLOAD_STATUS_PROCESSING = "processing"
UPLOAD_STATUS_COMPLETED = "completed"
UPLOAD_STATUS_FAILED = "failed"

UPLOAD_STATUSES = [
    UPLOAD_STATUS_PENDING,
    UPLOAD_STATUS_PROCESSING,
    UPLOAD_STATUS_COMPLETED,
    UPLOAD_STATUS_FAILED
]


# =============================================================================
# TERM VALIDATION CONSTANTS
# =============================================================================

# Default validation configuration (matches ValidationConfig defaults)
MIN_TERM_LENGTH = 3
MAX_TERM_LENGTH = 100
MIN_DEFINITION_LENGTH = 10

# Word count constraints
MIN_WORD_COUNT = 1
MAX_WORD_COUNT = 4

# Symbol/punctuation constraints
MAX_SYMBOL_RATIO = 0.3  # Max 30% symbols

# Capitalization rules for acronyms
MIN_ACRONYM_LENGTH = 2
MAX_ACRONYM_LENGTH = 8

# Validation flags
REJECT_PURE_NUMBERS = True
REJECT_PERCENTAGES = True
ALLOW_ALL_UPPERCASE = True

# Strict validator configuration
STRICT_MIN_TERM_LENGTH = 4
STRICT_MAX_TERM_LENGTH = 80
STRICT_MIN_WORD_COUNT = 1
STRICT_MAX_WORD_COUNT = 3
STRICT_MAX_SYMBOL_RATIO = 0.2
STRICT_MIN_ACRONYM_LENGTH = 2
STRICT_MAX_ACRONYM_LENGTH = 6

# Lenient validator configuration
LENIENT_MIN_TERM_LENGTH = 2
LENIENT_MAX_TERM_LENGTH = 150
LENIENT_MIN_WORD_COUNT = 1
LENIENT_MAX_WORD_COUNT = 6
LENIENT_MAX_SYMBOL_RATIO = 0.4
LENIENT_MIN_ACRONYM_LENGTH = 1
LENIENT_MAX_ACRONYM_LENGTH = 10


# =============================================================================
# FILE UPLOAD CONSTANTS
# =============================================================================

# Upload directory
UPLOAD_DIR = "./data/uploads"
DATABASE_DIR = "./data"

# File constraints
ALLOWED_EXTENSIONS = [".pdf"]
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB in bytes
MAX_FILE_SIZE_MB = 50

# Batch upload constraints
MAX_BATCH_SIZE = 20

# MIME types
MIME_TYPE_PDF = "application/pdf"
ALLOWED_MIME_TYPES = [MIME_TYPE_PDF]

# PDF magic bytes (for content validation)
PDF_MAGIC_BYTES = b'%PDF'


# =============================================================================
# PAGINATION CONSTANTS
# =============================================================================

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000
MIN_PAGE_SIZE = 1

DEFAULT_OFFSET = 0


# =============================================================================
# NEO4J CONSTANTS
# =============================================================================

NEO4J_TIMEOUT = 30  # seconds
NEO4J_MAX_RETRY = 3
NEO4J_RETRY_DELAY = 1  # seconds

# Neo4j relationship types
REL_USES = "USES"
REL_PART_OF = "PART_OF"
REL_RELATED_TO = "RELATED_TO"
REL_SYNONYM_OF = "SYNONYM_OF"
REL_TRANSLATION_OF = "TRANSLATION_OF"
REL_DERIVED_FROM = "DERIVED_FROM"


# =============================================================================
# DATABASE CONSTANTS
# =============================================================================

# Database URLs
DATABASE_URL_SQLITE = "sqlite:///./data/glossary.db"
DATABASE_URL_POSTGRESQL = "postgresql://glossary_user:glossary_password@localhost:5432/glossary"

# Database types
DB_TYPE_SQLITE = "sqlite"
DB_TYPE_POSTGRESQL = "postgresql"

# PostgreSQL connection settings
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "glossary"
POSTGRES_USER = "glossary_user"
POSTGRES_PASSWORD = "glossary_password"  # Change in production!

# Connection pool settings (PostgreSQL)
POSTGRES_POOL_SIZE = 5
POSTGRES_MAX_OVERFLOW = 10
POSTGRES_POOL_TIMEOUT = 30
POSTGRES_POOL_RECYCLE = 3600

# Index names (for reference)
IDX_GLOSSARY_TERM = "idx_glossary_term"
IDX_GLOSSARY_LANGUAGE = "idx_glossary_language"
IDX_GLOSSARY_SOURCE = "idx_glossary_source"
IDX_GLOSSARY_FTS_EN = "idx_glossary_fts_en"  # Full-text search English
IDX_GLOSSARY_FTS_DE = "idx_glossary_fts_de"  # Full-text search German
IDX_GLOSSARY_VALIDATION_STATUS = "idx_glossary_validation_status"
IDX_GLOSSARY_CREATED_AT = "idx_glossary_created_at"

# PostgreSQL-specific index names
IDX_DEFINITIONS_ENTRY_ID = "idx_definitions_entry_id"
IDX_DEFINITIONS_IS_PRIMARY = "idx_definitions_is_primary"
IDX_DOCUMENTS_UPLOAD_STATUS = "idx_documents_upload_status"
IDX_DOCUMENTS_UPLOADED_AT = "idx_documents_uploaded_at"
IDX_DOCUMENTS_METADATA = "idx_documents_metadata"  # GIN index on JSONB
IDX_REFERENCES_ENTRY_ID = "idx_references_entry_id"
IDX_REFERENCES_DOCUMENT_ID = "idx_references_document_id"


# =============================================================================
# API RESPONSE CONSTANTS
# =============================================================================

# HTTP status code messages
MSG_CREATED = "Resource created successfully"
MSG_UPDATED = "Resource updated successfully"
MSG_DELETED = "Resource deleted successfully"
MSG_NOT_FOUND = "Resource not found"
MSG_DUPLICATE = "Resource already exists"
MSG_INVALID_INPUT = "Invalid input provided"
MSG_SERVER_ERROR = "Internal server error"


# =============================================================================
# REGEX PATTERNS (for validation and extraction)
# =============================================================================

# OCR corruption patterns
PATTERN_DUPLICATE_CHARS = r'([a-z])\1{2,}'  # 3+ consecutive duplicates
PATTERN_ALTERNATING_DUPLICATES = r'([a-z])\1([a-z])\2([a-z])\3'  # aabbcc pattern
PATTERN_PDF_ENCODING = r'cid:\d+'  # PDF font encoding artifacts
PATTERN_SPACED_CHARS = r'\b([A-Z](?:\s+[a-z])+)\b'  # "T e m p" pattern

# Citation patterns
PATTERN_ET_AL = r'\bet\s*al\.?$'
PATTERN_IBID = r'\bibid\.?$'
PATTERN_YEAR_ONLY = r'^\d{4}$'
PATTERN_PAGE_REF = r'^pp?\.\s*\d+'

# Number patterns
PATTERN_SCIENTIFIC_NOTATION = r'^-?\d+\.?\d*e[+-]?\d+$'
PATTERN_PERCENTAGE = r'^\d+\.?\d*\s*%$'

# Validation patterns
PATTERN_TRAILING_HYPHEN = r'-$'
PATTERN_LEADING_HYPHEN = r'^-'


# =============================================================================
# SPACY MODEL CONSTANTS
# =============================================================================

SPACY_MODEL_ENGLISH = "en_core_web_sm"
SPACY_MODEL_GERMAN = "de_core_news_sm"

SPACY_MODELS = {
    LANG_ENGLISH: SPACY_MODEL_ENGLISH,
    LANG_GERMAN: SPACY_MODEL_GERMAN
}


# =============================================================================
# LOGGING CONSTANTS
# =============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"


# =============================================================================
# ENVIRONMENT CONSTANTS
# =============================================================================

ENV_DEVELOPMENT = "development"
ENV_PRODUCTION = "production"
ENV_TESTING = "testing"


# =============================================================================
# EXTRACTION CONSTANTS
# =============================================================================

# Minimum confidence thresholds for term extraction
MIN_EXTRACTION_CONFIDENCE = 0.5
HIGH_CONFIDENCE_THRESHOLD = 0.8

# NLP processing
MIN_SENTENCE_LENGTH = 10  # characters
MAX_SENTENCES_PER_TERM = 5

# Term extraction limits
MAX_TERMS_PER_DOCUMENT = 10000
MAX_DEFINITIONS_PER_TERM = 10


# =============================================================================
# ERROR MESSAGES (for consistency)
# =============================================================================

ERR_FILE_TOO_LARGE = "File too large (maximum {max_size}MB)"
ERR_INVALID_FILE_TYPE = "Invalid file type. Allowed: {allowed_types}"
ERR_UPLOAD_FAILED = "Failed to upload file: {error}"
ERR_PROCESSING_FAILED = "Failed to process document: {error}"
ERR_INVALID_LANGUAGE = f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)}"
ERR_INVALID_SOURCE = f"Source must be one of: {', '.join(ALLOWED_SOURCES)}"
ERR_TERM_TOO_SHORT = "Term too short (minimum {min_length} characters)"
ERR_TERM_TOO_LONG = "Term too long (maximum {max_length} characters)"
ERR_DUPLICATE_ENTRY = "Entry '{term}' already exists for language '{language}' from source '{source}'"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_spacy_model(language: str) -> str:
    """
    Get the appropriate spaCy model for a language

    Args:
        language: Language code ('en' or 'de')

    Returns:
        spaCy model name

    Raises:
        ValueError: If language is not supported
    """
    if language not in SPACY_MODELS:
        raise ValueError(f"Unsupported language: {language}. Must be one of {SUPPORTED_LANGUAGES}")
    return SPACY_MODELS[language]


def validate_language(language: str) -> bool:
    """
    Validate if a language code is supported

    Args:
        language: Language code to validate

    Returns:
        True if language is supported, False otherwise
    """
    return language in SUPPORTED_LANGUAGES


def validate_source(source: str) -> bool:
    """
    Validate if a source is allowed

    Args:
        source: Source to validate

    Returns:
        True if source is allowed, False otherwise
    """
    return source in ALLOWED_SOURCES


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Languages
    'LANG_ENGLISH', 'LANG_GERMAN', 'SUPPORTED_LANGUAGES', 'DEFAULT_LANGUAGE',
    'LANGUAGE_PATTERN',

    # Sources
    'SOURCE_INTERNAL', 'SOURCE_NAMUR', 'SOURCE_DIN', 'SOURCE_ASME',
    'SOURCE_IEC', 'SOURCE_IATE', 'SOURCE_PDF', 'SOURCE_MANUAL',
    'ALLOWED_SOURCES', 'DEFAULT_SOURCE',

    # Statuses
    'VALIDATION_STATUS_PENDING', 'VALIDATION_STATUS_VALIDATED', 'VALIDATION_STATUS_REJECTED',
    'VALIDATION_STATUSES', 'VALIDATION_STATUS_PATTERN',
    'SYNC_STATUS_PENDING', 'SYNC_STATUS_SYNCED', 'SYNC_STATUS_FAILED',
    'SYNC_STATUSES', 'SYNC_STATUS_PATTERN',
    'UPLOAD_STATUS_PENDING', 'UPLOAD_STATUS_PROCESSING',
    'UPLOAD_STATUS_COMPLETED', 'UPLOAD_STATUS_FAILED', 'UPLOAD_STATUSES',

    # Validation
    'MIN_TERM_LENGTH', 'MAX_TERM_LENGTH', 'MIN_DEFINITION_LENGTH',
    'MIN_WORD_COUNT', 'MAX_WORD_COUNT', 'MAX_SYMBOL_RATIO',
    'MIN_ACRONYM_LENGTH', 'MAX_ACRONYM_LENGTH',
    'REJECT_PURE_NUMBERS', 'REJECT_PERCENTAGES', 'ALLOW_ALL_UPPERCASE',

    # File Upload
    'UPLOAD_DIR', 'DATABASE_DIR', 'ALLOWED_EXTENSIONS',
    'MAX_UPLOAD_SIZE', 'MAX_FILE_SIZE_MB', 'MAX_BATCH_SIZE',
    'MIME_TYPE_PDF', 'ALLOWED_MIME_TYPES', 'PDF_MAGIC_BYTES',

    # Pagination
    'DEFAULT_PAGE_SIZE', 'MAX_PAGE_SIZE', 'MIN_PAGE_SIZE', 'DEFAULT_OFFSET',

    # Neo4j
    'NEO4J_TIMEOUT', 'NEO4J_MAX_RETRY', 'NEO4J_RETRY_DELAY',
    'REL_USES', 'REL_PART_OF', 'REL_RELATED_TO', 'REL_SYNONYM_OF',
    'REL_TRANSLATION_OF', 'REL_DERIVED_FROM',

    # Patterns
    'PATTERN_DUPLICATE_CHARS', 'PATTERN_ALTERNATING_DUPLICATES',
    'PATTERN_PDF_ENCODING', 'PATTERN_SPACED_CHARS',
    'PATTERN_ET_AL', 'PATTERN_IBID', 'PATTERN_YEAR_ONLY', 'PATTERN_PAGE_REF',

    # SpaCy
    'SPACY_MODEL_ENGLISH', 'SPACY_MODEL_GERMAN', 'SPACY_MODELS',

    # Helpers
    'get_spacy_model', 'validate_language', 'validate_source', 'format_file_size'
]
