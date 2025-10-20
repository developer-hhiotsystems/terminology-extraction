# Glossary APP - Comprehensive E2E Test Suite

This directory contains a **comprehensive Puppeteer-based E2E testing infrastructure** that thoroughly tests every feature, button, API integration, and user interaction in the Glossary APP.

## Overview

The test suite consists of 5 specialized test modules that cover all application features:

1. **Comprehensive Feature Test** - Tests all navigation, UI elements, and basic functionality
2. **API Integration Test** - Verifies frontend-backend API communication
3. **Search Feature Test** - Deep dive into all 4 FTS5 search modes
4. **Relationship Feature Test** - Tests graph visualization and interactions
5. **Enhanced Glossary Test** - Tests bilingual cards and bulk operations

## Prerequisites

### 1. Install Dependencies

```bash
cd tests/e2e
npm install
```

### 2. Start the Application

**You MUST have both frontend and backend running:**

```bash
# Terminal 1 - Start Backend API
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python run_backend.py

# Terminal 2 - Start Frontend
cd src/frontend
npm run dev
```

Verify servers are running:
- Frontend: http://localhost:3000
- Backend API: http://localhost:9123

## Running Tests

### Run All Tests (Recommended)

```bash
npm test
```

This runs the complete test suite and generates a consolidated report.

### Run Individual Test Suites

```bash
# Comprehensive feature tests
npm run test:comprehensive

# API integration tests
npm run test:api

# Search feature tests
npm run test:search

# Relationship explorer tests
npm run test:relationship

# Enhanced glossary tests
npm run test:enhanced
```

### Clean Test Artifacts

```bash
npm run clean
```

## Test Coverage

### 1. Comprehensive Feature Test (`comprehensive-feature-test.js`)

Tests **25+ core features** including:

#### Navigation Tests
- Homepage loads correctly
- All navigation links exist and work
- Navigation to Search, Enhanced Glossary, Relationships, Documents, Statistics, Admin
- URL routing verification

#### Main Glossary Tests
- Glossary page loads and displays terms
- Search box functionality
- Term filtering

#### Search Page Tests
- Search mode selector exists
- Search input field present
- Search button functionality

#### Enhanced Glossary Tests
- Bilingual cards display
- Bulk operations UI

#### Relationship Explorer Tests
- Graph visualization renders
- Filter controls exist

#### Documents Tests
- Upload functionality present
- Documents list displays

#### UI Features Tests
- Keyboard shortcuts button
- Keyboard shortcuts modal opens

### 2. API Integration Test (`api-integration-test.js`)

Tests **15+ API integrations** including:

#### API Call Verification
- `/api/glossary` - Fetch terms
- `/api/search` or `/api/fts` - Search functionality
- `/api/autocomplete` - Autocomplete suggestions
- `/api/relationship` or `/api/graph` - Relationship data
- `/api/documents` - Documents list
- `/api/statistics` - Statistics data

#### Response Handling
- API responses parsed correctly
- Data displayed in UI
- Error states handled gracefully
- Network failures caught

#### Performance
- API response time measurement
- Average response time calculation

### 3. Search Feature Test (`search-feature-test.js`)

Tests **all 4 FTS5 search modes** including:

#### Simple Search
- Basic text search
- Results display
- "No results" handling

#### Autocomplete
- Dropdown appears on typing
- Suggestions displayed
- Suggestion selection works

#### Advanced Search
- Mode switching
- Filter controls
- Advanced query features

#### Boolean Search
- Boolean mode activation
- AND/OR/NOT operators
- Complex query handling

#### Interactions
- Clear button
- Keyboard navigation (Enter, Escape)

### 4. Relationship Feature Test (`relationship-feature-test.js`)

Tests **15+ relationship features** including:

#### Graph Visualization
- SVG/Canvas rendering
- Nodes displayed
- Edges/links rendered

#### Graph Interactions
- Node hover effects
- Node click handling
- Zoom in/out
- Pan/drag functionality

#### Filters and Controls
- Filter controls exist
- Filter interaction
- Legend display
- Node labels

#### Data Loading
- API calls for graph data
- Loading states
- Error handling

#### Export
- Export button availability

### 5. Enhanced Glossary Test (`enhanced-glossary-test.js`)

Tests **15+ enhanced features** including:

#### Bilingual Cards
- Cards display
- Card flip animation
- Bilingual content verification

#### Bulk Operations
- Bulk operations section
- Select checkboxes
- "Select All" functionality
- Bulk action buttons

#### Filters and Sort
- Filter controls
- Sort options
- Pagination
- Page navigation

#### View Modes
- Grid/list view toggle
- Detail view modal

## Test Reports

### Generated Reports

After running tests, detailed JSON reports are saved:

```
tests/e2e/
├── test-results-consolidated.json    # Master report (ALL tests)
├── test-results-comprehensive.json   # Feature tests
├── test-results-api.json            # API tests
├── test-results-search.json         # Search tests
├── test-results-relationship.json   # Relationship tests
└── test-results-enhanced-glossary.json  # Enhanced glossary tests
```

### Consolidated Report Structure

```json
{
  "testDate": "2025-10-19T...",
  "duration": "45.23s",
  "summary": {
    "totalSuites": 5,
    "totalTests": 75,
    "passed": 60,
    "failed": 15,
    "passRate": "80.00"
  },
  "suites": [...],
  "brokenFeatures": [
    {
      "feature": "Search - Autocomplete",
      "priority": "HIGH",
      "errors": [...]
    }
  ],
  "recommendations": [
    {
      "category": "API Integration",
      "severity": "CRITICAL",
      "issue": "Backend not responding",
      "action": "Verify backend is running on port 9123"
    }
  ]
}
```

## Screenshots

Test screenshots are automatically captured:

```
tests/e2e/test-screenshots/
├── success/          # Success state screenshots
├── failures/         # Failure screenshots
└── test/            # General test screenshots
```

Screenshots are taken:
- **On success**: Key feature states
- **On failure**: Automatic screenshot with error context
- **On interactions**: Before/after major actions

## Understanding Test Results

### Console Output

The test runner provides real-time feedback:

```
🧪 Testing: Homepage Loads
✅ PASSED: Homepage Loads

🧪 Testing: Search API Call
⚠️  No /api/search request detected
❌ FAILED: Search API Call - API not called
```

### Priority Levels

Broken features are categorized:

- **HIGH**: Critical features (API, navigation, search)
- **MEDIUM**: Important features (filters, interactions)
- **LOW**: Nice-to-have features (export, keyboard shortcuts)

### Pass/Fail Criteria

Each test:
- ✅ **PASS**: Feature works as expected
- ❌ **FAIL**: Feature broken or not found
- ⚠️ **WARN**: Feature might be missing but test continues

## Troubleshooting

### Common Issues

#### 1. "net::ERR_CONNECTION_REFUSED"

**Problem**: Backend server not running

**Solution**:
```bash
cd backend
source venv/bin/activate
python run_backend.py
```

#### 2. "Element not found" errors

**Problem**: Frontend UI changed or not fully loaded

**Solutions**:
- Increase timeout in test
- Verify frontend is running
- Check browser console for errors

#### 3. Tests timeout

**Problem**: Application loading slowly

**Solutions**:
- Increase `waitForTimeout` values
- Check network tab for slow API calls
- Verify database is responsive

#### 4. Screenshot permission errors

**Problem**: Cannot write to screenshots directory

**Solution**:
```bash
mkdir -p tests/e2e/test-screenshots/{success,failures,test}
chmod 755 tests/e2e/test-screenshots
```

### Debug Mode

Run tests with browser visible (non-headless):

Tests already run in non-headless mode by default. To switch to headless:

```javascript
// In test-utils.js, change:
headless: false  // to
headless: true
```

## Test Configuration

### Timeouts

Default timeouts in `test-utils.js`:

```javascript
waitForElement: 5000ms    // Element wait timeout
waitForNetworkIdle: 5000ms // Network idle timeout
waitForTimeout: 300ms      // Small delays after actions
```

### Viewport

Default viewport: 1920x1080 (can be changed in `test-utils.js`)

### Browser Args

```javascript
args: [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-web-security',
  '--disable-features=IsolateOrigins,site-per-process'
]
```

## Extending Tests

### Adding New Tests

1. Create test method in appropriate test class:

```javascript
async testNewFeature() {
  await this.runTest(
    'New Feature Name',
    'Description of what it tests',
    async () => {
      // Your test code
      await this.page.goto(`${FRONTEND_URL}/feature`);
      const element = await this.page.$('.selector');
      assert(element !== null, 'Element not found');
    }
  );
}
```

2. Add to `runAllTests()` method:

```javascript
async runAllTests() {
  // ...existing tests
  await this.testNewFeature();
}
```

### Creating New Test Suite

1. Copy existing test file
2. Rename class and update tests
3. Add to `run-all-tests.js`:

```javascript
const NewTest = require('./new-test');

this.testSuites = [
  // ...existing
  { name: 'New Test Suite', class: NewTest, priority: 'HIGH' }
];
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Start Backend
        run: |
          cd backend
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
          python run_backend.py &

      - name: Start Frontend
        run: |
          cd src/frontend
          npm install
          npm run dev &

      - name: Run E2E Tests
        run: |
          cd tests/e2e
          npm install
          npm test

      - name: Upload Test Reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: tests/e2e/test-results-*.json
```

## Best Practices

1. **Always start servers before testing**
2. **Run tests in isolation** - each test should be independent
3. **Check screenshots** - they provide valuable debugging info
4. **Review consolidated report** - it prioritizes issues
5. **Fix HIGH priority issues first** - these are critical features
6. **Update tests when UI changes** - keep selectors in sync

## Test Maintenance

### Regular Updates Needed

- Update selectors when UI changes
- Add tests for new features
- Remove tests for deprecated features
- Adjust timeouts as needed
- Update API endpoints

### Review Schedule

- **Daily**: Check test results
- **Weekly**: Review broken features
- **Monthly**: Update test coverage
- **Per Release**: Full test suite validation

## Support

For issues or questions:

1. Check test output and screenshots
2. Review consolidated report recommendations
3. Verify both servers are running
4. Check browser console for errors
5. Review network tab for failed API calls

## License

ISC

---

**Last Updated**: 2025-10-19
**Version**: 2.0.0
**Test Coverage**: 75+ tests across 5 test suites
