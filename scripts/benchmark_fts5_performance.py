#!/usr/bin/env python3
"""
FTS5 Performance Benchmark Suite
=================================
Compares FTS5 full-text search vs traditional LIKE queries

Tests:
1. Simple term search
2. Multiple term search
3. Wildcard search
4. Complex Boolean search
5. Filtered search (with language/domain)

Measures:
- Query execution time
- Results returned
- Speed improvement (FTS5 vs LIKE)
"""

import sqlite3
import time
import statistics
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Force UTF-8 for Windows
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("FTS5 vs LIKE Performance Benchmark Suite")
print("="*70)

# Connect to database
conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

# Get database statistics
cursor.execute("SELECT COUNT(*) FROM glossary_entries")
total_entries = cursor.fetchone()[0]
print(f"\nDatabase: {total_entries} glossary entries")

# Check FTS5 status
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='glossary_fts'")
fts5_enabled = cursor.fetchone() is not None
print(f"FTS5 Index: {'ENABLED' if fts5_enabled else 'DISABLED'}")
print("="*70)


# =============================================================================
# Benchmark Functions
# =============================================================================

def benchmark_query(query_func, iterations=10) -> Tuple[float, int]:
    """
    Run a query multiple times and measure average execution time

    Returns:
        Tuple of (average_time_ms, result_count)
    """
    times = []
    result_count = 0

    for _ in range(iterations):
        start = time.perf_counter()
        results = query_func()
        end = time.perf_counter()

        times.append((end - start) * 1000)  # Convert to milliseconds
        result_count = len(results)

    avg_time = statistics.mean(times)
    return avg_time, result_count


def fts5_simple_search(term: str) -> List:
    """FTS5 simple search"""
    cursor.execute("""
        SELECT ge.id, ge.term, bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH ?
        ORDER BY score
    """, (term,))
    return cursor.fetchall()


def like_simple_search(term: str) -> List:
    """LIKE-based simple search"""
    cursor.execute("""
        SELECT id, term, 0 AS score
        FROM glossary_entries
        WHERE term LIKE ? OR definitions LIKE ?
    """, (f'%{term}%', f'%{term}%'))
    return cursor.fetchall()


def fts5_boolean_search(query: str) -> List:
    """FTS5 Boolean search"""
    cursor.execute("""
        SELECT ge.id, ge.term, bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH ?
        ORDER BY score
    """, (query,))
    return cursor.fetchall()


def like_boolean_search(term1: str, term2: str) -> List:
    """LIKE-based AND search (both terms)"""
    cursor.execute("""
        SELECT id, term, 0 AS score
        FROM glossary_entries
        WHERE (term LIKE ? OR definitions LIKE ?)
          AND (term LIKE ? OR definitions LIKE ?)
    """, (f'%{term1}%', f'%{term1}%', f'%{term2}%', f'%{term2}%'))
    return cursor.fetchall()


def fts5_wildcard_search(prefix: str) -> List:
    """FTS5 wildcard prefix search"""
    cursor.execute("""
        SELECT ge.id, ge.term, bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH ?
        ORDER BY score
    """, (f'{prefix}*',))
    return cursor.fetchall()


def like_wildcard_search(prefix: str) -> List:
    """LIKE-based wildcard search"""
    cursor.execute("""
        SELECT id, term, 0 AS score
        FROM glossary_entries
        WHERE term LIKE ? OR definitions LIKE ?
    """, (f'{prefix}%', f'%{prefix}%'))
    return cursor.fetchall()


def fts5_filtered_search(term: str, language: str) -> List:
    """FTS5 search with language filter"""
    cursor.execute("""
        SELECT ge.id, ge.term, bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH ? AND ge.language = ?
        ORDER BY score
    """, (term, language))
    return cursor.fetchall()


def like_filtered_search(term: str, language: str) -> List:
    """LIKE-based search with language filter"""
    cursor.execute("""
        SELECT id, term, 0 AS score
        FROM glossary_entries
        WHERE (term LIKE ? OR definitions LIKE ?) AND language = ?
    """, (f'%{term}%', f'%{term}%', language))
    return cursor.fetchall()


# =============================================================================
# Benchmark Test Cases
# =============================================================================

test_cases = [
    {
        "name": "Simple Search: 'control'",
        "fts5_func": lambda: fts5_simple_search("control"),
        "like_func": lambda: like_simple_search("control"),
    },
    {
        "name": "Simple Search: 'temperature'",
        "fts5_func": lambda: fts5_simple_search("temperature"),
        "like_func": lambda: like_simple_search("temperature"),
    },
    {
        "name": "Simple Search: 'process'",
        "fts5_func": lambda: fts5_simple_search("process"),
        "like_func": lambda: like_simple_search("process"),
    },
    {
        "name": "Boolean AND: 'temperature AND control'",
        "fts5_func": lambda: fts5_boolean_search("temperature AND control"),
        "like_func": lambda: like_boolean_search("temperature", "control"),
    },
    {
        "name": "Boolean OR: 'sensor OR actuator'",
        "fts5_func": lambda: fts5_boolean_search("sensor OR actuator"),
        "like_func": lambda: like_simple_search("sensor"),  # Approximate with single term
    },
    {
        "name": "Wildcard: 'temp*'",
        "fts5_func": lambda: fts5_wildcard_search("temp"),
        "like_func": lambda: like_wildcard_search("temp"),
    },
    {
        "name": "Wildcard: 'cont*'",
        "fts5_func": lambda: fts5_wildcard_search("cont"),
        "like_func": lambda: like_wildcard_search("cont"),
    },
    {
        "name": "Filtered: 'temperature' (language=en)",
        "fts5_func": lambda: fts5_filtered_search("temperature", "en"),
        "like_func": lambda: like_filtered_search("temperature", "en"),
    },
    {
        "name": "Complex Boolean: 'process AND (control OR temperature)'",
        "fts5_func": lambda: fts5_boolean_search("process AND (control OR temperature)"),
        "like_func": lambda: like_boolean_search("process", "control"),
    },
]

# Run benchmarks
results = []
print("\nRunning benchmarks (10 iterations each)...")
print("-"*70)

for i, test in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] {test['name']}")
    print("  " + "-"*66)

    # FTS5 benchmark
    fts5_time, fts5_count = benchmark_query(test['fts5_func'], iterations=10)
    print(f"  FTS5: {fts5_time:>8.3f} ms | {fts5_count:>4} results")

    # LIKE benchmark
    like_time, like_count = benchmark_query(test['like_func'], iterations=10)
    print(f"  LIKE: {like_time:>8.3f} ms | {like_count:>4} results")

    # Calculate improvement
    if like_time > 0:
        speedup = like_time / fts5_time if fts5_time > 0 else float('inf')
        print(f"  Speed improvement: {speedup:.1f}x faster")

    results.append({
        "test": test['name'],
        "fts5_time_ms": round(fts5_time, 3),
        "like_time_ms": round(like_time, 3),
        "fts5_results": fts5_count,
        "like_results": like_count,
        "speedup": round(speedup, 2) if like_time > 0 else 0
    })

# =============================================================================
# Summary Statistics
# =============================================================================

print("\n" + "="*70)
print("BENCHMARK SUMMARY")
print("="*70)

fts5_times = [r['fts5_time_ms'] for r in results]
like_times = [r['like_time_ms'] for r in results]
speedups = [r['speedup'] for r in results if r['speedup'] > 0]

print(f"\nFTS5 Performance:")
print(f"  Average:  {statistics.mean(fts5_times):>8.3f} ms")
print(f"  Median:   {statistics.median(fts5_times):>8.3f} ms")
print(f"  Min:      {min(fts5_times):>8.3f} ms")
print(f"  Max:      {max(fts5_times):>8.3f} ms")

print(f"\nLIKE Performance:")
print(f"  Average:  {statistics.mean(like_times):>8.3f} ms")
print(f"  Median:   {statistics.median(like_times):>8.3f} ms")
print(f"  Min:      {min(like_times):>8.3f} ms")
print(f"  Max:      {max(like_times):>8.3f} ms")

print(f"\nSpeed Improvement:")
print(f"  Average:  {statistics.mean(speedups):>8.1f}x faster")
print(f"  Median:   {statistics.median(speedups):>8.1f}x faster")
print(f"  Min:      {min(speedups):>8.1f}x faster")
print(f"  Max:      {max(speedups):>8.1f}x faster")

# =============================================================================
# Save Results to JSON
# =============================================================================

report = {
    "database_stats": {
        "total_entries": total_entries,
        "fts5_enabled": fts5_enabled
    },
    "benchmark_results": results,
    "summary": {
        "fts5_avg_ms": round(statistics.mean(fts5_times), 3),
        "like_avg_ms": round(statistics.mean(like_times), 3),
        "avg_speedup": round(statistics.mean(speedups), 2),
        "median_speedup": round(statistics.median(speedups), 2),
        "max_speedup": round(max(speedups), 2)
    }
}

output_file = Path('docs/fts5_benchmark_results.json')
with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\nResults saved to: {output_file}")

# =============================================================================
# Performance Table
# =============================================================================

print("\n" + "="*70)
print("DETAILED RESULTS TABLE")
print("="*70)
print(f"\n{'Test':<45} {'FTS5 (ms)':<12} {'LIKE (ms)':<12} {'Speedup':<10}")
print("-"*70)

for r in results:
    test_name = r['test'][:44]
    print(f"{test_name:<45} {r['fts5_time_ms']:<12.3f} {r['like_time_ms']:<12.3f} {r['speedup']:<10.1f}x")

print("="*70)

# =============================================================================
# Recommendations
# =============================================================================

print("\nRECOMMENDATIONS:")
print("-"*70)

avg_speedup = statistics.mean(speedups)

if avg_speedup >= 50:
    print("[EXCELLENT] FTS5 provides exceptional performance improvement!")
    print("            Ideal for production use with current dataset size.")
elif avg_speedup >= 20:
    print("[VERY GOOD] FTS5 provides significant performance improvement.")
    print("            Recommended for production use.")
elif avg_speedup >= 10:
    print("[GOOD] FTS5 provides notable performance improvement.")
    print("       Recommended for search-heavy applications.")
elif avg_speedup >= 5:
    print("[MODERATE] FTS5 provides moderate performance improvement.")
    print("           Consider for applications with frequent searches.")
else:
    print("[LIMITED] FTS5 improvement is present but limited.")
    print("          May increase as dataset grows larger.")

print("\nNote: Performance improvement typically increases with:")
print("  - Larger datasets (10,000+ entries)")
print("  - More complex search queries")
print("  - Higher search frequency")

print("\n" + "="*70)
print("Benchmark complete!")
print("="*70)

conn.close()
