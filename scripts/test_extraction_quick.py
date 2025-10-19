"""
Quick test of extraction pipeline with prevention-first fixes
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.backend.services.pdf_extractor import PDFExtractor
from src.backend.services.term_extractor import TermExtractor
from src.backend.services.term_validator import create_default_validator

print("="*60)
print("QUICK EXTRACTION PIPELINE TEST")
print("="*60)

# Test 1: OCR Normalization
print("\n1. Testing OCR Normalization")
test_cases = [
    ("Pplloottttiinngg", "Plotting"),
    ("cid:31 Temperature", "Temperature"),
]
for input_text, expected in test_cases:
    result = PDFExtractor._normalize_ocr_artifacts(input_text)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{input_text}' → '{result}'")

# Test 2: Article Stripping
print("\n2. Testing Article Stripping")
test_cases = [
    ("The Sensor", "Sensor"),
    ("A Process", "Process"),
]
for input_term, expected in test_cases:
    result = TermExtractor.strip_leading_articles(input_term, "en")
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{input_term}' → '{result}'")

# Test 3: PDF Artifact Rejection
print("\n3. Testing PDF Artifact Rejection")
validator = create_default_validator()

bad_terms = ["cid:31", "et al", "-tion"]
print("  Should REJECT:")
for term in bad_terms:
    is_valid = validator.is_valid_term(term)
    status = "✅" if not is_valid else "❌"
    print(f"  {status} '{term}' - {'rejected' if not is_valid else 'ACCEPTED (BAD!)'}")

good_terms = ["Sensor", "Temperature", "pH"]
print("  Should ACCEPT:")
for term in good_terms:
    is_valid = validator.is_valid_term(term)
    status = "✅" if is_valid else "❌"
    print(f"  {status} '{term}' - {'accepted' if is_valid else 'REJECTED (BAD!)'}")

# Test 4: Quick PDF extraction test
print("\n4. Testing PDF Extraction (first PDF found)")
pdf_path = project_root / "test-data" / "Single-Use_BioReactors_2020.pdf"

if pdf_path.exists():
    print(f"  Processing: {pdf_path.name}")

    # Extract text
    pdf_result = PDFExtractor.extract_text(str(pdf_path))

    if pdf_result["success"]:
        text = pdf_result["text"]
        print(f"  ✅ Extracted {len(text)} chars from {pdf_result['pages']} pages")

        # Extract terms (with validation enabled)
        extractor = TermExtractor(language="en")
        terms = extractor.extract_terms(
            text[:50000],  # Use first 50k chars for speed
            min_term_length=3,
            min_frequency=2,
            enable_validation=True
        )

        print(f"  ✅ Extracted {len(terms)} terms")

        # Check for bad patterns
        bad_count = 0
        for term_dict in terms:
            term = term_dict["term"]
            term_lower = term.lower()

            if term_lower.startswith(('the ', 'a ', 'an ')):
                print(f"  ❌ Found article: '{term}'")
                bad_count += 1
            if 'cid:' in term_lower:
                print(f"  ❌ Found PDF artifact: '{term}'")
                bad_count += 1
            if 'et al' in term_lower:
                print(f"  ❌ Found citation: '{term}'")
                bad_count += 1

        if bad_count == 0:
            print(f"  ✅ NO bad patterns found - extraction is clean!")
        else:
            print(f"  ❌ Found {bad_count} bad patterns")

        # Show sample terms
        print(f"\n  Sample of extracted terms:")
        for i, term_dict in enumerate(terms[:10]):
            print(f"    {i+1}. '{term_dict['term']}' (freq: {term_dict['frequency']})")
    else:
        print(f"  ❌ PDF extraction failed: {pdf_result['error']}")
else:
    print(f"  ⚠️  PDF not found: {pdf_path}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
