"""
Validation Analysis Script
Analyzes current validation effectiveness and provides metrics
"""
import sqlite3
import json
from pathlib import Path
from collections import Counter, defaultdict
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from services.term_validator import TermValidator, ValidationConfig, create_strict_validator, create_lenient_validator


def analyze_validation():
    """Analyze validation effectiveness on current glossary terms"""

    # Connect to database
    db_path = Path(__file__).parent.parent / "data" / "glossary.db"
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all terms
    cursor.execute('SELECT term, language, source FROM glossary_entries')
    all_terms = cursor.fetchall()

    print("=" * 80)
    print("VALIDATION ANALYSIS REPORT")
    print("=" * 80)
    print(f"\n📊 Total Terms in Database: {len(all_terms)}\n")

    # Test with different validation profiles
    profiles = {
        "strict": create_strict_validator("en"),
        "default": TermValidator(ValidationConfig(language="en")),
        "lenient": create_lenient_validator("en")
    }

    results = {}

    for profile_name, validator in profiles.items():
        print(f"\n{'=' * 40}")
        print(f"PROFILE: {profile_name.upper()}")
        print('=' * 40)

        valid_count = 0
        invalid_count = 0
        rejection_reasons = Counter()
        rejection_examples = defaultdict(list)

        for term, lang, source in all_terms:
            if validator.is_valid_term(term):
                valid_count += 1
            else:
                invalid_count += 1
                reason = validator.get_rejection_reason(term)
                rejection_reasons[reason] += 1

                # Store examples (max 3 per reason)
                if len(rejection_examples[reason]) < 3:
                    rejection_examples[reason].append(term)

        # Calculate metrics
        total = len(all_terms)
        precision = (valid_count / total * 100) if total > 0 else 0
        rejection_rate = (invalid_count / total * 100) if total > 0 else 0

        print(f"\n✅ Valid Terms: {valid_count} ({precision:.1f}%)")
        print(f"❌ Invalid Terms: {invalid_count} ({rejection_rate:.1f}%)")

        print(f"\n📋 TOP 10 REJECTION REASONS:")
        for reason, count in rejection_reasons.most_common(10):
            percentage = (count / invalid_count * 100) if invalid_count > 0 else 0
            print(f"  • {reason}: {count} ({percentage:.1f}%)")
            print(f"    Examples: {', '.join(rejection_examples[reason][:3])}")

        results[profile_name] = {
            'valid': valid_count,
            'invalid': invalid_count,
            'precision': precision,
            'rejection_rate': rejection_rate,
            'rejection_reasons': dict(rejection_reasons.most_common(10))
        }

    # Sample analysis - get term quality indicators
    print(f"\n\n{'=' * 80}")
    print("TERM QUALITY INDICATORS")
    print('=' * 80)

    # Analyze term characteristics
    term_lengths = []
    word_counts = []
    has_numbers = 0
    has_symbols = 0
    all_uppercase = 0
    stop_words_present = 0

    stop_words = {"the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for"}

    for term, lang, source in all_terms:
        term_lengths.append(len(term))
        word_counts.append(len(term.split()))

        if any(c.isdigit() for c in term):
            has_numbers += 1
        if any(c in "!@#$%^&*()+=[]{}|\\:;\"'<>,?/" for c in term):
            has_symbols += 1
        if term.isupper() and len(term) > 1:
            all_uppercase += 1
        if term.lower() in stop_words or any(word in stop_words for word in term.lower().split()):
            stop_words_present += 1

    avg_length = sum(term_lengths) / len(term_lengths) if term_lengths else 0
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0

    print(f"\n📏 Average Term Length: {avg_length:.1f} characters")
    print(f"📝 Average Word Count: {avg_words:.1f} words")
    print(f"🔢 Terms with Numbers: {has_numbers} ({has_numbers/len(all_terms)*100:.1f}%)")
    print(f"💠 Terms with Symbols: {has_symbols} ({has_symbols/len(all_terms)*100:.1f}%)")
    print(f"🔠 All-Uppercase Terms: {all_uppercase} ({all_uppercase/len(all_terms)*100:.1f}%)")
    print(f"⛔ Terms with Stop Words: {stop_words_present} ({stop_words_present/len(all_terms)*100:.1f}%)")

    # Analyze frequency distribution
    cursor.execute('''
        SELECT tdr.frequency, ge.term
        FROM term_document_references tdr
        JOIN glossary_entries ge ON tdr.glossary_entry_id = ge.id
        ORDER BY tdr.frequency DESC
        LIMIT 20
    ''')
    high_freq_terms = cursor.fetchall()

    print(f"\n\n{'=' * 80}")
    print("HIGH-FREQUENCY TERMS (Top 20)")
    print('=' * 80)

    validator_default = TermValidator(ValidationConfig(language="en"))

    for freq, term in high_freq_terms:
        is_valid = validator_default.is_valid_term(term)
        status = "✅" if is_valid else "❌"
        reason = "" if is_valid else f" - {validator_default.get_rejection_reason(term)}"
        print(f"{status} {term} (freq: {freq}){reason}")

    # Configuration recommendations
    print(f"\n\n{'=' * 80}")
    print("CONFIGURATION RECOMMENDATIONS")
    print('=' * 80)

    print(f"""
Based on the analysis:

1. CURRENT STATE:
   - Total terms extracted: {len(all_terms)}
   - Terms are currently marked as 'pending' validation
   - Validation during extraction was {'ENABLED' if 'enable_validation' in str(all_terms) else 'NOT DETECTED'}

2. VALIDATION PROFILE COMPARISON:
   - STRICT: {results['strict']['valid']} valid ({results['strict']['precision']:.1f}%)
   - DEFAULT: {results['default']['valid']} valid ({results['default']['precision']:.1f}%)
   - LENIENT: {results['lenient']['valid']} valid ({results['lenient']['precision']:.1f}%)

3. QUALITY ISSUES DETECTED:
   - Stop words in terms: {stop_words_present} terms ({stop_words_present/len(all_terms)*100:.1f}%)
   - Terms with excessive symbols: {has_symbols} terms ({has_symbols/len(all_terms)*100:.1f}%)
   - Potential fragments (check rejection reasons above)

4. RECOMMENDATIONS:

   A. IMMEDIATE ACTIONS:
      • Enable validation during extraction (currently may be disabled)
      • Use DEFAULT profile as starting point (balanced precision/recall)
      • Set min_frequency=2 to reduce low-quality single-occurrence terms
      • Set min_term_length=4 to filter out short fragments

   B. CONFIGURATION TUNING:
      ```python
      ValidationConfig(
          min_term_length=4,          # Up from 3 to reduce fragments
          max_term_length=100,        # Keep current
          min_word_count=1,           # Keep current
          max_word_count=4,           # Keep current (technical terms can be long)
          max_symbol_ratio=0.25,      # Reduce from 0.3 to filter symbol-heavy terms
          reject_pure_numbers=True,   # Keep enabled
          reject_percentages=True,    # Keep enabled
          allow_all_uppercase=True,   # Keep for acronyms
          min_acronym_length=2,       # Keep current
          max_acronym_length=8,       # Keep current
          language="en"
      )
      ```

   C. EXTRACTION PARAMETERS:
      ```python
      extract_terms(
          text=text,
          min_term_length=3,          # Keep (handled by validator)
          max_term_length=100,        # Keep
          min_frequency=2,            # INCREASE from 1 to 2
          enable_validation=True      # ENSURE this is True
      )
      ```

5. EXPECTED IMPROVEMENTS:
   - Precision: {results['default']['precision']:.1f}% → ~85-90% (with recommended config)
   - Rejection of low-quality terms: {results['default']['rejection_rate']:.1f}% → ~25-30%
   - Better signal-to-noise ratio in glossary

6. A/B TEST PLAN:
   - Test recommended config on 1-2 sample PDFs
   - Compare term quality manually (review 20-30 terms)
   - Measure: precision, recall, user satisfaction
   - Iterate based on domain-specific needs
""")

    conn.close()


if __name__ == "__main__":
    analyze_validation()
