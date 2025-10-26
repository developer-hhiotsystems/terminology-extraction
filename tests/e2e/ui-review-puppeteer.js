/**
 * Comprehensive Frontend UI Review with Puppeteer
 * Captures errors, screenshots, and analyzes UI issues
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Configuration
const BASE_URL = 'http://localhost:3000';
const SCREENSHOT_DIR = './test-screenshots/ui-review';
const REPORT_FILE = './ui-review-report.json';

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

class UIReviewer {
  constructor() {
    this.browser = null;
    this.page = null;
    this.errors = [];
    this.warnings = [];
    this.consoleMessages = [];
    this.networkErrors = [];
    this.screenshots = [];
  }

  async initialize() {
    console.log('🚀 Launching browser...');
    this.browser = await puppeteer.launch({
      headless: false, // Show browser for debugging
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: {
        width: 1920,
        height: 1080
      }
    });

    this.page = await this.browser.newPage();

    // Capture console messages
    this.page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();

      this.consoleMessages.push({
        type,
        text,
        timestamp: new Date().toISOString()
      });

      if (type === 'error') {
        this.errors.push({ source: 'console', message: text });
        console.error('❌ Console Error:', text);
      } else if (type === 'warning') {
        this.warnings.push({ source: 'console', message: text });
        console.warn('⚠️  Console Warning:', text);
      }
    });

    // Capture page errors
    this.page.on('pageerror', error => {
      this.errors.push({
        source: 'page',
        message: error.message,
        stack: error.stack
      });
      console.error('❌ Page Error:', error.message);
    });

    // Capture network failures
    this.page.on('requestfailed', request => {
      this.networkErrors.push({
        url: request.url(),
        failure: request.failure().errorText
      });
      console.error('❌ Network Error:', request.url(), request.failure().errorText);
    });

    // Capture response errors
    this.page.on('response', response => {
      if (response.status() >= 400) {
        this.networkErrors.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
        console.error(`❌ HTTP ${response.status()}:`, response.url());
      }
    });
  }

  async takeScreenshot(name, description) {
    const filename = `${name}-${Date.now()}.png`;
    const filepath = path.join(SCREENSHOT_DIR, filename);

    await this.page.screenshot({
      path: filepath,
      fullPage: true
    });

    this.screenshots.push({ name, description, filepath });
    console.log(`📸 Screenshot saved: ${filename}`);
  }

  async testHomePage() {
    console.log('\n📋 Test 1: Loading Homepage...');

    try {
      await this.page.goto(BASE_URL, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      await this.takeScreenshot('01-homepage', 'Initial homepage load');

      // Check for basic elements
      const title = await this.page.title();
      console.log('✓ Page Title:', title);

      // Check if main content loaded
      const bodyText = await this.page.evaluate(() => document.body.innerText);
      console.log('✓ Page has content:', bodyText.length > 0);

    } catch (error) {
      this.errors.push({ source: 'test', test: 'homepage', message: error.message });
      console.error('❌ Homepage load failed:', error.message);
    }
  }

  async testNavigation() {
    console.log('\n📋 Test 2: Testing Navigation...');

    try {
      // Look for navigation tabs
      const navTabs = await this.page.$$('nav a, .nav-link, [role="tab"], button');
      console.log(`✓ Found ${navTabs.length} navigation elements`);

      // Take screenshot of navigation
      await this.takeScreenshot('02-navigation', 'Navigation elements');

      // Try to find specific tabs
      const tabNames = ['Glossary', 'Documents', 'Statistics', 'Admin', 'Home'];

      for (const tabName of tabNames) {
        const tabExists = await this.page.evaluate((name) => {
          const text = document.body.innerText.toLowerCase();
          return text.includes(name.toLowerCase());
        }, tabName);

        if (tabExists) {
          console.log(`✓ Found ${tabName} tab/link`);
        } else {
          console.warn(`⚠️  Missing ${tabName} tab/link`);
        }
      }

    } catch (error) {
      this.errors.push({ source: 'test', test: 'navigation', message: error.message });
      console.error('❌ Navigation test failed:', error.message);
    }
  }

  async testGlossaryPage() {
    console.log('\n📋 Test 3: Testing Glossary Page...');

    try {
      // Try to navigate to glossary
      const glossaryLink = await this.page.$('a[href*="glossary"], button:has-text("Glossary")');

      if (glossaryLink) {
        await glossaryLink.click();
        await new Promise(resolve => setTimeout(resolve, 2000));
        await this.takeScreenshot('03-glossary-page', 'Glossary page view');
        console.log('✓ Navigated to Glossary page');
      } else {
        // Try direct URL
        await this.page.goto(`${BASE_URL}/glossary`, { waitUntil: 'networkidle2' });
        await this.takeScreenshot('03-glossary-direct', 'Glossary page (direct URL)');
        console.log('✓ Loaded Glossary via direct URL');
      }

      // Check for glossary entries
      const hasEntries = await this.page.evaluate(() => {
        const text = document.body.innerText;
        return text.length > 100; // Assume content if text is substantial
      });

      if (hasEntries) {
        console.log('✓ Glossary page has content');
      } else {
        console.warn('⚠️  Glossary page appears empty');
      }

    } catch (error) {
      this.errors.push({ source: 'test', test: 'glossary', message: error.message });
      console.error('❌ Glossary test failed:', error.message);
    }
  }

  async testSearchFeature() {
    console.log('\n📋 Test 4: Testing Search Feature...');

    try {
      // Look for search input
      const searchInput = await this.page.$('input[type="search"], input[placeholder*="search" i], input[name*="search" i]');

      if (searchInput) {
        console.log('✓ Found search input');

        // Try typing in search
        await searchInput.type('bio', { delay: 100 });
        await new Promise(resolve => setTimeout(resolve, 1000));

        await this.takeScreenshot('04-search-test', 'Search with "bio" query');
        console.log('✓ Typed search query');

        // Check for autocomplete/results
        const hasResults = await this.page.evaluate(() => {
          const text = document.body.innerText;
          return text.includes('result') || text.includes('found') || text.includes('match');
        });

        if (hasResults) {
          console.log('✓ Search results appeared');
        } else {
          console.warn('⚠️  No search results visible');
        }
      } else {
        console.warn('⚠️  Search input not found');
      }

    } catch (error) {
      this.errors.push({ source: 'test', test: 'search', message: error.message });
      console.error('❌ Search test failed:', error.message);
    }
  }

  async testAPIConnectivity() {
    console.log('\n📋 Test 5: Testing API Connectivity...');

    try {
      // Monitor API requests
      const apiRequests = [];

      this.page.on('request', request => {
        const url = request.url();
        if (url.includes('/api/') || url.includes(':9123')) {
          apiRequests.push({
            url,
            method: request.method()
          });
        }
      });

      // Reload page to trigger API calls
      await this.page.reload({ waitUntil: 'networkidle2' });
      await new Promise(resolve => setTimeout(resolve, 2000));

      console.log(`✓ Captured ${apiRequests.length} API requests`);

      if (apiRequests.length === 0) {
        console.warn('⚠️  No API requests detected - backend may not be connected');
      } else {
        apiRequests.forEach(req => {
          console.log(`  → ${req.method} ${req.url}`);
        });
      }

    } catch (error) {
      this.errors.push({ source: 'test', test: 'api', message: error.message });
      console.error('❌ API connectivity test failed:', error.message);
    }
  }

  async testResponsiveness() {
    console.log('\n📋 Test 6: Testing Responsive Design...');

    try {
      // Test mobile viewport
      await this.page.setViewport({ width: 375, height: 667 }); // iPhone SE
      await new Promise(resolve => setTimeout(resolve, 1000));
      await this.takeScreenshot('05-mobile-view', 'Mobile viewport (375x667)');
      console.log('✓ Mobile viewport tested');

      // Test tablet viewport
      await this.page.setViewport({ width: 768, height: 1024 }); // iPad
      await new Promise(resolve => setTimeout(resolve, 1000));
      await this.takeScreenshot('06-tablet-view', 'Tablet viewport (768x1024)');
      console.log('✓ Tablet viewport tested');

      // Restore desktop viewport
      await this.page.setViewport({ width: 1920, height: 1080 });
      await new Promise(resolve => setTimeout(resolve, 1000));
      await this.takeScreenshot('07-desktop-view', 'Desktop viewport restored');
      console.log('✓ Desktop viewport restored');

    } catch (error) {
      this.errors.push({ source: 'test', test: 'responsive', message: error.message });
      console.error('❌ Responsive test failed:', error.message);
    }
  }

  async analyzePerformance() {
    console.log('\n📋 Test 7: Analyzing Performance...');

    try {
      const metrics = await this.page.metrics();

      console.log('Performance Metrics:');
      console.log(`  → Script Duration: ${(metrics.ScriptDuration * 1000).toFixed(2)}ms`);
      console.log(`  → Layout Duration: ${(metrics.LayoutDuration * 1000).toFixed(2)}ms`);
      console.log(`  → Recalc Style: ${(metrics.RecalcStyleDuration * 1000).toFixed(2)}ms`);
      console.log(`  → JS Heap Used: ${(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2)}MB`);

      // Get page load performance
      const performanceData = await this.page.evaluate(() => {
        const perf = window.performance.timing;
        return {
          loadTime: perf.loadEventEnd - perf.navigationStart,
          domReady: perf.domContentLoadedEventEnd - perf.navigationStart,
          responseTime: perf.responseEnd - perf.requestStart
        };
      });

      console.log('\nPage Load Performance:');
      console.log(`  → Total Load Time: ${performanceData.loadTime}ms`);
      console.log(`  → DOM Ready: ${performanceData.domReady}ms`);
      console.log(`  → Response Time: ${performanceData.responseTime}ms`);

    } catch (error) {
      this.errors.push({ source: 'test', test: 'performance', message: error.message });
      console.error('❌ Performance analysis failed:', error.message);
    }
  }

  async checkAccessibility() {
    console.log('\n📋 Test 8: Checking Accessibility...');

    try {
      // Check for common accessibility issues
      const a11yIssues = await this.page.evaluate(() => {
        const issues = [];

        // Check for images without alt text
        const imgsWithoutAlt = Array.from(document.querySelectorAll('img:not([alt])'));
        if (imgsWithoutAlt.length > 0) {
          issues.push(`${imgsWithoutAlt.length} images missing alt text`);
        }

        // Check for buttons without labels
        const btnsWithoutLabel = Array.from(document.querySelectorAll('button:not([aria-label]):empty'));
        if (btnsWithoutLabel.length > 0) {
          issues.push(`${btnsWithoutLabel.length} buttons without labels`);
        }

        // Check for proper heading hierarchy
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        if (headings.length === 0) {
          issues.push('No headings found on page');
        }

        // Check for form inputs without labels
        const inputsWithoutLabel = Array.from(document.querySelectorAll('input:not([aria-label]):not([id])'));
        if (inputsWithoutLabel.length > 0) {
          issues.push(`${inputsWithoutLabel.length} inputs without labels`);
        }

        return issues;
      });

      if (a11yIssues.length === 0) {
        console.log('✓ No major accessibility issues detected');
      } else {
        console.warn('⚠️  Accessibility issues found:');
        a11yIssues.forEach(issue => console.warn(`    - ${issue}`));
      }

    } catch (error) {
      this.errors.push({ source: 'test', test: 'accessibility', message: error.message });
      console.error('❌ Accessibility check failed:', error.message);
    }
  }

  async generateReport() {
    console.log('\n📊 Generating Report...');

    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalErrors: this.errors.length,
        totalWarnings: this.warnings.length,
        consoleMessages: this.consoleMessages.length,
        networkErrors: this.networkErrors.length,
        screenshots: this.screenshots.length
      },
      errors: this.errors,
      warnings: this.warnings,
      consoleMessages: this.consoleMessages,
      networkErrors: this.networkErrors,
      screenshots: this.screenshots
    };

    // Save report to file
    fs.writeFileSync(REPORT_FILE, JSON.stringify(report, null, 2));
    console.log(`✓ Report saved to: ${REPORT_FILE}`);

    // Print summary
    console.log('\n' + '='.repeat(80));
    console.log('                      UI REVIEW SUMMARY');
    console.log('='.repeat(80));
    console.log(`Total Errors:       ${report.summary.totalErrors}`);
    console.log(`Total Warnings:     ${report.summary.totalWarnings}`);
    console.log(`Console Messages:   ${report.summary.consoleMessages}`);
    console.log(`Network Errors:     ${report.summary.networkErrors}`);
    console.log(`Screenshots Taken:  ${report.summary.screenshots}`);
    console.log('='.repeat(80));

    if (this.errors.length > 0) {
      console.log('\n❌ TOP ERRORS:');
      this.errors.slice(0, 10).forEach((err, idx) => {
        console.log(`\n${idx + 1}. [${err.source}] ${err.test || ''}`);
        console.log(`   ${err.message}`);
      });
    }

    if (this.networkErrors.length > 0) {
      console.log('\n🌐 NETWORK ERRORS:');
      this.networkErrors.slice(0, 5).forEach((err, idx) => {
        console.log(`${idx + 1}. ${err.url}`);
        console.log(`   Status: ${err.status || err.failure}`);
      });
    }

    console.log('\n📸 Screenshots saved in:', SCREENSHOT_DIR);
    console.log('📄 Full report:', REPORT_FILE);

    return report;
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async runFullReview() {
    try {
      await this.initialize();
      await this.testHomePage();
      await this.testNavigation();
      await this.testGlossaryPage();
      await this.testSearchFeature();
      await this.testAPIConnectivity();
      await this.testResponsiveness();
      await this.analyzePerformance();
      await this.checkAccessibility();

      const report = await this.generateReport();

      return report;
    } catch (error) {
      console.error('❌ Fatal error during review:', error);
      throw error;
    } finally {
      await this.close();
    }
  }
}

// Run the review
(async () => {
  console.log('🔍 Starting Comprehensive UI Review...\n');

  const reviewer = new UIReviewer();

  try {
    await reviewer.runFullReview();
    console.log('\n✅ UI Review Complete!');
    process.exit(0);
  } catch (error) {
    console.error('\n❌ UI Review Failed:', error);
    process.exit(1);
  }
})();
