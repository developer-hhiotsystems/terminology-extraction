"""
Quality Analysis Script for Term Extraction
Analyzes the quality of extracted terms against industry standards
"""
import sqlite3
import json
import re
from collections import Counter

def analyze_term_quality():
    """Analyze quality of extracted terms"""
    conn = sqlite3.connect('data/glossary.db')
    cursor = conn.cursor()

    # Get all terms
    cursor.execute('SELECT term, definitions FROM glossary_entries')
    rows = cursor.fetchall()

    total_terms = len(rows)
    quality_issues = {
        'fragments': [],
        'stop_words': [],
        'too_short': [],
        'symbols': [],
        'abbreviations': [],
        'duplicates': [],
        'non_semantic': [],
        'formatting_errors': []
    }

    stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have',
                  'our', 'time', 'method', 'fact', 'single'}

    seen_terms = {}

    for term, definitions in rows:
        term_lower = term.lower()

        # Check for duplicates (case variations)
        if term_lower in seen_terms:
            quality_issues['duplicates'].append(f"{term} (duplicate of {seen_terms[term_lower]})")
        else:
            seen_terms[term_lower] = term

        # Check for word fragments
        if term.endswith('-') or term.startswith('-'):
            quality_issues['fragments'].append(term)
        elif re.search(r'\b[A-Za-z]{1,2}ons?\b', term):  # "ations", "ions"
            quality_issues['fragments'].append(term)
        elif re.search(r'^(Ing|Res|Des|Sub|Chem|Eng|Tech|Technol)$', term):
            quality_issues['fragments'].append(term)

        # Check for stop words
        if term_lower in stop_words:
            quality_issues['stop_words'].append(term)

        # Check for too short (< 3 chars)
        if len(term) < 3:
            quality_issues['too_short'].append(term)

        # Check for pure symbols
        if re.match(r'^[^a-zA-Z0-9]+$', term):
            quality_issues['symbols'].append(term)

        # Check for abbreviations without context
        if len(term) == 2 or (len(term) == 3 and term.isupper()):
            quality_issues['abbreviations'].append(term)

        # Check for non-semantic terms (repeated characters)
        if re.search(r'(.)\1{2,}', term):  # "Tthhee", "Oonn"
            quality_issues['formatting_errors'].append(term)

        # Check for non-semantic standalone words
        if term in ['Et Al', 'Sponse Time', 'Tthhee', 'Oonn']:
            quality_issues['non_semantic'].append(term)

    # Calculate statistics
    total_issues = sum(len(v) for v in quality_issues.values())
    quality_score = ((total_terms - total_issues) / total_terms * 100) if total_terms > 0 else 0

    # Print report
    print("="*80)
    print("TERM EXTRACTION QUALITY ANALYSIS REPORT")
    print("="*80)
    print(f"\nTotal Terms Extracted: {total_terms}")
    print(f"Total Quality Issues Found: {total_issues}")
    print(f"Overall Quality Score: {quality_score:.1f}%")
    print(f"\n{'='*80}")
    print("QUALITY ISSUES BREAKDOWN:")
    print("="*80)

    for category, issues in quality_issues.items():
        if len(issues) > 0:
            print(f"\n{category.upper()}: {len(issues)} issues ({len(issues)/total_terms*100:.1f}%)")
            # Handle unicode encoding issues
            try:
                examples = ', '.join(issues[:10])
                print(f"  Examples: {examples}")
            except UnicodeEncodeError:
                print(f"  Examples: [Unicode encoding issues - {len(issues[:10])} terms]")

    # Semantic quality assessment
    print(f"\n{'='*80}")
    print("SEMANTIC QUALITY DIMENSIONS:")
    print("="*80)

    cursor.execute('SELECT term FROM glossary_entries WHERE LENGTH(term) >= 8')
    meaningful_terms = cursor.fetchall()

    cursor.execute('SELECT term FROM glossary_entries WHERE term LIKE "% %"')
    compound_terms = cursor.fetchall()

    cursor.execute('SELECT term FROM glossary_entries WHERE term GLOB "*[A-Z]*" AND term != UPPER(term)')
    proper_case_terms = cursor.fetchall()

    print(f"\nMeaningful Terms (>=8 chars): {len(meaningful_terms)} ({len(meaningful_terms)/total_terms*100:.1f}%)")
    print(f"Compound Terms (multi-word): {len(compound_terms)} ({len(compound_terms)/total_terms*100:.1f}%)")
    print(f"Properly Formatted: {len(proper_case_terms)} ({len(proper_case_terms)/total_terms*100:.1f}%)")

    # Sample high-quality terms
    cursor.execute('''
        SELECT term FROM glossary_entries
        WHERE LENGTH(term) >= 10
        AND term LIKE "% %"
        AND term NOT LIKE "%-%"
        LIMIT 20
    ''')
    good_terms = cursor.fetchall()

    print(f"\n{'='*80}")
    print("SAMPLE HIGH-QUALITY TERMS:")
    print("="*80)
    for i, (term,) in enumerate(good_terms, 1):
        print(f"  {i}. {term}")

    conn.close()

    return {
        'total_terms': total_terms,
        'total_issues': total_issues,
        'quality_score': quality_score,
        'issues': quality_issues
    }

if __name__ == "__main__":
    analyze_term_quality()
