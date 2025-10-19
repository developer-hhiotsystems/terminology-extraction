# Remaining Setup Tasks

This document outlines the remaining tasks to complete the full development environment setup.

## Task 1: Install Microsoft C++ Build Tools ⚙️

### Why Needed:
Required to compile Python packages: spaCy, lxml, mutmut, python-Levenshtein

### When Needed:
- **Phase 2**: NLP extraction (spaCy)
- **Phase 2**: IATE import (lxml)
- **Phase 3**: Mutation testing (mutmut)
- **Phase 2**: String similarity (python-Levenshtein)

### Installation Steps:

**Option 1: Visual Studio Build Tools (Recommended)**
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select "Desktop development with C++"
4. Click Install (requires ~6 GB disk space)
5. Restart your computer after installation

**Option 2: Visual Studio Community (Full IDE)**
1. Download from: https://visualstudio.microsoft.com/vs/community/
2. During installation, select "Desktop development with C++"
3. Install and restart

### Verification:
```bash
# After installation, open a new terminal
cd "C:\Users\devel\Coding Projects\Glossary APP"
./venv/Scripts/activate
pip install -r requirements.txt
```

Expected: All packages install successfully, including spaCy, lxml, mutmut

### Download spaCy Language Model:
```bash
./venv/Scripts/python -m spacy download en_core_web_sm
```

---

## Task 2: Install Docker Desktop 🐳

### Why Needed:
To run Neo4j graph database in a container

### When Needed:
- **Phase 2**: Graph database for terminology relationships
- **Phase 3**: Integration testing with Neo4j

### Installation Steps:

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download for Windows
   - Requires Windows 10/11 Pro, Enterprise, or Education with Hyper-V

2. **Install Docker Desktop**
   - Run installer
   - Enable WSL 2 backend if prompted
   - Restart computer

3. **Start Docker Desktop**
   - Launch Docker Desktop from Start menu
   - Wait for Docker engine to start (whale icon in system tray)

4. **Start Neo4j Container**
   ```bash
   cd "C:\Users\devel\Coding Projects\Glossary APP"
   docker-compose -f docker-compose.dev.yml up -d
   ```

5. **Verify Neo4j is Running**
   - Open browser: http://localhost:7474
   - Login: neo4j / devpassword
   - Run test query: `RETURN 1`

### Alternative: Neo4j Desktop (No Docker Required)

If you cannot install Docker:

1. Download Neo4j Desktop: https://neo4j.com/download/
2. Install and create a new database
3. Set password to `devpassword`
4. Update `.env`:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=devpassword
   ```

---

## Task 3: Configure DeepL API Key 🔑

### Why Needed:
Translation service for terminology validation

### When Needed:
- **Phase 2**: Term translation features
- **Phase 3**: Multi-language support

### Setup Steps:

1. **Sign Up for DeepL API**
   - Visit: https://www.deepl.com/pro-api
   - Click "Sign up for free"
   - Free tier: 500,000 characters/month
   - Verify email

2. **Get API Key**
   - Login to DeepL account
   - Go to Account Settings > API Keys
   - Copy your API key

3. **Configure in Project**
   ```bash
   # Open .env file
   notepad .env

   # Replace this line:
   DEEPL_API_KEY=YOUR_DEEPL_API_KEY_HERE

   # With your actual key:
   DEEPL_API_KEY=your-actual-api-key-here

   # Save and close
   ```

4. **Verify API Key**
   ```bash
   ./venv/Scripts/python -c "import deepl; translator = deepl.Translator('YOUR_KEY'); print('DeepL API key valid')"
   ```

---

## Task 4: Download IATE Dataset 📚

### Why Needed:
Reference terminology database for validation (Inter-Active Terminology for Europe)

### When Needed:
- **Phase 2**: Terminology validation
- **Phase 3**: Quality assurance

### Download Steps:

1. **Visit IATE Download Page**
   - URL: https://iate.europa.eu/download-iate
   - No account required for public data

2. **Download Dataset**
   - Choose format: TBX (TermBase eXchange) recommended
   - Alternative: CSV format
   - File size: ~500 MB compressed
   - Download time: 5-10 minutes

3. **Save to Project**
   ```bash
   # Create IATE directory if not exists
   mkdir -p "data/iate"

   # Move downloaded file
   move "%USERPROFILE%\Downloads\IATE_export.tbx" "C:\Users\devel\Coding Projects\Glossary APP\data\iate\IATE_export.tbx"
   ```

4. **Verify in .env**
   ```
   IATE_DATASET_PATH=./data/iate/IATE_export.tbx
   ```

5. **Update Quarterly**
   - IATE releases updates quarterly
   - Set reminder to download new version
   - Replace old file with new export

---

## Task 5: Address NPM Vulnerabilities 🔒

### Current Status:
14 vulnerabilities (2 low, 3 moderate, 9 high)

### Resolution Steps:

1. **Run Audit Fix**
   ```bash
   cd "C:\Users\devel\Coding Projects\Glossary APP"
   npm audit fix
   ```

2. **Check Remaining Issues**
   ```bash
   npm audit
   ```

3. **Force Fix (if needed)**
   ```bash
   npm audit fix --force
   ```
   ⚠️ Warning: May introduce breaking changes

4. **Manual Review**
   - Review `npm audit` output
   - Check if vulnerabilities affect production code
   - Many are dev dependencies or false positives

5. **Verify Application Still Works**
   ```bash
   npm start
   ```

---

## Task 6: Complete Pre-Phase Checklist 📋

Review and complete all items in `docs/PRE-PHASE-CHECKLIST.md`:

### Agent A2 (NLP Engineer):
- [ ] Create NLP ground truth corpus (500 term-definition pairs)

### Agent A3 (Graph Database Engineer):
- [ ] Complete Neo4j GraphAcademy bootcamp (~8 hours)
  - URL: https://graphacademy.neo4j.com/

### Agent A6 (Integration Specialist):
- [ ] Download IATE dataset (covered above)

### Agent A7 (DevOps Engineer):
- [x] Setup Neo4j (covered above)
- [x] Install dependencies (completed)
- [ ] Create SQLite backup script
- [ ] Generate Docker secrets for production
- [ ] Create comprehensive .env.example

### Agent A8 (Project Manager):
- [ ] Review and approve PRT v2.2
- [ ] Review and approve IMPLEMENTATION-STRATEGY v1.1

---

## Automated Setup Script

Create `setup-check.py` to verify all installations:

```python
#!/usr/bin/env python
"""Verify development environment setup"""
import sys
import subprocess
from pathlib import Path

def check_python_packages():
    try:
        import fastapi, neo4j, pdfplumber, pytest, deepl
        print("✓ Core Python packages installed")
        return True
    except ImportError as e:
        print(f"✗ Missing Python package: {e}")
        return False

def check_optional_packages():
    try:
        import spacy, lxml
        print("✓ Optional Python packages installed")
        return True
    except ImportError:
        print("⚠ Optional packages not installed (spaCy, lxml)")
        return False

def check_node_modules():
    if Path("node_modules").exists():
        print("✓ Node.js packages installed")
        return True
    print("✗ Node.js packages not installed")
    return False

def check_docker():
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("✓ Docker installed")
        return True
    except:
        print("⚠ Docker not installed")
        return False

def check_env_file():
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        has_deepl = "YOUR_DEEPL_API_KEY_HERE" not in content
        if has_deepl:
            print("✓ DeepL API key configured")
        else:
            print("⚠ DeepL API key not configured")
        return True
    print("✗ .env file missing")
    return False

def check_iate_dataset():
    iate_path = Path("data/iate/IATE_export.tbx")
    if iate_path.exists():
        print("✓ IATE dataset downloaded")
        return True
    print("⚠ IATE dataset not downloaded")
    return False

if __name__ == "__main__":
    print("\n=== Development Environment Check ===\n")

    checks = [
        check_python_packages(),
        check_optional_packages(),
        check_node_modules(),
        check_docker(),
        check_env_file(),
        check_iate_dataset()
    ]

    print("\n=== Summary ===")
    print(f"Required: {sum(checks[:3])}/3")
    print(f"Optional: {sum(checks[3:])}/3")

    if all(checks[:3]):
        print("\n✓ Minimum requirements met - ready for Phase 1")
    else:
        print("\n✗ Missing required dependencies")
        sys.exit(1)
```

Save as `setup-check.py` and run:
```bash
./venv/Scripts/python setup-check.py
```

---

## Quick Reference

### Installation Priority:

**High Priority (Required for Phase 1):**
- [x] Python packages ✓
- [x] Node.js packages ✓
- [x] Configuration files ✓

**Medium Priority (Required for Phase 2):**
- [ ] C++ Build Tools (for spaCy, lxml)
- [ ] Docker Desktop (for Neo4j)
- [ ] DeepL API key

**Low Priority (Required for Phase 3):**
- [ ] IATE dataset
- [ ] Mutation testing packages

### Estimated Time:
- C++ Build Tools: 30-45 minutes
- Docker Desktop: 15-30 minutes
- DeepL API setup: 5-10 minutes
- IATE download: 10-15 minutes
- NPM audit fix: 5 minutes

**Total**: 1.5 - 2 hours

---

## Next Steps After Completion

1. Run verification script: `./venv/Scripts/python setup-check.py`
2. Test backend: `python src/backend/app.py`
3. Test frontend: `npm start`
4. Review Phase 1 tasks in `docs/IMPLEMENTATION-STRATEGY-v1.1.md`
5. Begin concurrent agent execution for Phase 1 development

---

**Last Updated**: October 16, 2025
