"""
Demonstration Script: Term Validation System
Shows how the TermValidator filters low-quality glossary entries
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.services.term_validator import (
    create_default_validator,
    create_strict_validator,
    create_lenient_validator
)


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_known_issues():
    """Demonstrate filtering of known bad entries"""
    print_section("Known Issues - Terms That Should Be Rejected")

    validator = create_default_validator("en")

    bad_terms = {
        "Symbols": ["[%]", "...", "---", "!!!"],
        "Numbers": ["4000", "123", "70%"],
        "Stop Words": ["The", "and", "for"],
        "Fragments": ["Mem-", "three-", "-able"],
    }

    for category, terms in bad_terms.items():
        print(f"\n{category}:")
        for term in terms:
            is_valid = validator.is_valid_term(term)
            reason = validator.get_rejection_reason(term)
            status = "[X] REJECTED" if not is_valid else "[OK] ACCEPTED"
            print(f"  {status}: '{term}'")
            if reason:
                print(f"    Reason: {reason}")


def demo_valid_terms():
    """Demonstrate acceptance of valid technical terms"""
    print_section("Valid Technical Terms - Should Be Accepted")

    validator = create_default_validator("en")

    valid_terms = [
        "API",
        "Database",
        "Machine Learning",
        "Natural Language Processing",
        "RESTful API",
        "JavaScript",
        "PostgreSQL",
        "Client-Server",
    ]

    for term in valid_terms:
        is_valid = validator.is_valid_term(term)
        status = "[OK] ACCEPTED" if is_valid else "[X] REJECTED"
        print(f"  {status}: '{term}'")
        if not is_valid:
            print(f"    Reason: {validator.get_rejection_reason(term)}")


def demo_batch_validation():
    """Demonstrate batch validation"""
    print_section("Batch Validation Example")

    validator = create_default_validator("en")

    mixed_terms = [
        "API",           # Valid
        "Database",      # Valid
        "123",           # Invalid - number
        "The",           # Invalid - stop word
        "[%]",           # Invalid - symbols
        "Machine Learning",  # Valid
        "70%",           # Invalid - percentage
        "PostgreSQL",    # Valid
        "...",           # Invalid - symbols
    ]

    print("\nProcessing batch of terms...")
    result = validator.batch_validate(mixed_terms)

    print(f"\nResults:")
    print(f"  Total terms: {result['total']}")
    print(f"  Valid: {result['valid_count']}")
    print(f"  Invalid: {result['invalid_count']}")

    print(f"\n  Valid Terms:")
    for term in result['valid']:
        print(f"    [+] {term}")

    print(f"\n  Invalid Terms:")
    for term in result['invalid']:
        reason = result['rejection_reasons'][term]
        print(f"    [-] {term} - {reason}")


def demo_detailed_validation():
    """Demonstrate detailed validation results"""
    print_section("Detailed Validation Analysis")

    validator = create_default_validator("en")

    terms_to_analyze = ["Database", "123", "[%]", "The"]

    for term in terms_to_analyze:
        print(f"\nAnalyzing: '{term}'")
        result = validator.validate_with_details(term)

        print(f"  Valid: {result['valid']}")
        if not result['valid']:
            print(f"  Rejection Reason: {result['rejection_reason']}")

        print(f"  Validation Checks:")
        for check, passed in result['details'].items():
            status = "[+]" if passed else "[-]"
            print(f"    {status} {check}")


def demo_validation_profiles():
    """Demonstrate different validation profiles"""
    print_section("Validation Profiles Comparison")

    strict = create_strict_validator("en")
    default = create_default_validator("en")
    lenient = create_lenient_validator("en")

    test_terms = ["API", "AB", "REST", "A"]

    print("\nComparing validation profiles:\n")
    print(f"{'Term':<10} {'Strict':<10} {'Default':<10} {'Lenient':<10}")
    print("-" * 45)

    for term in test_terms:
        strict_result = "[+]" if strict.is_valid_term(term) else "[-]"
        default_result = "[+]" if default.is_valid_term(term) else "[-]"
        lenient_result = "[+]" if lenient.is_valid_term(term) else "[-]"

        print(f"{term:<10} {strict_result:<10} {default_result:<10} {lenient_result:<10}")


def demo_real_world_scenario():
    """Demonstrate real-world PDF extraction scenario"""
    print_section("Real-World Scenario: PDF Term Extraction")

    validator = create_default_validator("en")

    # Simulated extracted terms from a technical PDF
    extracted_terms = [
        "Control System",      # Valid
        "Process Automation",  # Valid
        "The",                 # Invalid - stop word
        "4000",                # Invalid - number
        "NAMUR",               # Valid - acronym
        "[%]",                 # Invalid - symbols
        "Safety Integrity Level",  # Valid
        "and",                 # Invalid - stop word
        "PLC",                 # Valid - acronym
        "...",                 # Invalid - symbols
        "IEC 61511",           # Valid - standard reference
        "Mem-",                # Invalid - fragment
        "Fieldbus",            # Valid
    ]

    print("\nSimulating term extraction from technical PDF...")
    print(f"Total extracted: {len(extracted_terms)} terms\n")

    result = validator.batch_validate(extracted_terms)

    print("Filtering results:")
    print(f"  [+] Accepted: {result['valid_count']} high-quality terms")
    print(f"  [-] Rejected: {result['invalid_count']} low-quality terms")

    print("\n  Accepted Terms:")
    for term in result['valid']:
        print(f"    * {term}")

    print("\n  Rejected Terms (with reasons):")
    for term in result['invalid']:
        reason = result['rejection_reasons'][term]
        print(f"    * {term} - {reason}")

    quality_ratio = (result['valid_count'] / result['total']) * 100
    print(f"\n  Quality Improvement: {quality_ratio:.1f}% of terms are high-quality")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  TERM VALIDATION SYSTEM DEMONSTRATION")
    print("  Comprehensive Term Quality Filtering for Glossary Extraction")
    print("=" * 70)

    demo_known_issues()
    demo_valid_terms()
    demo_batch_validation()
    demo_detailed_validation()
    demo_validation_profiles()
    demo_real_world_scenario()

    print("\n" + "=" * 70)
    print("  Demonstration Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
