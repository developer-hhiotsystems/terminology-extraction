# VS Code Setup Guide

Quick guide for setting up VS Code for this project.

---

## 📦 Required Extensions

When you open this project in VS Code, you'll be prompted to install recommended extensions. Click **"Install All"**.

### Core Extensions (Required):

1. **Python** (`ms-python.python`)
   - Python language support
   - IntelliSense, debugging, testing

2. **Pylance** (`ms-python.vscode-pylance`)
   - Fast Python language server
   - Type checking

3. **ESLint** (`dbaeumer.vscode-eslint`)
   - JavaScript/React linting
   - Code quality

4. **Prettier** (`esbenp.prettier-vscode`)
   - Code formatting
   - Auto-format on save

5. **ES7+ React Snippets** (`dsznajder.es7-react-js-snippets`)
   - React code snippets
   - Faster development

---

## 🔧 Manual Installation (If Needed)

If the prompt doesn't appear, install manually:

**Method 1: VS Code Extensions Panel**
1. Click Extensions icon (Ctrl+Shift+X)
2. Search for extension name
3. Click Install

**Method 2: Command Line**
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension dsznajder.es7-react-js-snippets
```

---

## ⚙️ Workspace Settings

The project includes pre-configured settings in `.vscode/settings.json`:

✅ **Python**:
- Virtual environment auto-detection
- pytest configured for testing
- Auto-formatting on save

✅ **JavaScript/React**:
- ESLint enabled
- Prettier formatting
- Import updates on file move

✅ **Terminal**:
- PowerShell as default
- Virtual environment auto-activation

✅ **Git**:
- Auto-fetch enabled
- Simplified sync

---

## 🚀 After Installation

### 1. Select Python Interpreter

**First time opening the project:**
1. Press `Ctrl+Shift+P`
2. Type: "Python: Select Interpreter"
3. Choose: `./venv/Scripts/python.exe`

**Or click the Python version in the bottom-left corner**

### 2. Verify Setup

Open integrated terminal (Ctrl+\`) and run:

```powershell
# Check Python from venv
python --version

# Check packages
pip list

# Should see (venv) prefix in terminal
```

### 3. Run Tests in VS Code

**Option 1: Test Explorer**
1. Click Testing icon in sidebar (flask icon)
2. Click "Configure Python Tests"
3. Select "pytest"
4. Select "tests" directory
5. Tests appear in sidebar - click to run

**Option 2: Terminal**
```bash
pytest tests/ -v
```

---

## 🎨 Optional Extensions (Recommended)

These improve the development experience:

6. **GitLens** (`eamodio.gitlens`)
   - Enhanced Git features
   - Blame annotations, history

7. **Path Intellisense** (`christian-kohler.path-intellisense`)
   - Auto-complete file paths
   - Faster file imports

8. **Code Spell Checker** (`streetsidesoftware.code-spell-checker`)
   - Spell checking in code
   - Catches typos in comments

9. **IntelliCode** (`visualstudioexptteam.vscodeintellicode`)
   - AI-assisted code completion
   - Learns from your patterns

---

## 🐛 Troubleshooting

### Extension Not Working?

**Reload VS Code:**
1. Press `Ctrl+Shift+P`
2. Type: "Developer: Reload Window"
3. Press Enter

### Python Interpreter Not Found?

**Check virtual environment:**
```bash
# Should exist
ls venv/Scripts/python.exe

# If missing, run setup again
.\setup-windows.ps1
```

**Then select interpreter:**
1. `Ctrl+Shift+P`
2. "Python: Select Interpreter"
3. Choose `./venv/Scripts/python.exe`

### ESLint/Prettier Not Formatting?

**Check settings:**
1. `Ctrl+,` (Open Settings)
2. Search: "format on save"
3. Enable checkbox
4. Search: "default formatter"
5. Select "Prettier - Code formatter"

**Or manually format:**
- `Shift+Alt+F` (Format Document)

### Tests Not Showing in Test Explorer?

**Refresh tests:**
1. Click Testing icon
2. Click refresh icon (top of panel)

**Or configure manually:**
1. `Ctrl+Shift+P`
2. "Python: Configure Tests"
3. Select "pytest"
4. Select "tests" directory

---

## 📋 Quick Reference

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Command Palette | `Ctrl+Shift+P` |
| Open Terminal | `Ctrl+\`` |
| Open Extensions | `Ctrl+Shift+X` |
| Format Document | `Shift+Alt+F` |
| Go to File | `Ctrl+P` |
| Search in Files | `Ctrl+Shift+F` |
| Run Tests | `Ctrl+; A` |
| Debug Tests | `Ctrl+; D` |

### Useful Commands

```bash
# Activate virtual environment (if not auto-activated)
.venv\Scripts\activate

# Run backend
python src\backend\app.py

# Run frontend (in new terminal)
npm start

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_example.py -v
```

---

## ✅ Verification Checklist

After installing extensions:

- [ ] Python extension installed (green checkmark)
- [ ] Pylance installed
- [ ] ESLint installed
- [ ] Prettier installed
- [ ] Python interpreter selected (bottom-left shows "./venv/Scripts/python.exe")
- [ ] Terminal shows `(venv)` prefix when opened
- [ ] Tests visible in Testing panel
- [ ] Format on save works (edit a file, save, see formatting)

---

## 🎯 Company Computer Note

**First time on company computer:**

1. **Clone project:**
   ```bash
   git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
   cd terminology-extraction
   ```

2. **Run setup:**
   ```bash
   .\setup-windows.ps1
   ```

3. **Open in VS Code:**
   ```bash
   code .
   ```

4. **Install recommended extensions** when prompted

5. **Select Python interpreter** (`./venv/Scripts/python.exe`)

**Done!** Ready to test.

---

## 📚 Additional Resources

- **VS Code Python**: https://code.visualstudio.com/docs/python/python-tutorial
- **VS Code React**: https://code.visualstudio.com/docs/nodejs/reactjs-tutorial
- **Testing in VS Code**: https://code.visualstudio.com/docs/python/testing

---

**Questions?**
- Check: `TROUBLESHOOTING.md`
- Or open an issue on GitHub
