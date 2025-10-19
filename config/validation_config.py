"""
Term Validation Configuration Presets
Provides ready-to-use validation configurations for different use cases
"""
from src.backend.services.term_validator import ValidationConfig


# ===== Predefined Validation Profiles =====

STRICT_ENGLISH = ValidationConfig(
    min_term_length=4,
    max_term_length=80,
    min_word_count=1,
    max_word_count=3,
    max_symbol_ratio=0.2,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=6,
    language="en"
)

STRICT_GERMAN = ValidationConfig(
    min_term_length=4,
    max_term_length=80,
    min_word_count=1,
    max_word_count=3,
    max_symbol_ratio=0.2,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=6,
    language="de"
)

DEFAULT_ENGLISH = ValidationConfig(
    min_term_length=3,
    max_term_length=100,
    min_word_count=1,
    max_word_count=4,
    max_symbol_ratio=0.3,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=8,
    language="en"
)

DEFAULT_GERMAN = ValidationConfig(
    min_term_length=3,
    max_term_length=100,
    min_word_count=1,
    max_word_count=4,
    max_symbol_ratio=0.3,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=8,
    language="de"
)

LENIENT_ENGLISH = ValidationConfig(
    min_term_length=2,
    max_term_length=150,
    min_word_count=1,
    max_word_count=6,
    max_symbol_ratio=0.4,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=1,
    max_acronym_length=10,
    language="en"
)

LENIENT_GERMAN = ValidationConfig(
    min_term_length=2,
    max_term_length=150,
    min_word_count=1,
    max_word_count=6,
    max_symbol_ratio=0.4,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=1,
    max_acronym_length=10,
    language="de"
)

# ===== Domain-Specific Configurations =====

TECHNICAL_DOCUMENTATION = ValidationConfig(
    min_term_length=3,
    max_term_length=100,
    min_word_count=1,
    max_word_count=5,  # Technical terms can be longer
    max_symbol_ratio=0.3,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=10,  # Technical acronyms can be longer
    language="en"
)

STANDARDS_AND_NORMS = ValidationConfig(
    min_term_length=3,
    max_term_length=120,
    min_word_count=1,
    max_word_count=6,  # Standard names can be long
    max_symbol_ratio=0.35,  # Standards may have more symbols (e.g., "ISO/IEC")
    reject_pure_numbers=False,  # Standards often have numbers (e.g., "ISO 9001")
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=12,
    language="en"
)

ACADEMIC_SCIENTIFIC = ValidationConfig(
    min_term_length=4,
    max_term_length=150,
    min_word_count=1,
    max_word_count=8,  # Scientific terms can be very long
    max_symbol_ratio=0.25,
    reject_pure_numbers=True,
    reject_percentages=True,
    allow_all_uppercase=True,
    min_acronym_length=2,
    max_acronym_length=8,
    language="en"
)


# ===== Helper Function =====

def get_validation_config(profile: str = "default", language: str = "en") -> ValidationConfig:
    """
    Get a validation configuration by profile name

    Args:
        profile: Profile name ("strict", "default", "lenient", "technical", "standards", "academic")
        language: Language code ("en" or "de")

    Returns:
        ValidationConfig instance

    Raises:
        ValueError: If profile or language is invalid
    """
    profiles = {
        "strict": {
            "en": STRICT_ENGLISH,
            "de": STRICT_GERMAN
        },
        "default": {
            "en": DEFAULT_ENGLISH,
            "de": DEFAULT_GERMAN
        },
        "lenient": {
            "en": LENIENT_ENGLISH,
            "de": LENIENT_GERMAN
        },
        "technical": {
            "en": TECHNICAL_DOCUMENTATION,
            "de": TECHNICAL_DOCUMENTATION  # Use same config for German technical docs
        },
        "standards": {
            "en": STANDARDS_AND_NORMS,
            "de": STANDARDS_AND_NORMS
        },
        "academic": {
            "en": ACADEMIC_SCIENTIFIC,
            "de": ACADEMIC_SCIENTIFIC
        }
    }

    if profile not in profiles:
        raise ValueError(f"Invalid profile: {profile}. Must be one of: {', '.join(profiles.keys())}")

    if language not in ["en", "de"]:
        raise ValueError(f"Invalid language: {language}. Must be 'en' or 'de'")

    # Clone the config and update language if needed
    config = profiles[profile][language]

    return config


# ===== Documentation =====

PROFILE_DESCRIPTIONS = {
    "strict": "Strict validation for high-quality glossaries. Rejects more terms to ensure quality.",
    "default": "Balanced validation suitable for most use cases.",
    "lenient": "Lenient validation that accepts more terms. Good for initial extraction.",
    "technical": "Optimized for technical documentation with longer compound terms and acronyms.",
    "standards": "Optimized for industry standards (DIN, ISO, ASME, etc.) that may contain numbers.",
    "academic": "Optimized for academic and scientific terminology with complex multi-word terms."
}


def list_profiles() -> dict:
    """
    List all available validation profiles with descriptions

    Returns:
        Dictionary mapping profile names to descriptions
    """
    return PROFILE_DESCRIPTIONS.copy()
