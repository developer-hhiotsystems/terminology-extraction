# VS Code Extensions Summary

Quick reference for required extensions.

---

## ✅ When You Open Project in VS Code

**You'll see a notification:**
> "This workspace has extension recommendations."

**Click: "Install All"** - That's it! All extensions install automatically.

---

## 📦 What Gets Installed

### **Core Development (Required):**

| Extension | ID | Purpose |
|-----------|----|---------|
| Python | `ms-python.python` | Python language support, debugging |
| Pylance | `ms-python.vscode-pylance` | Fast type checking, IntelliSense |
| ESLint | `dbaeumer.vscode-eslint` | JavaScript/React linting |
| Prettier | `esbenp.prettier-vscode` | Auto code formatting |
| React Snippets | `dsznajder.es7-react-js-snippets` | React code shortcuts |

### **Testing (Included):**

| Extension | ID | Purpose |
|-----------|----|---------|
| Test Explorer | `hbenl.vscode-test-explorer` | Visual test runner |
| Python Test Adapter | `littlefoxteam.vscode-python-test-adapter` | pytest integration |

### **Optional but Helpful:**

| Extension | ID | Purpose |
|-----------|----|---------|
| GitLens | `eamodio.gitlens` | Enhanced Git features |
| Path Intellisense | `christian-kohler.path-intellisense` | Auto-complete file paths |
| Code Spell Checker | `streetsidesoftware.code-spell-checker` | Catch typos |
| IntelliCode | `visualstudioexptteam.vscodeintellicode` | AI code completion |

---

## ⚡ After Installation

### 1. Select Python Interpreter

**When you first open a Python file:**
- Click Python version in bottom-left corner
- Choose: `./venv/Scripts/python.exe`

**Or:**
- Press `Ctrl+Shift+P`
- Type: "Python: Select Interpreter"
- Choose: `./venv/Scripts/python.exe`

### 2. Verify Virtual Environment

**Check terminal:**
```bash
# Should show (venv) prefix
(venv) PS C:\...\terminology-extraction>
```

If not showing, reload window:
- `Ctrl+Shift+P` → "Developer: Reload Window"

---

## 🎯 What Each Extension Does

### **Python Extension**
- Syntax highlighting
- Code completion
- Debugging
- Linting (error checking)
- Test discovery

### **Pylance**
- Fast type checking
- Better IntelliSense
- Import suggestions
- Error detection

### **ESLint**
- Finds JavaScript/React errors
- Enforces code style
- Red squiggly lines for issues

### **Prettier**
- Auto-formats code on save
- Consistent style across team
- Formats JS, JSX, JSON, CSS

### **React Snippets**
- Type shortcuts like `rafce` → complete React component
- Speed up React development
- Reduces boilerplate

### **GitLens**
- See who changed each line (blame)
- View file history
- Compare branches visually

### **Test Explorer**
- Visual test panel
- Click to run individual tests
- See pass/fail status

---

## 🚀 Quick Actions

### Format Code
- **Auto**: Save file (Ctrl+S) - formats automatically
- **Manual**: `Shift+Alt+F`

### Run Tests
- **Method 1**: Click Testing icon → Run tests
- **Method 2**: Right-click test file → "Run Python Tests"
- **Method 3**: Terminal: `pytest tests/ -v`

### Git Operations
- **View Changes**: Click Source Control icon (Ctrl+Shift+G)
- **Commit**: Type message, click ✓
- **Push**: Click "..." → Push
- **Pull**: Click "..." → Pull

---

## 🐛 If Extensions Don't Work

### Extension Not Activating?

**Reload VS Code:**
```
Ctrl+Shift+P → "Developer: Reload Window"
```

### Python Extension Not Finding venv?

**Select interpreter manually:**
```
Ctrl+Shift+P → "Python: Select Interpreter" → ./venv/Scripts/python.exe
```

### ESLint/Prettier Not Formatting?

**Check settings:**
1. `Ctrl+,` (Settings)
2. Search: "format on save"
3. Enable checkbox
4. Search: "default formatter"
5. Choose: "Prettier - Code formatter"

### Tests Not Showing?

**Configure pytest:**
1. `Ctrl+Shift+P`
2. "Python: Configure Tests"
3. Select "pytest"
4. Select "tests" directory
5. Refresh test panel

---

## 📚 More Help

- **Full guide**: `docs/VSCODE-SETUP.md`
- **Quick start**: `QUICK-START.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

---

## ✅ Checklist

After opening project on company computer:

- [ ] VS Code shows extension recommendations notification
- [ ] Clicked "Install All" (or installed manually)
- [ ] All 12 extensions installed (green checkmarks)
- [ ] Python interpreter selected (shows in bottom-left)
- [ ] Terminal shows `(venv)` prefix
- [ ] Tests visible in Testing panel
- [ ] Format on save works (edit → save → see formatting)

**All done? Ready to test!** 🎉

---

**Need to install manually?**

See full instructions in: `docs/VSCODE-SETUP.md`
