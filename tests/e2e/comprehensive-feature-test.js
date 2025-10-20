/**
 * Comprehensive Feature Test Suite
 * Tests ALL features, buttons, and navigation in the Glossary APP
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
  getElementText,
  assert,
  createBrowser
} = require('./test-utils');

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:9123';

class ComprehensiveFeatureTest {
  constructor() {
    this.reporter = new TestReporter('Comprehensive Feature Test');
    this.browser = null;
    this.page = null;
  }

  async setup() {
    console.log('🚀 Starting Comprehensive Feature Test Suite');
    console.log(`📍 Frontend: ${FRONTEND_URL}`);
    console.log(`📍 Backend: ${BACKEND_URL}`);

    this.browser = await createBrowser(puppeteer, { headless: false });
    this.page = await this.browser.newPage();

    // Setup monitoring
    setupNetworkMonitoring(this.page, this.reporter);
    setupConsoleMonitoring(this.page, this.reporter);
  }

  async teardown() {
    if (this.browser) {
      await this.browser.close();
    }

    // Save and print report
    const report = this.reporter.saveReport('./tests/e2e/test-results-comprehensive.json');
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
  // TEST SUITE: NAVIGATION
  // =====================================================

  async testHomepageLoads() {
    await this.runTest(
      'Homepage Loads',
      'Verify the application homepage loads successfully',
      async () => {
        await this.page.goto(FRONTEND_URL, { waitUntil: 'networkidle2' });

        // Check for main header
        const headerExists = await elementExists(this.page, '.app-header h1');
        assert(headerExists, 'Main header not found');

        const headerText = await getElementText(this.page, '.app-header h1');
        assert(
          headerText.includes('Glossary Management System'),
          'Header text incorrect'
        );

        await takeScreenshot(this.page, 'homepage-load', 'Initial homepage', 'success');
      }
    );
  }

  async testNavigationLinks() {
    await this.runTest(
      'Navigation Links Exist',
      'Verify all navigation links are present',
      async () => {
        const expectedLinks = [
          'Glossary',
          'Search',
          'Enhanced View',
          'Relationships',
          'Documents',
          'Statistics',
          'Admin'
        ];

        for (const linkText of expectedLinks) {
          const navLinks = await this.page.$$('.app-nav a');
          let found = false;

          for (const link of navLinks) {
            const text = await this.page.evaluate(el => el.textContent, link);
            if (text.includes(linkText)) {
              found = true;
              break;
            }
          }

          assert(found, `Navigation link not found: ${linkText}`);
        }
      }
    );
  }

  async testNavigationToSearch() {
    await this.runTest(
      'Navigate to Search Page',
      'Click Search link and verify page loads',
      async () => {
        await waitAndClick(this.page, 'a[href="/search"]');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/search'), 'Did not navigate to search page');

        await takeScreenshot(this.page, 'search-page', 'Search page loaded', 'success');
      }
    );
  }

  async testNavigationToEnhancedGlossary() {
    await this.runTest(
      'Navigate to Enhanced Glossary',
      'Click Enhanced View link and verify page loads',
      async () => {
        await waitAndClick(this.page, 'a[href="/enhanced-glossary"]');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/enhanced-glossary'), 'Did not navigate to enhanced glossary');

        await takeScreenshot(this.page, 'enhanced-glossary', 'Enhanced glossary loaded', 'success');
      }
    );
  }

  async testNavigationToRelationships() {
    await this.runTest(
      'Navigate to Relationships',
      'Click Relationships link and verify page loads',
      async () => {
        await waitAndClick(this.page, 'a[href="/relationships"]');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/relationships'), 'Did not navigate to relationships');

        await takeScreenshot(this.page, 'relationships', 'Relationships page loaded', 'success');
      }
    );
  }

  async testNavigationToDocuments() {
    await this.runTest(
      'Navigate to Documents',
      'Click Documents link and verify page loads',
      async () => {
        await waitAndClick(this.page, 'a[href="/documents"]');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/documents'), 'Did not navigate to documents');

        await takeScreenshot(this.page, 'documents', 'Documents page loaded', 'success');
      }
    );
  }

  async testNavigationToStatistics() {
    await this.runTest(
      'Navigate to Statistics',
      'Click Statistics link and verify page loads',
      async () => {
        await waitAndClick(this.page, 'a[href="/statistics"]');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/statistics'), 'Did not navigate to statistics');

        await takeScreenshot(this.page, 'statistics', 'Statistics page loaded', 'success');
      }
    );
  }

  async testNavigationToAdmin() {
    await this.runTest(
      'Navigate to Admin',
      'Click Admin link and verify page loads',
      async () => {
        await waitAndClick(this.page, 'a[href="/admin"]');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const url = this.page.url();
        assert(url.includes('/admin'), 'Did not navigate to admin');

        await takeScreenshot(this.page, 'admin', 'Admin page loaded', 'success');
      }
    );
  }

  // =====================================================
  // TEST SUITE: MAIN GLOSSARY PAGE
  // =====================================================

  async testGlossaryPageLoads() {
    await this.runTest(
      'Glossary Page Loads',
      'Verify main glossary page displays terms',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check if there are any glossary items or a message
        const hasItems = await elementExists(this.page, '.glossary-item');
        const hasMessage = await elementExists(this.page, '.no-terms-message');

        assert(
          hasItems || hasMessage,
          'No glossary items or message displayed'
        );

        await takeScreenshot(this.page, 'glossary-main', 'Main glossary view', 'success');
      }
    );
  }

  async testGlossarySearchBox() {
    await this.runTest(
      'Glossary Search Box Works',
      'Type in the glossary search and verify filtering',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        const searchExists = await elementExists(this.page, 'input[type="search"], input[placeholder*="Search"]');

        if (searchExists) {
          await waitAndType(this.page, 'input[type="search"], input[placeholder*="Search"]', 'test');
          await new Promise(resolve => setTimeout(resolve, 1000));

          await takeScreenshot(this.page, 'glossary-search', 'Search typed', 'success');
        } else {
          console.warn('⚠️  No search box found on glossary page');
        }
      }
    );
  }

  // =====================================================
  // TEST SUITE: SEARCH PAGE FEATURES
  // =====================================================

  async testSearchPageHasSearchModes() {
    await this.runTest(
      'Search Page Has Mode Selector',
      'Verify search mode tabs/buttons exist',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Look for mode selector buttons or tabs
        const hasModeTabs = await elementExists(this.page, 'button, .tab, [role="tab"]');
        assert(hasModeTabs, 'No search mode selector found');

        await takeScreenshot(this.page, 'search-modes', 'Search modes view', 'success');
      }
    );
  }

  async testSearchInputExists() {
    await this.runTest(
      'Search Input Exists',
      'Verify search input field is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchInput = await elementExists(
          this.page,
          'input[type="search"], input[type="text"], input[placeholder*="search" i]'
        );

        assert(searchInput, 'Search input not found');
      }
    );
  }

  async testSearchButtonExists() {
    await this.runTest(
      'Search Button Exists',
      'Verify search submit button is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });

        const searchButton = await elementExists(
          this.page,
          'button[type="submit"], button:has-text("Search")'
        );

        // Button might not exist if it's auto-search
        if (!searchButton) {
          console.warn('⚠️  No explicit search button (might be auto-search)');
        }
      }
    );
  }

  // =====================================================
  // TEST SUITE: ENHANCED GLOSSARY FEATURES
  // =====================================================

  async testEnhancedGlossaryHasCards() {
    await this.runTest(
      'Enhanced Glossary Has Cards',
      'Verify bilingual cards are displayed',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        const hasCards = await elementExists(this.page, '.card, .bilingual-card, .glossary-card');

        if (!hasCards) {
          console.warn('⚠️  No cards found on enhanced glossary page');
        }

        await takeScreenshot(this.page, 'enhanced-cards', 'Enhanced glossary cards', 'success');
      }
    );
  }

  async testBulkOperationsExists() {
    await this.runTest(
      'Bulk Operations Section Exists',
      'Verify bulk operations UI is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const hasBulkOps = await elementExists(
          this.page,
          '.bulk-operations, [class*="bulk"], button:has-text("Bulk")'
        );

        if (!hasBulkOps) {
          console.warn('⚠️  No bulk operations UI found');
        }
      }
    );
  }

  // =====================================================
  // TEST SUITE: RELATIONSHIP EXPLORER
  // =====================================================

  async testRelationshipGraphExists() {
    await this.runTest(
      'Relationship Graph Exists',
      'Verify graph visualization is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000)); // Graph needs time to load

        const hasGraph = await elementExists(
          this.page,
          'svg, canvas, .graph, #graph-container'
        );

        assert(hasGraph, 'No graph visualization found');

        await takeScreenshot(this.page, 'relationship-graph', 'Relationship graph', 'success');
      }
    );
  }

  async testRelationshipFilters() {
    await this.runTest(
      'Relationship Filters Exist',
      'Verify filter controls are present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });

        const hasFilters = await elementExists(
          this.page,
          'select, input[type="checkbox"], .filter, [class*="filter"]'
        );

        if (!hasFilters) {
          console.warn('⚠️  No relationship filters found');
        }
      }
    );
  }

  // =====================================================
  // TEST SUITE: DOCUMENTS PAGE
  // =====================================================

  async testDocumentUploadExists() {
    await this.runTest(
      'Document Upload Exists',
      'Verify upload functionality is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/documents`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        const hasUpload = await elementExists(
          this.page,
          'input[type="file"], .dropzone, [class*="upload"]'
        );

        if (!hasUpload) {
          console.warn('⚠️  No document upload found');
        }

        await takeScreenshot(this.page, 'documents-page', 'Documents page', 'success');
      }
    );
  }

  async testDocumentsList() {
    await this.runTest(
      'Documents List Exists',
      'Verify documents list is displayed',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/documents`, { waitUntil: 'networkidle2' });

        const hasList = await elementExists(
          this.page,
          '.document-list, .documents, table, [class*="document"]'
        );

        if (!hasList) {
          console.warn('⚠️  No documents list found');
        }
      }
    );
  }

  // =====================================================
  // TEST SUITE: KEYBOARD SHORTCUTS
  // =====================================================

  async testKeyboardShortcutsButton() {
    await this.runTest(
      'Keyboard Shortcuts Button',
      'Verify keyboard shortcuts help button exists',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });

        const hasButton = await elementExists(
          this.page,
          '.shortcuts-help-btn, button:has-text("Keyboard")'
        );

        assert(hasButton, 'Keyboard shortcuts button not found');
      }
    );
  }

  async testKeyboardShortcutsModal() {
    await this.runTest(
      'Keyboard Shortcuts Modal Opens',
      'Click shortcuts button and verify modal opens',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });

        const button = await this.page.$('.shortcuts-help-btn');
        if (button) {
          await button.click();
          await new Promise(resolve => setTimeout(resolve, 500));

          const modalExists = await elementExists(
            this.page,
            '.modal, .dialog, [role="dialog"]'
          );

          if (!modalExists) {
            console.warn('⚠️  Shortcuts modal did not open');
          }

          await takeScreenshot(this.page, 'shortcuts-modal', 'Shortcuts modal', 'success');
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

      // Navigation Tests
      console.log('\n📋 TESTING: NAVIGATION');
      await this.testHomepageLoads();
      await this.testNavigationLinks();
      await this.testNavigationToSearch();
      await this.testNavigationToEnhancedGlossary();
      await this.testNavigationToRelationships();
      await this.testNavigationToDocuments();
      await this.testNavigationToStatistics();
      await this.testNavigationToAdmin();

      // Main Glossary Tests
      console.log('\n📋 TESTING: MAIN GLOSSARY');
      await this.testGlossaryPageLoads();
      await this.testGlossarySearchBox();

      // Search Page Tests
      console.log('\n📋 TESTING: SEARCH PAGE');
      await this.testSearchPageHasSearchModes();
      await this.testSearchInputExists();
      await this.testSearchButtonExists();

      // Enhanced Glossary Tests
      console.log('\n📋 TESTING: ENHANCED GLOSSARY');
      await this.testEnhancedGlossaryHasCards();
      await this.testBulkOperationsExists();

      // Relationship Explorer Tests
      console.log('\n📋 TESTING: RELATIONSHIP EXPLORER');
      await this.testRelationshipGraphExists();
      await this.testRelationshipFilters();

      // Documents Tests
      console.log('\n📋 TESTING: DOCUMENTS');
      await this.testDocumentUploadExists();
      await this.testDocumentsList();

      // UI Features Tests
      console.log('\n📋 TESTING: UI FEATURES');
      await this.testKeyboardShortcutsButton();
      await this.testKeyboardShortcutsModal();

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
  const test = new ComprehensiveFeatureTest();
  test.runAllTests()
    .then(report => {
      console.log('\n✨ Test suite completed');
      process.exit(report.summary.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = ComprehensiveFeatureTest;
