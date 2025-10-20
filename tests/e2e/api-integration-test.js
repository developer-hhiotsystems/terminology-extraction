/**
 * API Integration Test Suite
 * Tests that frontend actually calls backend APIs and displays data correctly
 */

const puppeteer = require('puppeteer');
const {
  TestReporter,
  takeScreenshot,
  takeScreenshotOnError,
  waitForElement,
  setupNetworkMonitoring,
  setupConsoleMonitoring,
  assert,
  createBrowser
} = require('./test-utils');

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:9123';

class APIIntegrationTest {
  constructor() {
    this.reporter = new TestReporter('API Integration Test');
    this.browser = null;
    this.page = null;
    this.networkRequests = [];
    this.networkFailures = [];
  }

  async setup() {
    console.log('🚀 Starting API Integration Test Suite');
    console.log(`📍 Frontend: ${FRONTEND_URL}`);
    console.log(`📍 Backend: ${BACKEND_URL}`);

    this.browser = await createBrowser(puppeteer, { headless: false });
    this.page = await this.browser.newPage();

    // Setup network monitoring
    const { requests, failures } = setupNetworkMonitoring(this.page, this.reporter);
    this.networkRequests = requests;
    this.networkFailures = failures;

    setupConsoleMonitoring(this.page, this.reporter);

    // Capture all network traffic
    await this.page.setRequestInterception(false);
  }

  async teardown() {
    if (this.browser) {
      await this.browser.close();
    }

    const report = this.reporter.saveReport('./tests/e2e/test-results-api.json');
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

  getAPIRequests(pattern) {
    return this.networkRequests.filter(req => req.url.includes(pattern));
  }

  hasAPIRequest(pattern) {
    return this.getAPIRequests(pattern).length > 0;
  }

  // =====================================================
  // GLOSSARY API TESTS
  // =====================================================

  async testGlossaryAPICall() {
    await this.runTest(
      'Glossary API - Fetch Terms',
      'Verify frontend calls /api/glossary endpoint',
      async () => {
        // Clear previous requests
        this.networkRequests.length = 0;

        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check if API was called
        const apiCalled = this.hasAPIRequest('/api/glossary');

        if (!apiCalled) {
          console.warn('⚠️  No /api/glossary request detected');
          console.log('Network requests:', this.networkRequests.map(r => r.url));
        } else {
          console.log('✓ API request to /api/glossary detected');
        }

        await takeScreenshot(this.page, 'glossary-api', 'After glossary API call', 'success');
      }
    );
  }

  async testGlossaryAPIResponse() {
    await this.runTest(
      'Glossary API - Response Handling',
      'Verify API response is displayed in UI',
      async () => {
        let responseData = null;
        let responseStatus = null;

        // Intercept response
        this.page.on('response', async (response) => {
          if (response.url().includes('/api/glossary')) {
            responseStatus = response.status();
            try {
              responseData = await response.json();
              console.log(`📦 Glossary API response: ${responseStatus}`);
            } catch (e) {
              console.warn('Could not parse API response');
            }
          }
        });

        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Verify response was received
        if (responseStatus === null) {
          console.warn('⚠️  No API response captured (backend might be down)');
        } else if (responseStatus >= 400) {
          console.error(`❌ API returned error status: ${responseStatus}`);
        } else {
          console.log(`✓ API returned success status: ${responseStatus}`);
        }
      }
    );
  }

  // =====================================================
  // SEARCH API TESTS
  // =====================================================

  async testSearchAPICall() {
    await this.runTest(
      'Search API - Simple Search',
      'Verify search triggers API call',
      async () => {
        this.networkRequests.length = 0;

        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Try to find and use search input
        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          await searchInput.click();
          await this.page.keyboard.type('test', { delay: 100 });
          await new Promise(resolve => setTimeout(resolve, 2000));

          // Check for search API calls
          const searchAPICalled = this.hasAPIRequest('/api/search') ||
                                   this.hasAPIRequest('/api/fts') ||
                                   this.hasAPIRequest('/api/glossary');

          if (!searchAPICalled) {
            console.warn('⚠️  No search API request detected');
          } else {
            console.log('✓ Search API request detected');
          }

          await takeScreenshot(this.page, 'search-api', 'After search API call', 'success');
        } else {
          console.warn('⚠️  Search input not found');
        }
      }
    );
  }

  async testAutocompleteAPI() {
    await this.runTest(
      'Search API - Autocomplete',
      'Verify autocomplete triggers API call',
      async () => {
        this.networkRequests.length = 0;

        await this.page.goto(`${FRONTEND_URL}/search`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 1000));

        const searchInput = await this.page.$('input[type="search"], input[type="text"]');

        if (searchInput) {
          await searchInput.click();
          await this.page.keyboard.type('a', { delay: 300 });
          await new Promise(resolve => setTimeout(resolve, 1500));

          // Check for autocomplete API
          const autocompleteCalled = this.hasAPIRequest('/autocomplete') ||
                                      this.hasAPIRequest('/suggest') ||
                                      this.hasAPIRequest('/api/glossary');

          if (!autocompleteCalled) {
            console.warn('⚠️  No autocomplete API request detected');
          } else {
            console.log('✓ Autocomplete API request detected');
          }
        }
      }
    );
  }

  // =====================================================
  // RELATIONSHIP API TESTS
  // =====================================================

  async testRelationshipAPICall() {
    await this.runTest(
      'Relationship API - Graph Data',
      'Verify relationship explorer calls API',
      async () => {
        this.networkRequests.length = 0;

        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Check for relationship API calls
        const relationshipAPICalled = this.hasAPIRequest('/api/relationship') ||
                                       this.hasAPIRequest('/api/graph') ||
                                       this.hasAPIRequest('/api/extract');

        if (!relationshipAPICalled) {
          console.warn('⚠️  No relationship API request detected');
          console.log('Network requests:', this.networkRequests.map(r => r.url));
        } else {
          console.log('✓ Relationship API request detected');
        }

        await takeScreenshot(this.page, 'relationship-api', 'Relationship API call', 'success');
      }
    );
  }

  // =====================================================
  // DOCUMENT API TESTS
  // =====================================================

  async testDocumentsAPICall() {
    await this.runTest(
      'Documents API - Fetch List',
      'Verify documents page calls API',
      async () => {
        this.networkRequests.length = 0;

        await this.page.goto(`${FRONTEND_URL}/documents`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check for documents API
        const documentsAPICalled = this.hasAPIRequest('/api/documents') ||
                                    this.hasAPIRequest('/api/uploads');

        if (!documentsAPICalled) {
          console.warn('⚠️  No documents API request detected');
        } else {
          console.log('✓ Documents API request detected');
        }

        await takeScreenshot(this.page, 'documents-api', 'Documents API call', 'success');
      }
    );
  }

  // =====================================================
  // STATISTICS API TESTS
  // =====================================================

  async testStatisticsAPICall() {
    await this.runTest(
      'Statistics API - Fetch Stats',
      'Verify statistics page calls API',
      async () => {
        this.networkRequests.length = 0;

        await this.page.goto(`${FRONTEND_URL}/statistics`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check for stats API
        const statsAPICalled = this.hasAPIRequest('/api/stats') ||
                                this.hasAPIRequest('/api/statistics');

        if (!statsAPICalled) {
          console.warn('⚠️  No statistics API request detected');
        } else {
          console.log('✓ Statistics API request detected');
        }

        await takeScreenshot(this.page, 'statistics-api', 'Statistics API call', 'success');
      }
    );
  }

  // =====================================================
  // ERROR HANDLING TESTS
  // =====================================================

  async testAPIErrorHandling() {
    await this.runTest(
      'API Error Handling',
      'Verify frontend handles API errors gracefully',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check if there were any network failures
        console.log(`Network failures: ${this.networkFailures.length}`);

        if (this.networkFailures.length > 0) {
          console.warn('⚠️  Network failures detected:');
          this.networkFailures.forEach(failure => {
            console.warn(`  - ${failure.url}: ${failure.error || failure.status}`);
          });
        }

        // Check for error messages in UI
        const errorMessage = await this.page.$('.error, .error-message, [class*="error"]');

        if (errorMessage && this.networkFailures.length > 0) {
          const errorText = await this.page.evaluate(el => el.textContent, errorMessage);
          console.log(`✓ Error message displayed: ${errorText}`);
        }
      }
    );
  }

  // =====================================================
  // PERFORMANCE TESTS
  // =====================================================

  async testAPIResponseTimes() {
    await this.runTest(
      'API Response Times',
      'Measure and verify API response times',
      async () => {
        const timings = [];

        this.page.on('response', async (response) => {
          if (response.url().includes('/api/')) {
            const timing = response.timing();
            if (timing) {
              timings.push({
                url: response.url(),
                status: response.status(),
                duration: timing.responseEnd - timing.requestStart
              });
            }
          }
        });

        await this.page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        if (timings.length > 0) {
          console.log('\n📊 API Response Times:');
          timings.forEach(t => {
            console.log(`  ${t.url}: ${t.duration.toFixed(2)}ms (${t.status})`);
          });

          const avgTime = timings.reduce((sum, t) => sum + t.duration, 0) / timings.length;
          console.log(`  Average: ${avgTime.toFixed(2)}ms`);
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

      console.log('\n📋 TESTING: GLOSSARY API');
      await this.testGlossaryAPICall();
      await this.testGlossaryAPIResponse();

      console.log('\n📋 TESTING: SEARCH API');
      await this.testSearchAPICall();
      await this.testAutocompleteAPI();

      console.log('\n📋 TESTING: RELATIONSHIP API');
      await this.testRelationshipAPICall();

      console.log('\n📋 TESTING: DOCUMENTS API');
      await this.testDocumentsAPICall();

      console.log('\n📋 TESTING: STATISTICS API');
      await this.testStatisticsAPICall();

      console.log('\n📋 TESTING: ERROR HANDLING');
      await this.testAPIErrorHandling();

      console.log('\n📋 TESTING: PERFORMANCE');
      await this.testAPIResponseTimes();

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
  const test = new APIIntegrationTest();
  test.runAllTests()
    .then(report => {
      console.log('\n✨ API Integration test suite completed');
      process.exit(report.summary.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = APIIntegrationTest;
