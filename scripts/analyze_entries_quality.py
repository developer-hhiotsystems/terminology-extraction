"""
Data Quality Analysis - Second Round
Analyzes glossary entries after TermValidator integration
"""
import sys
import os
from collections import defaultdict, Counter
import re

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root and backend to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src', 'backend'))

from src.backend.database import SessionLocal
from src.backend.models import GlossaryEntry
from src.backend.services.term_validator import create_default_validator

def categorize_term_quality(term: str, definition: str, validator) -> tuple[str, str]:
    """
    Categorize a term into quality levels with reasoning
    Returns: (category, reason)
    """
    # Test if it would pass validation
    is_valid = validator.is_valid_term(term)
    reason = validator.get_rejection_reason(term) if not is_valid else "valid"

    # Additional quality checks
    term_lower = term.lower().strip()

    # Excellent: Clear technical terms, proper nouns, specific concepts
    excellent_patterns = [
        (len(term.split()) >= 2 and len(term.split()) <= 5, "multi-word technical term"),
        (term[0].isupper() and ' ' in term, "proper noun or title"),
        (any(char.isupper() for char in term[1:]) and not term.isupper(), "mixed case technical term"),
        (term.endswith('tion') or term.endswith('ment') or term.endswith('ness'), "abstract concept suffix"),
    ]

    # Good: Valid single words, acronyms, basic terms
    good_patterns = [
        (term.isupper() and len(term) >= 2 and len(term) <= 6, "acronym"),
        (term.isalpha() and len(term) >= 4, "valid word"),
        (term.replace('-', '').replace('_', '').isalpha(), "hyphenated term"),
    ]

    # Questionable: Edge cases
    questionable_patterns = [
        (len(term) <= 2 and term.isalpha(), "very short term"),
        (term.startswith('the ') or term.startswith('a '), "starts with article"),
        (any(char.isdigit() for char in term) and not term.isdigit(), "contains numbers"),
        (term.count('.') > 0, "contains periods"),
    ]

    # Bad: Should be filtered
    bad_patterns = [
        (term.isdigit(), "pure number"),
        (len(term) <= 1, "single character"),
        (term in ['', ' ', '\t', '\n'], "whitespace/empty"),
        (bool(re.match(r'^[^a-zA-Z]+$', term)), "no letters"),
        (term.lower() in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'], "stopword"),
    ]

    # Check patterns in order
    for pattern, desc in bad_patterns:
        if pattern:
            return "bad", f"BAD: {desc} (validator: {reason})"

    for pattern, desc in questionable_patterns:
        if pattern:
            return "questionable", f"QUESTIONABLE: {desc} (validator: {reason})"

    if not is_valid:
        return "questionable", f"QUESTIONABLE: failed validation - {reason}"

    for pattern, desc in excellent_patterns:
        if pattern:
            return "excellent", f"EXCELLENT: {desc}"

    for pattern, desc in good_patterns:
        if pattern:
            return "good", f"GOOD: {desc}"

    return "good", "GOOD: standard valid term"

def analyze_quality():
    """Main analysis function"""
    db = SessionLocal()
    validator = create_default_validator('en')

    print("=" * 80)
    print("DATA QUALITY ANALYSIS - SECOND ROUND")
    print("After TermValidator Integration")
    print("=" * 80)
    print()

    # Fetch all entries
    entries = db.query(GlossaryEntry).all()
    total_count = len(entries)

    print(f"📊 TOTAL ENTRIES: {total_count}")
    print()

    if total_count == 0:
        print("⚠️  No entries found in database!")
        return

    # Categorize all entries
    quality_distribution = defaultdict(list)

    for entry in entries:
        # Note: GlossaryEntry uses 'definitions' (plural) field
        definition = entry.definitions[:100] if entry.definitions else ""
        category, reason = categorize_term_quality(entry.term, entry.definitions or "", validator)
        quality_distribution[category].append({
            'term': entry.term,
            'definition': definition,
            'source': entry.source_document,
            'reason': reason
        })

    # Calculate percentages
    print("📈 QUALITY DISTRIBUTION:")
    print("-" * 80)

    categories = ['excellent', 'good', 'questionable', 'bad']
    for category in categories:
        count = len(quality_distribution[category])
        percentage = (count / total_count * 100) if total_count > 0 else 0
        icon = {'excellent': '✅', 'good': '👍', 'questionable': '⚠️', 'bad': '❌'}[category]
        print(f"{icon} {category.upper():15s}: {count:4d} ({percentage:5.1f}%)")

    print()

    # Calculate overall quality score
    high_quality_count = len(quality_distribution['excellent']) + len(quality_distribution['good'])
    quality_percentage = (high_quality_count / total_count * 100) if total_count > 0 else 0

    print(f"🎯 HIGH-QUALITY TERMS: {high_quality_count}/{total_count} ({quality_percentage:.1f}%)")
    print()

    # Show sample entries from each category
    print("=" * 80)
    print("📋 SAMPLE ENTRIES BY CATEGORY")
    print("=" * 80)
    print()

    samples_per_category = 10

    for category in categories:
        entries_in_cat = quality_distribution[category]
        if not entries_in_cat:
            continue

        print(f"\n{category.upper()} ({len(entries_in_cat)} total)")
        print("-" * 80)

        for i, entry in enumerate(entries_in_cat[:samples_per_category], 1):
            print(f"{i}. '{entry['term']}'")
            print(f"   Definition: {entry['definition']}...")
            print(f"   Source: {entry['source']}")
            print(f"   Analysis: {entry['reason']}")
            print()

        if len(entries_in_cat) > samples_per_category:
            print(f"   ... and {len(entries_in_cat) - samples_per_category} more")
            print()

    # Validator effectiveness assessment
    print("=" * 80)
    print("🔍 TERMVALIDATOR EFFECTIVENESS ASSESSMENT")
    print("=" * 80)
    print()

    # Test validator against all entries
    validation_results = {'passed': 0, 'failed': 0, 'false_positives': 0, 'false_negatives': 0}

    for category, entries_list in quality_distribution.items():
        for entry_data in entries_list:
            is_valid = validator.is_valid_term(entry_data['term'])
            reason = validator.get_rejection_reason(entry_data['term'])

            if is_valid:
                validation_results['passed'] += 1
                # False negative: validator passed a bad term
                if category == 'bad':
                    validation_results['false_negatives'] += 1
            else:
                validation_results['failed'] += 1
                # False positive: validator rejected a good term
                if category in ['excellent', 'good']:
                    validation_results['false_positives'] += 1

    print(f"✅ Validation Passed: {validation_results['passed']}")
    print(f"❌ Validation Failed: {validation_results['failed']}")
    print(f"⚠️  False Positives (good terms rejected): {validation_results['false_positives']}")
    print(f"⚠️  False Negatives (bad terms accepted): {validation_results['false_negatives']}")
    print()

    # Calculate precision and recall
    true_positives = len(quality_distribution['excellent']) + len(quality_distribution['good']) - validation_results['false_positives']
    false_positives = validation_results['false_positives']
    false_negatives = validation_results['false_negatives']
    true_negatives = len(quality_distribution['bad']) - false_negatives

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"📊 VALIDATOR METRICS:")
    print(f"   Precision: {precision:.2%} (of accepted terms, how many are good?)")
    print(f"   Recall: {recall:.2%} (of good terms, how many are accepted?)")
    print(f"   F1 Score: {f1_score:.2%}")
    print()

    # Specific issues analysis
    print("=" * 80)
    print("🔧 SPECIFIC ISSUES FOUND")
    print("=" * 80)
    print()

    issues_found = []

    # Check for patterns in bad entries that passed
    if quality_distribution['bad']:
        issues_found.append(f"❌ {len(quality_distribution['bad'])} BAD entries in database")
        print(f"❌ {len(quality_distribution['bad'])} BAD entries that should have been filtered:")
        for entry in quality_distribution['bad'][:5]:
            print(f"   - '{entry['term']}' ({entry['reason']})")
        print()

    # Check for questionable entries
    if len(quality_distribution['questionable']) > total_count * 0.1:
        issues_found.append(f"⚠️  High percentage of questionable entries ({len(quality_distribution['questionable'])}/{total_count})")
        print(f"⚠️  High percentage of questionable entries:")
        for entry in quality_distribution['questionable'][:5]:
            print(f"   - '{entry['term']}' ({entry['reason']})")
        print()

    # Check for false positives
    if validation_results['false_positives'] > 0:
        issues_found.append(f"⚠️  {validation_results['false_positives']} good terms incorrectly rejected")
        print(f"⚠️  Good terms being incorrectly rejected:")
        # Find examples
        for category in ['excellent', 'good']:
            for entry in quality_distribution[category]:
                is_valid = validator.is_valid_term(entry['term'])
                if not is_valid:
                    reason = validator.get_rejection_reason(entry['term'])
                    print(f"   - '{entry['term']}' rejected because: {reason}")
        print()

    if not issues_found:
        print("✅ No significant issues found! Validator is working well.")
        print()

    # Recommendations
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    print()

    if quality_percentage >= 95:
        print("✅ EXCELLENT: Quality is very high (≥95%). Minor tuning only.")
    elif quality_percentage >= 85:
        print("👍 GOOD: Quality is good (85-95%). Some improvements possible.")
    elif quality_percentage >= 70:
        print("⚠️  FAIR: Quality is acceptable (70-85%). Needs improvement.")
    else:
        print("❌ POOR: Quality is low (<70%). Significant improvements needed.")

    print()

    # Specific recommendations
    recommendations = []

    if len(quality_distribution['bad']) > 0:
        recommendations.append("1. Strengthen validation rules to catch bad entries (numbers, single chars, stopwords)")

    if validation_results['false_positives'] > total_count * 0.05:
        recommendations.append("2. Relax validation rules to reduce false positives")

    if len(quality_distribution['questionable']) > total_count * 0.15:
        recommendations.append("3. Review questionable entries and adjust categorization rules")

    if quality_percentage < 90:
        recommendations.append("4. Consider implementing post-processing filters for edge cases")

    if not recommendations:
        recommendations.append("1. Continue monitoring quality with new documents")
        recommendations.append("2. Consider adding domain-specific validation rules if needed")

    for rec in recommendations:
        print(f"   {rec}")

    print()
    print("=" * 80)

    db.close()

if __name__ == "__main__":
    analyze_quality()
