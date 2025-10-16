#!/usr/bin/env python
"""Verify development environment setup"""
import sys
import subprocess
from pathlib import Path

def check_python_packages():
    """Check core Python packages"""
    try:
        import fastapi, neo4j, pdfplumber, pytest, deepl
        print("[OK] Core Python packages installed")
        return True
    except ImportError as e:
        print(f"[FAIL] Missing Python package: {e}")
        return False

def check_optional_packages():
    """Check optional Python packages that require C++ compiler"""
    try:
        import spacy, lxml
        print("[OK] Optional Python packages installed (spaCy, lxml)")
        return True
    except ImportError:
        print("[WARN] Optional packages not installed (spaCy, lxml) - needed for Phase 2")
        return False

def check_node_modules():
    """Check if Node.js packages are installed"""
    if Path("node_modules").exists():
        print("[OK] Node.js packages installed")
        return True
    print("[FAIL] Node.js packages not installed - run: npm install")
    return False

def check_docker():
    """Check if Docker is installed"""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("[OK] Docker installed")
        return True
    except:
        print("[WARN] Docker not installed - needed for Neo4j in Phase 2")
        return False

def check_neo4j_running():
    """Check if Neo4j is running"""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:7474", timeout=2)
        print("[OK] Neo4j is running")
        return True
    except:
        print("[WARN] Neo4j not running - start with: docker-compose -f docker-compose.dev.yml up -d")
        return False

def check_env_file():
    """Check .env file configuration"""
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        has_deepl = "YOUR_DEEPL_API_KEY_HERE" not in content
        if has_deepl:
            print("[OK] DeepL API key configured")
        else:
            print("[WARN] DeepL API key not configured - see docs/REMAINING-SETUP-TASKS.md")
        return True
    print("[FAIL] .env file missing")
    return False

def check_iate_dataset():
    """Check if IATE dataset is downloaded"""
    iate_path = Path("data/iate/IATE_export.tbx")
    if iate_path.exists():
        size_mb = iate_path.stat().st_size / (1024 * 1024)
        print(f"[OK] IATE dataset downloaded ({size_mb:.1f} MB)")
        return True
    print("[WARN] IATE dataset not downloaded - needed for Phase 2")
    return False

def check_directories():
    """Check required directories exist"""
    required_dirs = [
        "src/backend",
        "src/frontend/src",
        "tests/unit",
        "data/uploads",
        "backups/sqlite"
    ]
    all_exist = True
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"[FAIL] Missing directory: {dir_path}")
            all_exist = False
    if all_exist:
        print("[OK] All required directories exist")
    return all_exist

def check_venv():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[OK] Running in virtual environment")
        return True
    print("[WARN] Not running in virtual environment - activate with: ./venv/Scripts/activate")
    return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Development Environment Check")
    print("="*50 + "\n")

    # Required checks
    print("Required Components:")
    print("-" * 50)
    required = [
        check_venv(),
        check_python_packages(),
        check_node_modules(),
        check_directories(),
        check_env_file()
    ]

    print("\nOptional Components (Phase 2+):")
    print("-" * 50)
    optional = [
        check_optional_packages(),
        check_docker(),
        check_neo4j_running(),
        check_iate_dataset()
    ]

    print("\n" + "="*50)
    print("Summary:")
    print("="*50)
    print(f"Required: {sum(required)}/{len(required)} passed")
    print(f"Optional: {sum(optional)}/{len(optional)} passed")

    if all(required):
        print("\n[OK] Minimum requirements met - ready for Phase 1 development")
        print("\nNext steps:")
        print("  1. Test backend: python src/backend/app.py")
        print("  2. Test frontend: npm start")
        print("  3. Review: docs/IMPLEMENTATION-STRATEGY-v1.1.md")
        sys.exit(0)
    else:
        print("\n[FAIL] Missing required dependencies")
        print("\nSee docs/REMAINING-SETUP-TASKS.md for installation instructions")
        sys.exit(1)
