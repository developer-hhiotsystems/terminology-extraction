import requests

# Test reset API directly
print("Testing reset API...")

# Get stats before
response = requests.get("http://localhost:9123/api/admin/stats")
before = response.json()
print(f"Before: {before.get('total_glossary_entries', 0)} entries")

# Call reset
response = requests.delete("http://localhost:9123/api/admin/reset-database")
print(f"Reset response status: {response.status_code}")
print(f"Reset response: {response.json()}")

# Get stats after
response = requests.get("http://localhost:9123/api/admin/stats")
after = response.json()
print(f"After: {after.get('total_glossary_entries', 0)} entries")

if after.get('total_glossary_entries', 0) == 0:
    print("\n✅ RESET WORKED!")
else:
    print(f"\n❌ RESET FAILED - Still {after.get('total_glossary_entries', 0)} entries")
