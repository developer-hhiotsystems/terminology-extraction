# Term Validation System

## Overview

The Term Validation System provides comprehensive filtering logic to ensure only high-quality glossary entries are accepted. It addresses known issues with low-quality term extraction by implementing multi-layered validation rules.

## Problem Statement

The original term extraction system was accepting low-quality entries such as:

- **Symbols**: `[%]`, `...`, `---`
- **Numbers**: `4000`, `123`, `70%`
- **Stop Words**: `The`, `and`, `of`
- **Fragments**: `Mem-`, `three-`, `-able`

These entries polluted the glossary and made it less useful for end users.

## Solution

The `TermValidator` class implements comprehensive validation with configurable rules:

### Validation Rules

1. **Length Validation**
   - Minimum character length (default: 3)
   - Maximum character length (default: 100)
   - Prevents single characters and overly long terms

2. **Number Filtering**
   - Rejects pure numbers (`123`, `4000`)
   - Rejects scientific notation (`1.5e10`)
   - Configurable via `reject_pure_numbers` flag

3. **Percentage Filtering**
   - Rejects percentage patterns (`70%`, `50 percent`)
   - Configurable via `reject_percentages` flag

4. **Symbol/Punctuation Validation**
   - Rejects pure symbol terms (`[%]`, `...`, `!!!`)
   - Enforces symbol-to-character ratio limit (default: 30%)
   - Allows valid punctuation like hyphens and apostrophes

5. **Stop Word Filtering**
   - Filters common English/German words (`the`, `and`, `of`, `der`, `die`)
   - Language-specific stop word lists
   - Case-insensitive matching

6. **Word Count Validation**
   - Minimum words per term (default: 1)
   - Maximum words per term (default: 4)
   - Prevents overly complex compound terms

7. **Fragment Detection**
   - Rejects terms ending with hyphens (`Mem-`)
   - Rejects terms starting with hyphens (`-able`)
   - Prevents incomplete word extraction

8. **Capitalization Validation**
   - Accepts: Title Case, UPPERCASE, lowercase, camelCase, PascalCase
   - Rejects: Random capitalization patterns (`DaTaBaSe`)
   - Allows technical terms like `JavaScript`, `PostgreSQL`
   - Acronym length validation (default: 2-8 characters)

## Architecture

### Core Components

```
src/backend/services/
├── term_validator.py          # Main validation logic
└── term_extractor.py           # Integration with extraction

config/
└── validation_config.py        # Predefined validation profiles

tests/unit/
└── test_term_validator.py      # Comprehensive test suite (29 tests)
```

### Class Structure

```python
# Main validator class
class TermValidator:
    def __init__(self, config: ValidationConfig)
    def is_valid_term(self, term: str) -> bool
    def get_rejection_reason(self, term: str) -> str
    def validate_with_details(self, term: str) -> Dict
    def batch_validate(self, terms: List[str]) -> Dict

# Configuration dataclass
@dataclass
class ValidationConfig:
    min_term_length: int = 3
    max_term_length: int = 100
    max_symbol_ratio: float = 0.3
    reject_pure_numbers: bool = True
    reject_percentages: bool = True
    # ... more configuration options

# Factory functions
def create_default_validator(language: str) -> TermValidator
def create_strict_validator(language: str) -> TermValidator
def create_lenient_validator(language: str) -> TermValidator
```

## Usage

### Basic Usage

```python
from src.backend.services.term_validator import create_default_validator

# Create validator
validator = create_default_validator("en")

# Validate single term
if validator.is_valid_term("Database"):
    print("Valid term!")

# Get rejection reason
reason = validator.get_rejection_reason("123")
print(reason)  # "Term is a pure number"
```

### Batch Validation

```python
terms = ["API", "Database", "123", "The", "[%]"]
result = validator.batch_validate(terms)

print(f"Valid: {result['valid']}")      # ['API', 'Database']
print(f"Invalid: {result['invalid']}")  # ['123', 'The', '[%]']
print(f"Reasons: {result['rejection_reasons']}")
```

### Detailed Validation

```python
result = validator.validate_with_details("Database")
print(result)
# {
#     'valid': True,
#     'term': 'Database',
#     'rejection_reason': '',
#     'details': {
#         'length': True,
#         'not_number': True,
#         'not_stop_word': True,
#         # ... all validation checks
#     }
# }
```

### Integration with Term Extractor

```python
from src.backend.services.term_extractor import TermExtractor
from src.backend.services.term_validator import create_strict_validator

# Create extractor with custom validator
validator = create_strict_validator("en")
extractor = TermExtractor(language="en", validator=validator)

# Extract and validate terms
terms = extractor.extract_terms(
    text="Your document text here...",
    enable_validation=True  # Enable filtering
)
```

## Validation Profiles

The system includes predefined validation profiles for different use cases:

### Default Profile
Balanced validation suitable for most use cases.
- Min length: 3 characters
- Max words: 4
- Symbol ratio: 30%

### Strict Profile
High-quality filtering for curated glossaries.
- Min length: 4 characters
- Max words: 3
- Symbol ratio: 20%
- Stricter acronym rules

### Lenient Profile
Accepts more terms, good for initial extraction.
- Min length: 2 characters
- Max words: 6
- Symbol ratio: 40%

### Domain-Specific Profiles

**Technical Documentation**
- Optimized for technical terms
- Allows longer compound terms (up to 5 words)
- Supports longer acronyms (up to 10 chars)

**Standards and Norms**
- Optimized for industry standards (DIN, ISO, IEC, ASME)
- Allows numbers in terms (e.g., "ISO 9001")
- Higher symbol tolerance for standard notations

**Academic/Scientific**
- Allows very long multi-word terms (up to 8 words)
- Suitable for complex scientific terminology

### Using Profiles

```python
from config.validation_config import get_validation_config
from src.backend.services.term_validator import TermValidator

# Get predefined profile
config = get_validation_config("strict", "en")
validator = TermValidator(config)

# Or use factory functions
from src.backend.services.term_validator import (
    create_strict_validator,
    create_lenient_validator
)
strict = create_strict_validator("en")
lenient = create_lenient_validator("de")
```

## Configuration

### Custom Configuration

```python
from src.backend.services.term_validator import ValidationConfig, TermValidator

config = ValidationConfig(
    min_term_length=5,
    max_term_length=50,
    max_symbol_ratio=0.25,
    reject_pure_numbers=True,
    reject_percentages=True,
    min_word_count=1,
    max_word_count=3,
    language="en"
)

validator = TermValidator(config)
```

### Language Support

The system supports language-specific validation:

- **English (en)**: English stop words, capitalization rules
- **German (de)**: German stop words, language-specific patterns

Stop words are automatically loaded based on the language setting.

## Testing

Comprehensive test suite with 29 unit tests covering:

- Known bad entries (symbols, numbers, percentages, stop words, fragments)
- Valid technical terms
- Length validation
- Word count validation
- Symbol ratio validation
- Capitalization patterns
- Batch validation
- Detailed validation results
- Configuration variants
- Language-specific stop words
- Edge cases

### Running Tests

```bash
# Run all term validator tests
pytest tests/unit/test_term_validator.py -v

# Run specific test
pytest tests/unit/test_term_validator.py::TestTermValidator::test_reject_pure_symbols -v
```

### Test Coverage

All 29 tests pass successfully, covering:
- ✓ Symbol rejection
- ✓ Number rejection
- ✓ Percentage rejection
- ✓ Stop word filtering
- ✓ Fragment detection
- ✓ Valid term acceptance
- ✓ Batch processing
- ✓ Profile comparison

## Performance

The validator is designed for high performance:

- **O(n)** complexity for most validations
- Efficient string operations
- Minimal memory overhead
- Suitable for processing thousands of terms

Example performance:
- Single term validation: < 1ms
- Batch validation (1000 terms): < 50ms

## Demonstration

Run the demonstration script to see the validator in action:

```bash
python scripts/demo_term_validation.py
```

This demonstrates:
1. Known issue filtering
2. Valid term acceptance
3. Batch validation
4. Detailed analysis
5. Profile comparison
6. Real-world PDF extraction scenario

## Integration Points

### Backend API

The validator integrates with:

1. **Term Extraction (`term_extractor.py`)**
   - Automatic filtering during extraction
   - Configurable validation profiles
   - Logging of rejected terms

2. **Document Processing (`routers/documents.py`)**
   - PDF term extraction with validation
   - Quality metrics reporting

3. **Admin Panel**
   - Validation profile selection
   - Term quality monitoring

### Configuration Files

```python
# config/validation_config.py
STRICT_ENGLISH = ValidationConfig(...)
DEFAULT_ENGLISH = ValidationConfig(...)
LENIENT_ENGLISH = ValidationConfig(...)
# ... more profiles
```

## Error Handling

The validator handles edge cases gracefully:

- Empty strings → Invalid
- None values → Invalid
- Whitespace-only → Invalid
- Non-string input → Invalid
- Unicode characters → Handled correctly

## Logging

The validator logs important events:

```python
logger.info(f"Validation filtered out {count} low-quality terms")
logger.debug(f"Rejection reasons: {reasons}")
```

## Future Enhancements

Potential improvements:

1. Machine learning-based validation
2. Context-aware stop word filtering
3. Domain-specific term recognition
4. Multilingual support expansion
5. Performance optimizations for very large corpora
6. Custom regex pattern support

## References

- Main implementation: `src/backend/services/term_validator.py`
- Configuration: `config/validation_config.py`
- Tests: `tests/unit/test_term_validator.py`
- Demo: `scripts/demo_term_validation.py`
- Integration: `src/backend/services/term_extractor.py`

## Support

For issues or questions:
1. Check test suite for examples
2. Run demonstration script
3. Review validation configuration options
4. Consult API documentation

---

**Version**: 1.0.0
**Author**: Claude Code Implementation Agent
**Last Updated**: 2025-10-18
