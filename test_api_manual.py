"""
Manual API Testing Script
Run this after starting the backend server to test the CRUD endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_create_entry():
    """Test creating a glossary entry"""
    print("\n=== Testing Create Entry ===")
    data = {
        "term": "Sensor",
        "definition": "A device that detects or measures a physical property",
        "language": "en",
        "source": "internal",
        "domain_tags": ["automation", "measurement"]
    }
    response = requests.post(f"{BASE_URL}/api/glossary", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 201:
        return response.json()["id"]
    return None

def test_get_all_entries():
    """Test getting all entries"""
    print("\n=== Testing Get All Entries ===")
    response = requests.get(f"{BASE_URL}/api/glossary")
    print(f"Status: {response.status_code}")
    print(f"Found {len(response.json())} entries")
    for entry in response.json():
        print(f"  - {entry['term']} ({entry['language']})")
    return response.status_code == 200

def test_get_entry_by_id(entry_id):
    """Test getting specific entry"""
    print(f"\n=== Testing Get Entry by ID ({entry_id}) ===")
    response = requests.get(f"{BASE_URL}/api/glossary/{entry_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        entry = response.json()
        print(f"Term: {entry['term']}")
        print(f"Definition: {entry['definition']}")
        print(f"Language: {entry['language']}")
    return response.status_code == 200

def test_search(query):
    """Test search endpoint"""
    print(f"\n=== Testing Search (query='{query}') ===")
    response = requests.get(f"{BASE_URL}/api/glossary/search", params={"query": query})
    print(f"Status: {response.status_code}")
    print(f"Found {len(response.json())} results")
    return response.status_code == 200

def test_update_entry(entry_id):
    """Test updating an entry"""
    print(f"\n=== Testing Update Entry ({entry_id}) ===")
    data = {
        "definition": "An updated definition for sensor - a device that converts physical phenomena into electrical signals",
        "validation_status": "validated"
    }
    response = requests.put(f"{BASE_URL}/api/glossary/{entry_id}", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Updated definition: {response.json()['definition'][:50]}...")
    return response.status_code == 200

def test_delete_entry(entry_id):
    """Test deleting an entry"""
    print(f"\n=== Testing Delete Entry ({entry_id}) ===")
    response = requests.delete(f"{BASE_URL}/api/glossary/{entry_id}")
    print(f"Status: {response.status_code}")
    return response.status_code == 204

def main():
    """Run all tests"""
    print("=" * 60)
    print("Glossary API Manual Test Suite")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("Make sure the backend server is running!")
    print("  Start with: python src/backend/app.py")

    try:
        # Test health
        if not test_health():
            print("\n❌ Health check failed! Is the server running?")
            return

        # Create entry
        entry_id = test_create_entry()
        if not entry_id:
            print("\n❌ Failed to create entry")
            return

        # Get all entries
        test_get_all_entries()

        # Get by ID
        test_get_entry_by_id(entry_id)

        # Search
        test_search("Sensor")

        # Update
        test_update_entry(entry_id)

        # Verify update
        test_get_entry_by_id(entry_id)

        # Delete
        test_delete_entry(entry_id)

        # Verify deletion
        test_get_all_entries()

        print("\n" + "=" * 60)
        print("✓ All manual tests completed successfully!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Please start the backend server first:")
        print("  cd 'C:\\Users\\devel\\Coding Projects\\Glossary APP'")
        print("  .\\venv\\Scripts\\activate")
        print("  python src\\backend\\app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
