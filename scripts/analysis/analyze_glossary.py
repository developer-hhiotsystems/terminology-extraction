"""
Analyze glossary entries for quality issues
"""
from src.backend.database import SessionLocal
from src.backend.models import GlossaryEntry
import json

db = SessionLocal()

# Fetch all entries
entries = db.query(GlossaryEntry).all()

print(f"=== Glossary Quality Analysis ===")
print(f"Total entries: {len(entries)}\n")

# Categorize issues
problematic_entries = []
short_terms = []
numeric_terms = []
symbol_terms = []
incomplete_terms = []
good_entries = []

for entry in entries:
    term = entry.term
    term_len = len(term)

    # Check for various quality issues
    if term_len <= 2:
        short_terms.append(entry)
        problematic_entries.append(entry)
    elif term.isdigit():
        numeric_terms.append(entry)
        problematic_entries.append(entry)
    elif any(c in term for c in ['%', '[', ']', '{', '}', '...', '--']):
        symbol_terms.append(entry)
        problematic_entries.append(entry)
    elif term.lower() in ['the', 'and', 'or', 'of', 'to', 'in', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been']:
        incomplete_terms.append(entry)
        problematic_entries.append(entry)
    else:
        good_entries.append(entry)

# Print statistics
print(f"Quality Breakdown:")
print(f"  Good entries: {len(good_entries)} ({len(good_entries)/len(entries)*100:.1f}%)")
print(f"  Problematic entries: {len(problematic_entries)} ({len(problematic_entries)/len(entries)*100:.1f}%)")
print(f"    - Short terms (≤2 chars): {len(short_terms)}")
print(f"    - Numeric terms: {len(numeric_terms)}")
print(f"    - Symbol-heavy terms: {len(symbol_terms)}")
print(f"    - Stop words: {len(incomplete_terms)}")
print()

# Show examples of problematic entries
print("=== Problematic Entries (First 30) ===")
for i, entry in enumerate(problematic_entries[:30]):
    def_preview = entry.definitions[0]['text'][:60] if entry.definitions else "No definition"
    print(f"{i+1}. '{entry.term}' - {def_preview}...")

print()
print("=== Good Entries (First 20) ===")
for i, entry in enumerate(good_entries[:20]):
    def_preview = entry.definitions[0]['text'][:60] if entry.definitions else "No definition"
    print(f"{i+1}. '{entry.term}' - {def_preview}...")

# Save detailed report
report = {
    "total_entries": len(entries),
    "good_entries": len(good_entries),
    "problematic_entries": len(problematic_entries),
    "issues": {
        "short_terms": [e.term for e in short_terms[:20]],
        "numeric_terms": [e.term for e in numeric_terms[:20]],
        "symbol_terms": [e.term for e in symbol_terms[:20]],
        "stop_words": [e.term for e in incomplete_terms[:20]]
    },
    "recommendations": []
}

with open('glossary_quality_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✓ Detailed report saved to glossary_quality_report.json")

db.close()
