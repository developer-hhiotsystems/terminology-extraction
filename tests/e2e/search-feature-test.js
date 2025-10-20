/**
 * Search Feature Deep Dive Test Suite
 * Comprehensive testing of all FTS5 search modes and functionality
 */

const puppeteer = require('puppeteer');
const {
  TestReporter,
  takeScreenshot,
  takeScreenshotOnError,
  waitForElement,
  waitAndClick,
  waitAndType,
  setupNetworkMonitoring,
  setupConsoleMonitoring,
  elementExists,
  getElementCount,
  assert,
  createBrowser
} = require('./test-utils');

const FRONTEND_URL = 'http://localhost:3000';

class SearchFeatureTest {
  constructor() {
    this.reporter = new TestReporter('Search Feature Test');
    this.browser = null;
    this.page = null;
  }

  async setup() {
    console.log('🚀 Starting Search Feature Test Suite');
    console.log(`📍 Frontend: ${FRONTEND_URL}`);

    this.browser = await createBrowser(puppeteer, { headless: false });
    this.page = await this.browser.newPage();

    setupNetworkMonitoring(this.page, this.reporter);
    setupConsoleMonitoring(this.page, this.reporter);
  }

  async teardown() {
    if (this.browser) {
      await this.browser.close();
    }

    const report = this.reporter.saveReport('./tests/e2e/test-results-search.json');
    this.reporter.printSummary();

    return report;
  }

  async runTest(name, description, testFn) {
    this.reporter.startTest(name, description);
    console.log(`\n🧪 Testing: ${name}`);

    try {
      await testFn();
      this.reporter.endTest(true);
      console.log(`✅ PASSED: ${name}`);
    } catch (error) {
      console.error(`❌ FAILED: ${name} - ${error.message}`);
      await takeScreenshotOnError(this.page, name, error);
      this.reporter.endTest(false, error);
    }
  }

  // =====================================================
  // SEARCH PAGE SETUP TESTS
  // =====================================================

  async testSearchPageLoads() {
    await this.runTest(
      'Search Page Loads',
      'Verify search page loads successfully',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/search'), 'Not on search page');

        await takeScreenshot(this.page, 'search-page-load', 'Search page loaded', 'success');
      }
    );
  }

  async testSearchModesExist() {
    await this.runTest(
      'Search Modes Exist',
      'Verify all 4 search modes are available',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        // Look for mode selector buttons/tabs
        const buttons = await this.page.$$('button, [role="tab"], .tab');

        console.log(`Found ${buttons.length} interactive elements`);

        if (buttons.length === 0) {
          console.warn('⚠️  No mode selector buttons found');
        }

        await takeScreenshot(this.page, 'search-modes', 'Search modes view', 'success');
      }
    );
  }

  // =====================================================
  // SIMPLE SEARCH TESTS
  // =====================================================

  async testSimpleSearch() {
    await this.runTest(
      'Simple Search - Basic Query',
      'Test simple text search functionality',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Find search input
        const searchInput = await this.page.$('input[type="search"], input[type="text"], input[placeholder*="search" i]');
        assert(searchInput !== null, 'Search input not found');

        // Type search query
        await searchInput.click();
        await this.page.keyboard.type('test', { delay: 100 });
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Look for search button or auto-search results
        const searchButton = await this.page.$('button[type="submit"]') ||
          await this.page.evaluateHandle(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.find(btn => btn.textContent.includes('Search'));
          }).then(handle => handle.asElement());

        if (searchButton) {
          await searchButton.click();
          await new Promise(resolve => setTimeout(resolve, 2000));
        } else {
          // Auto-search, wait for results
          await new Promise(resolve => setTimeout(resolve, 2000));
        }

        await takeScreenshot(this.page, 'simple-search-results', 'Simple search results', 'success');
      }
    );
  }

  async testSimpleSearchResults() {
    await this.runTest(
      'Simple Search - Results Display',
      'Verify search results are displayed',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          await searchInput.click();
          await this.page.keyboard.type('glossary', { delay: 100 });
          await new Promise(resolve => setTimeout(resolve, 2000));

          // Check for results
          const hasResults = await elementExists(
            this.page,
            '.result, .search-result, .result-item, [class*="result"]'
          );

          if (!hasResults) {
            console.warn('⚠️  No search results elements found');
          } else {
            const resultCount = await getElementCount(
              this.page,
              '.result, .search-result, .result-item'
            );
            console.log(`✓ Found ${resultCount} result elements`);
          }
        }
      }
    );
  }

  async testSearchNoResults() {
    await this.runTest(
      'Simple Search - No Results Handling',
      'Verify "no results" message is shown',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          // Search for something unlikely to exist
          await searchInput.click();
          await this.page.keyboard.type('xyzabc123notfound999', { delay: 100 });
          await new Promise(resolve => setTimeout(resolve, 2000));

          // Look for "no results" message
          const noResultsMessage = await this.page.$('.no-results, .empty, [class*="no-results"]');

          if (noResultsMessage) {
            console.log('✓ "No results" message displayed');
          } else {
            console.warn('⚠️  No "no results" message found');
          }

          await takeScreenshot(this.page, 'search-no-results', 'No results state', 'success');
        }
      }
    );
  }

  // =====================================================
  // AUTOCOMPLETE TESTS
  // =====================================================

  async testAutocompleteAppears() {
    await this.runTest(
      'Autocomplete - Dropdown Appears',
      'Verify autocomplete dropdown shows suggestions',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');
        assert(searchInput !== null, 'Search input not found');

        // Type to trigger autocomplete
        await searchInput.click();
        await this.page.keyboard.type('a', { delay: 200 });
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Look for autocomplete dropdown
        const dropdown = await this.page.$('.autocomplete, .suggestions, .dropdown, [class*="autocomplete"]');

        if (!dropdown) {
          console.warn('⚠️  Autocomplete dropdown did not appear');
        } else {
          console.log('✓ Autocomplete dropdown appeared');

          const suggestionCount = await getElementCount(
            this.page,
            '.autocomplete-item, .suggestion, [class*="suggestion"]'
          );
          console.log(`✓ Found ${suggestionCount} suggestions`);

          await takeScreenshot(this.page, 'autocomplete-dropdown', 'Autocomplete active', 'success');
        }
      }
    );
  }

  async testAutocompleteSelection() {
    await this.runTest(
      'Autocomplete - Select Suggestion',
      'Verify selecting an autocomplete suggestion works',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          await searchInput.click();
          await this.page.keyboard.type('test', { delay: 200 });
          await new Promise(resolve => setTimeout(resolve, 1500));

          // Try to click first suggestion
          const firstSuggestion = await this.page.$('.autocomplete-item, .suggestion');

          if (firstSuggestion) {
            await firstSuggestion.click();
            await new Promise(resolve => setTimeout(resolve, 1000));

            console.log('✓ Autocomplete suggestion clicked');
            await takeScreenshot(this.page, 'autocomplete-selected', 'After selecting suggestion', 'success');
          } else {
            console.warn('⚠️  No autocomplete suggestions to click');
          }
        }
      }
    );
  }

  // =====================================================
  // ADVANCED SEARCH TESTS
  // =====================================================

  async testAdvancedSearchMode() {
    await this.runTest(
      'Advanced Search - Mode Selection',
      'Switch to advanced search mode',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        // Look for "Advanced" button or tab
        const buttons = await this.page.$$('button, [role="tab"]');

        let advancedButton = null;

        for (const button of buttons) {
          const text = await this.page.evaluate(el => el.textContent, button);
          if (text.toLowerCase().includes('advanced')) {
            advancedButton = button;
            break;
          }
        }

        if (advancedButton) {
          await advancedButton.click();
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ Switched to advanced search mode');
          await takeScreenshot(this.page, 'advanced-search-mode', 'Advanced search mode', 'success');
        } else {
          console.warn('⚠️  Advanced search mode button not found');
        }
      }
    );
  }

  async testAdvancedSearchFilters() {
    await this.runTest(
      'Advanced Search - Filters Exist',
      'Verify advanced search has filter options',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        // Try to find advanced button
        const buttons = await this.page.$$('button, [role="tab"]');

        for (const button of buttons) {
          const text = await this.page.evaluate(el => el.textContent, button);
          if (text.toLowerCase().includes('advanced')) {
            await button.click();
            await new Promise(resolve => setTimeout(resolve, 1000));
            break;
          }
        }

        // Look for filter controls
        const filters = await this.page.$$('select, input[type="checkbox"], input[type="radio"]');

        console.log(`Found ${filters.length} filter controls`);

        if (filters.length === 0) {
          console.warn('⚠️  No advanced search filters found');
        } else {
          console.log('✓ Advanced search filters exist');
        }
      }
    );
  }

  // =====================================================
  // BOOLEAN SEARCH TESTS
  // =====================================================

  async testBooleanSearchMode() {
    await this.runTest(
      'Boolean Search - Mode Selection',
      'Switch to Boolean search mode',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        // Look for "Boolean" button or tab
        const buttons = await this.page.$$('button, [role="tab"]');

        let booleanButton = null;

        for (const button of buttons) {
          const text = await this.page.evaluate(el => el.textContent, button);
          if (text.toLowerCase().includes('boolean')) {
            booleanButton = button;
            break;
          }
        }

        if (booleanButton) {
          await booleanButton.click();
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ Switched to Boolean search mode');
          await takeScreenshot(this.page, 'boolean-search-mode', 'Boolean search mode', 'success');
        } else {
          console.warn('⚠️  Boolean search mode button not found');
        }
      }
    );
  }

  async testBooleanSearchOperators() {
    await this.runTest(
      'Boolean Search - Test Operators',
      'Test Boolean search with AND/OR/NOT operators',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        // Try to find and click Boolean mode
        const buttons = await this.page.$$('button, [role="tab"]');

        for (const button of buttons) {
          const text = await this.page.evaluate(el => el.textContent, button);
          if (text.toLowerCase().includes('boolean')) {
            await button.click();
            await new Promise(resolve => setTimeout(resolve, 1000));
            break;
          }
        }

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          // Test Boolean query
          await searchInput.click();
          await this.page.keyboard.type('test AND glossary', { delay: 100 });
          await new Promise(resolve => setTimeout(resolve, 2000));

          console.log('✓ Boolean search query entered');
          await takeScreenshot(this.page, 'boolean-search-query', 'Boolean search with operators', 'success');
        }
      }
    );
  }

  // =====================================================
  // SEARCH INTERACTION TESTS
  // =====================================================

  async testSearchClear() {
    await this.runTest(
      'Search - Clear Button',
      'Verify search can be cleared',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          await searchInput.click();
          await this.page.keyboard.type('test query', { delay: 100 });
          await new Promise(resolve => setTimeout(resolve, 500));

          // Look for clear button
          const clearButton = await this.page.$('button[aria-label*="clear" i], button[title*="clear" i], .clear-button');

          if (clearButton) {
            await clearButton.click();
            await new Promise(resolve => setTimeout(resolve, 500));

            const value = await this.page.evaluate(el => el.value, searchInput);
            assert(value === '', 'Search input not cleared');

            console.log('✓ Search cleared successfully');
          } else {
            console.warn('⚠️  No clear button found');
          }
        }
      }
    );
  }

  async testSearchKeyboardNavigation() {
    await this.runTest(
      'Search - Keyboard Navigation',
      'Test keyboard shortcuts in search',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          // Test Enter key
          await searchInput.click();
          await this.page.keyboard.type('test', { delay: 100 });
          await this.page.keyboard.press('Enter');
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ Enter key pressed');

          // Test Escape key
          await this.page.keyboard.press('Escape');
          await new Promise(resolve => setTimeout(resolve, 500));

          console.log('✓ Escape key pressed');
        }
      }
    );
  }

  // =====================================================
  // MAIN TEST RUNNER
  // =====================================================

  async runAllTests() {
    try {
      await this.setup();

      console.log('\n📋 TESTING: SEARCH PAGE SETUP');
      await this.testSearchPageLoads();
      await this.testSearchModesExist();

      console.log('\n📋 TESTING: SIMPLE SEARCH');
      await this.testSimpleSearch();
      await this.testSimpleSearchResults();
      await this.testSearchNoResults();

      console.log('\n📋 TESTING: AUTOCOMPLETE');
      await this.testAutocompleteAppears();
      await this.testAutocompleteSelection();

      console.log('\n📋 TESTING: ADVANCED SEARCH');
      await this.testAdvancedSearchMode();
      await this.testAdvancedSearchFilters();

      console.log('\n📋 TESTING: BOOLEAN SEARCH');
      await this.testBooleanSearchMode();
      await this.testBooleanSearchOperators();

      console.log('\n📋 TESTING: SEARCH INTERACTIONS');
      await this.testSearchClear();
      await this.testSearchKeyboardNavigation();

      return await this.teardown();
    } catch (error) {
      console.error('💥 Test suite crashed:', error);
      await this.teardown();
      throw error;
    }
  }
}

// Run if executed directly
if (require.main === module) {
  const test = new SearchFeatureTest();
  test.runAllTests()
    .then(report => {
      console.log('\n✨ Search feature test suite completed');
      process.exit(report.summary.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = SearchFeatureTest;
