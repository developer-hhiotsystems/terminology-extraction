"""Quick test to initialize FTS5 index"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.database import initialize_fts5

print("Starting FTS5 initialization...")
result = initialize_fts5()
print(f"Result: {result}")
