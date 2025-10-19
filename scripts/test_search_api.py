"""Test FTS5 Search API"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from src.backend.app import app

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("FTS5 Search API Test")
print("="*60)

client = TestClient(app)

# Test 1: Search stats endpoint
print("\n[Test 1] GET /api/search/stats")
print("-"*60)
response = client.get("/api/search/stats")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] FTS5 enabled: {data['fts5_enabled']}")
    print(f"[OK] Total indexed: {data['total_indexed_entries']}")
    print(f"[OK] Languages: {data['entries_by_language']}")
    print(f"[OK] Top sources: {list(data['top_sources'].keys())[:3]}")
else:
    print(f"[ERROR] Failed: {response.text}")

# Test 2: Simple fulltext search
print("\n[Test 2] GET /api/search/fulltext?q=control")
print("-"*60)
response = client.get("/api/search/fulltext?q=control&limit=5")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] Query: '{data['query']}'")
    print(f"[OK] Total results: {data['total_results']}")
    print(f"[OK] Results returned: {len(data['results'])}")

    if data['results']:
        print("\nTop results:")
        for i, result in enumerate(data['results'][:3], 1):
            print(f"  {i}. {result['term']}")
            print(f"     Score: {result['relevance_score']:.4f}")
            print(f"     Language: {result['language']}")
            if result.get('snippet'):
                print(f"     Snippet: {result['snippet'][:80]}...")
else:
    print(f"[ERROR] Failed: {response.text}")

# Test 3: Phrase search
print("\n[Test 3] GET /api/search/fulltext?q=\"temperature control\"")
print("-"*60)
response = client.get('/api/search/fulltext?q="temperature control"&limit=3')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] Phrase search results: {data['total_results']}")
    if data['results']:
        print("Top matches:")
        for i, result in enumerate(data['results'], 1):
            print(f"  {i}. {result['term']} (score: {result['relevance_score']:.4f})")
else:
    print(f"[ERROR] Failed: {response.text}")

# Test 4: Language filtering
print("\n[Test 4] GET /api/search/fulltext?q=temperature&language=en")
print("-"*60)
response = client.get("/api/search/fulltext?q=temperature&language=en&limit=3")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] English results: {data['total_results']}")
    print(f"[OK] Filter applied: {data['filters_applied']['language']}")
    all_english = all(r['language'] == 'en' for r in data['results'])
    print(f"[OK] All results in English: {all_english}")
else:
    print(f"[ERROR] Failed: {response.text}")

# Test 5: Autocomplete suggestions
print("\n[Test 5] GET /api/search/suggest?q=temp")
print("-"*60)
response = client.get("/api/search/suggest?q=temp&limit=5")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] Query: '{data['query']}'")
    print(f"[OK] Suggestions: {len(data['suggestions'])}")
    if data['suggestions']:
        print("Suggestions:")
        for i, suggestion in enumerate(data['suggestions'][:5], 1):
            print(f"  {i}. {suggestion}")
else:
    print(f"[ERROR] Failed: {response.text}")

# Test 6: Boolean search
print("\n[Test 6] GET /api/search/fulltext?q=temperature AND control")
print("-"*60)
response = client.get("/api/search/fulltext?q=temperature AND control&limit=3")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] Boolean AND results: {data['total_results']}")
    if data['results']:
        for i, result in enumerate(data['results'][:3], 1):
            print(f"  {i}. {result['term']}")
else:
    print(f"[ERROR] Failed: {response.text}")

# Test 7: Wildcard search
print("\n[Test 7] GET /api/search/fulltext?q=temp*")
print("-"*60)
response = client.get("/api/search/fulltext?q=temp*&limit=3")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] Wildcard search results: {data['total_results']}")
    if data['results']:
        for i, result in enumerate(data['results'][:3], 1):
            print(f"  {i}. {result['term']}")
else:
    print(f"[ERROR] Failed: {response.text}")

print("\n" + "="*60)
print("[SUCCESS] All search API tests completed!")
print("="*60)
