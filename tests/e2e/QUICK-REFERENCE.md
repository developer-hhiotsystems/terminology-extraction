# E2E Test Suite - Quick Reference Card

## Run Tests

```bash
# Run all tests
npm test

# Run specific suite
npm run test:comprehensive  # All features
npm run test:api           # API integration
npm run test:search        # Search deep dive
npm run test:relationship  # Graph visualization
npm run test:enhanced      # Enhanced glossary

# Clean up
npm run clean
```

## Windows Quick Start

```bash
cd tests\e2e
RUN-TESTS.bat
```

## Check Prerequisites

✅ Backend running: http://localhost:9123
✅ Frontend running: http://localhost:3000
✅ Dependencies installed: `npm install` in tests/e2e

## Files Created

| File | Purpose | Size |
|------|---------|------|
| `comprehensive-feature-test.js` | Tests all features | 17.8 KB |
| `api-integration-test.js` | Tests API calls | 14.0 KB |
| `search-feature-test.js` | Tests search modes | 17.5 KB |
| `relationship-feature-test.js` | Tests graph viz | 16.5 KB |
| `enhanced-glossary-test.js` | Tests enhanced UI | 16.1 KB |
| `test-utils.js` | Helper utilities | 10.8 KB |
| `run-all-tests.js` | Master runner | 11.4 KB |
| `package.json` | npm config | 0.8 KB |
| `README.md` | Full docs | 11.2 KB |
| `RUN-TESTS.bat` | Windows script | 1.6 KB |
| `TEST-SUITE-SUMMARY.md` | Complete summary | 10.5 KB |

## Test Coverage Summary

| Category | Tests | What's Tested |
|----------|-------|---------------|
| **Navigation** | 8 | Homepage, all nav links, routing |
| **Glossary** | 10 | Main view, enhanced view, cards, bulk ops |
| **Search** | 15 | Simple, autocomplete, advanced, Boolean |
| **API** | 15 | All endpoints, responses, errors |
| **Relationships** | 18 | Graph, nodes, edges, interactions |
| **Documents** | 5 | Upload, list, detail view |
| **UI Features** | 5 | Shortcuts, modals, toggles |
| **TOTAL** | **75+** | **All major features** |

## Reports Generated

```
tests/e2e/
├── test-results-consolidated.json      ← MASTER REPORT
├── test-results-comprehensive.json
├── test-results-api.json
├── test-results-search.json
├── test-results-relationship.json
└── test-results-enhanced-glossary.json
```

## Screenshots Location

```
tests/e2e/test-screenshots/
├── success/    ← Passing tests
├── failures/   ← Failed tests (auto-captured)
└── test/       ← General screenshots
```

## Understanding Results

### Console Output

```
✅ PASSED: Test Name        ← Test passed
❌ FAILED: Test Name        ← Test failed
⚠️  Warning message         ← Non-critical issue
```

### Priority Levels

- 🔥 **HIGH**: Critical (API, navigation, search)
- ⚠️ **MEDIUM**: Important (filters, interactions)
- 💡 **LOW**: Nice-to-have (export, shortcuts)

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ERR_CONNECTION_REFUSED` | Start backend: `python run_backend.py` |
| `Element not found` | UI changed - update selectors in test files |
| Tests timeout | Increase timeouts in test files |
| Permission errors | Run as admin or check file permissions |

## Test File Structure

```javascript
// Each test follows this pattern:
async testFeatureName() {
  await this.runTest(
    'Feature Name',              // Test name
    'What it tests',             // Description
    async () => {
      // 1. Navigate
      await this.page.goto(URL);

      // 2. Find element
      const element = await this.page.$('selector');

      // 3. Assert
      assert(element !== null, 'Error message');

      // 4. Screenshot
      await takeScreenshot(this.page, 'name');
    }
  );
}
```

## Extending Tests

### Add a new test to existing suite:

1. Open appropriate test file
2. Add test method (see structure above)
3. Add to `runAllTests()` method
4. Run and verify

### Create a new test suite:

1. Copy `comprehensive-feature-test.js`
2. Rename and update class name
3. Add to `run-all-tests.js` testSuites array
4. Run with `npm test`

## CI/CD Integration

Add to `.github/workflows/e2e-tests.yml`:

```yaml
- name: Run E2E Tests
  run: |
    cd tests/e2e
    npm install
    npm test
```

## Performance Benchmarks

- Individual suite: **30-60s**
- All suites: **2-5 min**
- Headless mode: **30-50% faster**

## Success Criteria

✅ **Pass Rate**: >90%
✅ **HIGH Priority**: 100% pass
✅ **MEDIUM Priority**: >85% pass
✅ **API Tests**: 100% pass

## Key Test Utilities

| Function | Purpose |
|----------|---------|
| `waitForElement(selector)` | Wait for element to appear |
| `waitAndClick(selector)` | Wait then click |
| `waitAndType(selector, text)` | Wait then type |
| `takeScreenshot(page, name)` | Capture screenshot |
| `assert(condition, msg)` | Test assertion |
| `elementExists(selector)` | Check if element exists |
| `getElementCount(selector)` | Count elements |

## Troubleshooting Commands

```bash
# Check if servers running
curl http://localhost:3000
curl http://localhost:9123

# View test results
cat test-results-consolidated.json

# Find failure screenshots
ls test-screenshots/failures/

# Re-run failed suite only
npm run test:api  # example
```

## Support Checklist

Before asking for help:

- [ ] Both servers running?
- [ ] Dependencies installed? (`npm install`)
- [ ] Checked console output?
- [ ] Reviewed screenshots?
- [ ] Checked test-results-consolidated.json?
- [ ] Verified browser can access http://localhost:3000?

## Important Notes

- ⚠️ Tests run in **non-headless mode** by default (you'll see browser)
- ⚠️ Each test suite runs **independently**
- ⚠️ Screenshots are **auto-captured on failures**
- ⚠️ Tests **require both frontend and backend** running

## One-Line Test Execution

```bash
# From project root
cd tests/e2e && npm install && npm test
```

## View Last Test Results

```bash
# Windows
type test-results-consolidated.json

# Mac/Linux
cat test-results-consolidated.json | jq .summary
```

---

**Quick Help**: See `README.md` for full documentation

**Version**: 2.0.0 | **Tests**: 75+ | **Suites**: 5
