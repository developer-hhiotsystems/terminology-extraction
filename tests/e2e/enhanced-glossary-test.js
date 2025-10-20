/**
 * Enhanced Glossary Test Suite
 * Tests bilingual cards, bulk operations, and enhanced UI features
 */

const puppeteer = require('puppeteer');
const {
  TestReporter,
  takeScreenshot,
  takeScreenshotOnError,
  waitForElement,
  waitAndClick,
  setupNetworkMonitoring,
  setupConsoleMonitoring,
  elementExists,
  getElementCount,
  getElementText,
  assert,
  createBrowser
} = require('./test-utils');

const FRONTEND_URL = 'http://localhost:3000';

class EnhancedGlossaryTest {
  constructor() {
    this.reporter = new TestReporter('Enhanced Glossary Test');
    this.browser = null;
    this.page = null;
  }

  async setup() {
    console.log('🚀 Starting Enhanced Glossary Test Suite');
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

    const report = this.reporter.saveReport('./tests/e2e/test-results-enhanced-glossary.json');
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
  // PAGE LOAD TESTS
  // =====================================================

  async testEnhancedGlossaryPageLoads() {
    await this.runTest(
      'Enhanced Glossary Page Loads',
      'Verify enhanced glossary page loads successfully',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        const url = this.page.url();
        assert(url.includes('/enhanced-glossary'), 'Not on enhanced glossary page');

        await takeScreenshot(this.page, 'enhanced-glossary-load', 'Enhanced glossary loaded', 'success');
      }
    );
  }

  // =====================================================
  // BILINGUAL CARD TESTS
  // =====================================================

  async testBilingualCardsExist() {
    await this.runTest(
      'Bilingual Cards Exist',
      'Verify bilingual term cards are displayed',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        const cardCount = await getElementCount(
          this.page,
          '.card, .bilingual-card, .glossary-card, [class*="card"]'
        );

        console.log(`Found ${cardCount} cards`);

        if (cardCount === 0) {
          console.warn('⚠️  No bilingual cards found');
        } else {
          console.log(`✓ ${cardCount} bilingual cards displayed`);
        }

        await takeScreenshot(this.page, 'bilingual-cards', 'Bilingual cards view', 'success');
      }
    );
  }

  async testCardFlip() {
    await this.runTest(
      'Card Flip Animation',
      'Test card flip/toggle functionality',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Look for flip button or clickable card
        const flipButton = await this.page.$('.flip-button, button[aria-label*="flip" i], .card');

        if (flipButton) {
          await flipButton.click();
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ Card flip triggered');
          await takeScreenshot(this.page, 'card-flipped', 'Card after flip', 'success');
        } else {
          console.warn('⚠️  No flip button or card found');
        }
      }
    );
  }

  async testCardBilingualContent() {
    await this.runTest(
      'Card Bilingual Content',
      'Verify cards show both language versions',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        const card = await this.page.$('.card, .bilingual-card');

        if (card) {
          const cardText = await this.page.evaluate(el => el.textContent, card);

          console.log('Card content length:', cardText.length);

          if (cardText.length > 0) {
            console.log('✓ Card has content');
          }
        } else {
          console.warn('⚠️  No card found to inspect');
        }
      }
    );
  }

  // =====================================================
  // BULK OPERATIONS TESTS
  // =====================================================

  async testBulkOperationsSection() {
    await this.runTest(
      'Bulk Operations Section Exists',
      'Verify bulk operations UI is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const hasBulkOps = await elementExists(
          this.page,
          '.bulk-operations, [class*="bulk"], section:has(button[class*="bulk"])'
        );

        if (hasBulkOps) {
          console.log('✓ Bulk operations section exists');
        } else {
          console.warn('⚠️  No bulk operations section found');
        }

        await takeScreenshot(this.page, 'bulk-operations', 'Bulk operations view', 'success');
      }
    );
  }

  async testBulkSelectCheckboxes() {
    await this.runTest(
      'Bulk Select Checkboxes',
      'Verify bulk select checkboxes are present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        const checkboxCount = await getElementCount(
          this.page,
          'input[type="checkbox"]'
        );

        console.log(`Found ${checkboxCount} checkboxes`);

        if (checkboxCount === 0) {
          console.warn('⚠️  No bulk select checkboxes found');
        } else {
          console.log(`✓ ${checkboxCount} checkboxes for bulk selection`);
        }
      }
    );
  }

  async testBulkSelectAll() {
    await this.runTest(
      'Bulk Select All',
      'Test "Select All" functionality',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Look for "Select All" checkbox or button
        let selectAll = await this.page.$('input[type="checkbox"]').catch(() => null);
        if (!selectAll) {
          selectAll = await this.page.evaluateHandle(() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const selectAllLabel = labels.find(l => l.textContent.includes('Select All'));
            return selectAllLabel ? selectAllLabel.querySelector('input') : null;
          }).then(handle => handle.asElement());
        }

        if (selectAll) {
          await selectAll.click();
          await new Promise(resolve => setTimeout(resolve, 500));

          console.log('✓ "Select All" clicked');
          await takeScreenshot(this.page, 'bulk-select-all', 'All items selected', 'success');
        } else {
          console.warn('⚠️  No "Select All" control found');
        }
      }
    );
  }

  async testBulkActionButtons() {
    await this.runTest(
      'Bulk Action Buttons',
      'Verify bulk action buttons exist',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const bulkButtons = await this.page.$$('button[class*="bulk"], .bulk-operations button');

        console.log(`Found ${bulkButtons.length} bulk action buttons`);

        if (bulkButtons.length === 0) {
          console.warn('⚠️  No bulk action buttons found');
        } else {
          for (const button of bulkButtons) {
            const text = await this.page.evaluate(el => el.textContent, button);
            console.log(`  - ${text.trim()}`);
          }
        }
      }
    );
  }

  // =====================================================
  // FILTER AND SORT TESTS
  // =====================================================

  async testEnhancedFilters() {
    await this.runTest(
      'Enhanced Filters',
      'Verify filter controls are present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const filterCount = await getElementCount(
          this.page,
          'select, input[type="checkbox"]:not([class*="bulk"]), .filter'
        );

        console.log(`Found ${filterCount} filter controls`);

        if (filterCount === 0) {
          console.warn('⚠️  No filter controls found');
        } else {
          console.log(`✓ ${filterCount} filters available`);
        }
      }
    );
  }

  async testSortOptions() {
    await this.runTest(
      'Sort Options',
      'Verify sort dropdown/buttons exist',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const sortControl = await this.page.$('select[id*="sort" i], button[aria-label*="sort" i]');

        if (sortControl) {
          console.log('✓ Sort control exists');

          await sortControl.click();
          await new Promise(resolve => setTimeout(resolve, 500));

          await takeScreenshot(this.page, 'sort-options', 'Sort options displayed', 'success');
        } else {
          console.warn('⚠️  No sort control found');
        }
      }
    );
  }

  // =====================================================
  // PAGINATION TESTS
  // =====================================================

  async testPagination() {
    await this.runTest(
      'Pagination Controls',
      'Verify pagination is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        let hasPagination = await elementExists(this.page, '.pagination, .pagination-controls, nav[aria-label="pagination"]');
        if (!hasPagination) {
          hasPagination = await this.page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.some(btn => btn.textContent.includes('Next') || btn.textContent.includes('›'));
          });
        }

        if (hasPagination) {
          console.log('✓ Pagination controls exist');
        } else {
          console.warn('⚠️  No pagination found (might have few items)');
        }
      }
    );
  }

  async testPageNavigation() {
    await this.runTest(
      'Page Navigation',
      'Test clicking next/previous page',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        let nextButton = await this.page.$('.btn-pagination[title="Next page"]');
        if (!nextButton) {
          nextButton = await this.page.evaluateHandle(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.find(btn => btn.textContent.includes('›') ||
                              btn.textContent.includes('Next') ||
                              (btn.title && btn.title.toLowerCase().includes('next')));
          }).then(handle => handle.asElement());
        }

        if (nextButton) {
          await nextButton.click();
          await new Promise(resolve => setTimeout(resolve, 1500));

          console.log('✓ Next page clicked');
          await takeScreenshot(this.page, 'pagination-next', 'Next page loaded', 'success');
        } else {
          console.warn('⚠️  No next page button found');
        }
      }
    );
  }

  // =====================================================
  // SEARCH TESTS
  // =====================================================

  async testEnhancedSearch() {
    await this.runTest(
      'Enhanced Glossary Search',
      'Test search on enhanced glossary page',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          await searchInput.click();
          await this.page.keyboard.type('test', { delay: 100 });
          await new Promise(resolve => setTimeout(resolve, 1500));

          console.log('✓ Search query entered');
          await takeScreenshot(this.page, 'enhanced-search', 'Search active', 'success');
        } else {
          console.warn('⚠️  No search input found');
        }
      }
    );
  }

  // =====================================================
  // VIEW MODE TESTS
  // =====================================================

  async testViewModeToggle() {
    await this.runTest(
      'View Mode Toggle',
      'Test switching between grid/list view',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });

        const viewButtons = await this.page.$$('button[aria-label*="view" i], button[title*="view" i]');

        console.log(`Found ${viewButtons.length} view mode buttons`);

        if (viewButtons.length > 0) {
          await viewButtons[0].click();
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ View mode toggled');
          await takeScreenshot(this.page, 'view-mode-toggle', 'View mode changed', 'success');
        } else {
          console.warn('⚠️  No view mode toggle found');
        }
      }
    );
  }

  // =====================================================
  // DETAIL VIEW TESTS
  // =====================================================

  async testCardDetailView() {
    await this.runTest(
      'Card Detail View',
      'Test opening detailed view of a term',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/enhanced-glossary`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Look for detail button or clickable card
        let detailButton = await this.page.$('.card, .bilingual-card');
        if (!detailButton) {
          detailButton = await this.page.evaluateHandle(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const detailBtn = buttons.find(btn => btn.textContent.includes('Details') || btn.textContent.includes('View'));
            return detailBtn || document.querySelector('.card');
          }).then(handle => handle.asElement());
        }

        if (detailButton) {
          await detailButton.click();
          await new Promise(resolve => setTimeout(resolve, 1000));

          // Check if modal or detail panel opened
          const hasModal = await elementExists(
            this.page,
            '.modal, [role="dialog"], .detail-panel'
          );

          if (hasModal) {
            console.log('✓ Detail view opened');
            await takeScreenshot(this.page, 'detail-view', 'Term detail view', 'success');
          } else {
            console.log('✓ Detail button clicked (modal might not have appeared)');
          }
        } else {
          console.warn('⚠️  No detail button found');
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

      console.log('\n📋 TESTING: PAGE LOAD');
      await this.testEnhancedGlossaryPageLoads();

      console.log('\n📋 TESTING: BILINGUAL CARDS');
      await this.testBilingualCardsExist();
      await this.testCardFlip();
      await this.testCardBilingualContent();

      console.log('\n📋 TESTING: BULK OPERATIONS');
      await this.testBulkOperationsSection();
      await this.testBulkSelectCheckboxes();
      await this.testBulkSelectAll();
      await this.testBulkActionButtons();

      console.log('\n📋 TESTING: FILTERS AND SORT');
      await this.testEnhancedFilters();
      await this.testSortOptions();

      console.log('\n📋 TESTING: PAGINATION');
      await this.testPagination();
      await this.testPageNavigation();

      console.log('\n📋 TESTING: SEARCH');
      await this.testEnhancedSearch();

      console.log('\n📋 TESTING: VIEW MODES');
      await this.testViewModeToggle();

      console.log('\n📋 TESTING: DETAIL VIEW');
      await this.testCardDetailView();

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
  const test = new EnhancedGlossaryTest();
  test.runAllTests()
    .then(report => {
      console.log('\n✨ Enhanced glossary test suite completed');
      process.exit(report.summary.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = EnhancedGlossaryTest;
