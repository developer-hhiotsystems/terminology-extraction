/**
 * E2E Test Utilities
 * Helper functions for Puppeteer tests
 */

const fs = require('fs');
const path = require('path');

/**
 * Test result tracking
 */
class TestReporter {
  constructor(testSuiteName) {
    this.testSuiteName = testSuiteName;
    this.startTime = new Date();
    this.tests = [];
    this.currentTest = null;
  }

  startTest(name, description = '') {
    this.currentTest = {
      name,
      description,
      status: 'running',
      startTime: new Date(),
      screenshots: [],
      errors: [],
      warnings: [],
      networkRequests: [],
      consoleMessages: []
    };
  }

  endTest(passed, error = null) {
    if (!this.currentTest) return;

    this.currentTest.status = passed ? 'passed' : 'failed';
    this.currentTest.endTime = new Date();
    this.currentTest.duration = this.currentTest.endTime - this.currentTest.startTime;

    if (error) {
      this.currentTest.errors.push({
        message: error.message,
        stack: error.stack
      });
    }

    this.tests.push(this.currentTest);
    this.currentTest = null;
  }

  addScreenshot(filepath, description = '') {
    if (this.currentTest) {
      this.currentTest.screenshots.push({ filepath, description, timestamp: new Date() });
    }
  }

  addNetworkRequest(url, status, method = 'GET') {
    if (this.currentTest) {
      this.currentTest.networkRequests.push({ url, status, method, timestamp: new Date() });
    }
  }

  addConsoleMessage(type, text) {
    if (this.currentTest) {
      this.currentTest.consoleMessages.push({ type, text, timestamp: new Date() });
    }
  }

  addError(message, source = 'test') {
    if (this.currentTest) {
      this.currentTest.errors.push({ message, source, timestamp: new Date() });
    }
  }

  addWarning(message, source = 'test') {
    if (this.currentTest) {
      this.currentTest.warnings.push({ message, source, timestamp: new Date() });
    }
  }

  getReport() {
    const endTime = new Date();
    const passed = this.tests.filter(t => t.status === 'passed').length;
    const failed = this.tests.filter(t => t.status === 'failed').length;

    return {
      testSuite: this.testSuiteName,
      startTime: this.startTime,
      endTime: endTime,
      duration: endTime - this.startTime,
      summary: {
        total: this.tests.length,
        passed: passed,
        failed: failed,
        passRate: this.tests.length > 0 ? (passed / this.tests.length * 100).toFixed(2) : 0
      },
      tests: this.tests
    };
  }

  saveReport(filepath) {
    const report = this.getReport();
    fs.mkdirSync(path.dirname(filepath), { recursive: true });
    fs.writeFileSync(filepath, JSON.stringify(report, null, 2));
    console.log(`\n📊 Test report saved to: ${filepath}`);
    return report;
  }

  printSummary() {
    const report = this.getReport();
    console.log('\n' + '='.repeat(60));
    console.log(`📋 Test Suite: ${this.testSuiteName}`);
    console.log('='.repeat(60));
    console.log(`✅ Passed: ${report.summary.passed}`);
    console.log(`❌ Failed: ${report.summary.failed}`);
    console.log(`📊 Pass Rate: ${report.summary.passRate}%`);
    console.log(`⏱️  Duration: ${(report.duration / 1000).toFixed(2)}s`);
    console.log('='.repeat(60));

    if (report.summary.failed > 0) {
      console.log('\n❌ Failed Tests:');
      this.tests.filter(t => t.status === 'failed').forEach(test => {
        console.log(`  • ${test.name}`);
        test.errors.forEach(err => {
          console.log(`    - ${err.message}`);
        });
      });
    }
  }
}

/**
 * Screenshot utilities
 */
async function takeScreenshot(page, name, description = '', type = 'test') {
  const timestamp = Date.now();
  const dir = path.join(__dirname, 'test-screenshots', type);
  fs.mkdirSync(dir, { recursive: true });

  const filename = `${name}-${timestamp}.png`;
  const filepath = path.join(dir, filename);

  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`📸 Screenshot saved: ${filename}`);

  return { filepath, filename, description, timestamp };
}

async function takeScreenshotOnError(page, testName, error) {
  const timestamp = Date.now();
  const dir = path.join(__dirname, 'test-screenshots', 'failures');
  fs.mkdirSync(dir, { recursive: true });

  const filename = `failure-${testName.replace(/[^a-z0-9]/gi, '-')}-${timestamp}.png`;
  const filepath = path.join(dir, filename);

  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`❌ Failure screenshot: ${filename}`);

  return { filepath, filename, error: error.message, timestamp };
}

/**
 * Wait utilities
 */
async function waitForElement(page, selector, options = {}) {
  const timeout = options.timeout || 5000;
  const visible = options.visible !== false;

  try {
    await page.waitForSelector(selector, { timeout, visible });
    return true;
  } catch (error) {
    console.warn(`⚠️  Element not found: ${selector}`);
    return false;
  }
}

async function waitForNetworkIdle(page, timeout = 5000) {
  try {
    await page.waitForNetworkIdle({ timeout });
    return true;
  } catch (error) {
    console.warn('⚠️  Network did not become idle');
    return false;
  }
}

async function waitAndClick(page, selector, options = {}) {
  const found = await waitForElement(page, selector, options);
  if (!found) {
    throw new Error(`Cannot click: element not found: ${selector}`);
  }

  await page.click(selector);
  await new Promise(resolve => setTimeout(resolve, 300)); // Small delay after click
  return true;
}

async function waitAndType(page, selector, text, options = {}) {
  const found = await waitForElement(page, selector, options);
  if (!found) {
    throw new Error(`Cannot type: element not found: ${selector}`);
  }

  await page.click(selector); // Focus the element
  await page.keyboard.type(text, { delay: options.delay || 50 });
  return true;
}

/**
 * Network monitoring
 */
function setupNetworkMonitoring(page, reporter) {
  const requests = [];
  const failures = [];

  page.on('request', request => {
    requests.push({
      url: request.url(),
      method: request.method(),
      timestamp: new Date()
    });
  });

  page.on('response', response => {
    const status = response.status();
    const url = response.url();

    if (reporter) {
      reporter.addNetworkRequest(url, status, response.request().method());
    }

    if (status >= 400) {
      console.warn(`⚠️  HTTP ${status}: ${url}`);
      failures.push({ url, status, timestamp: new Date() });
    }
  });

  page.on('requestfailed', request => {
    const url = request.url();
    const failure = request.failure();

    console.error(`❌ Request failed: ${url} - ${failure.errorText}`);
    failures.push({
      url,
      error: failure.errorText,
      timestamp: new Date()
    });
  });

  return { requests, failures };
}

/**
 * Console monitoring
 */
function setupConsoleMonitoring(page, reporter) {
  const messages = [];

  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    messages.push({ type, text, timestamp: new Date() });

    if (reporter) {
      reporter.addConsoleMessage(type, text);
    }

    if (type === 'error') {
      console.error(`🔴 Console Error: ${text}`);
    } else if (type === 'warning') {
      console.warn(`🟡 Console Warning: ${text}`);
    }
  });

  page.on('pageerror', error => {
    const text = error.message;
    console.error(`🔴 Page Error: ${text}`);

    messages.push({
      type: 'pageerror',
      text,
      stack: error.stack,
      timestamp: new Date()
    });

    if (reporter) {
      reporter.addError(text, 'page');
    }
  });

  return messages;
}

/**
 * Element utilities
 */
async function elementExists(page, selector) {
  try {
    const element = await page.$(selector);
    return element !== null;
  } catch (error) {
    return false;
  }
}

async function getElementText(page, selector) {
  try {
    const element = await page.$(selector);
    if (!element) return null;
    return await page.evaluate(el => el.textContent, element);
  } catch (error) {
    return null;
  }
}

async function getElementCount(page, selector) {
  try {
    const elements = await page.$$(selector);
    return elements.length;
  } catch (error) {
    return 0;
  }
}

async function clickElementByText(page, text, tagName = '*') {
  const xpath = `//${tagName}[contains(text(), "${text}")]`;
  const elements = await page.$x(xpath);

  if (elements.length === 0) {
    throw new Error(`No element found with text: ${text}`);
  }

  await elements[0].click();
  await new Promise(resolve => setTimeout(resolve, 300));
  return true;
}

/**
 * API testing utilities
 */
async function testAPIEndpoint(page, url, expectedStatus = 200) {
  let capturedResponse = null;

  // Capture the response
  page.on('response', response => {
    if (response.url() === url) {
      capturedResponse = response;
    }
  });

  // Trigger the request (navigate or interact with UI)
  const status = capturedResponse ? capturedResponse.status() : null;
  const success = status === expectedStatus;

  return {
    success,
    status,
    url,
    expected: expectedStatus
  };
}

/**
 * Form testing utilities
 */
async function fillForm(page, formData) {
  for (const [selector, value] of Object.entries(formData)) {
    await waitAndType(page, selector, value);
  }
}

async function submitForm(page, formSelector) {
  await page.click(`${formSelector} button[type="submit"]`);
  await waitForNetworkIdle(page);
}

/**
 * Test assertions
 */
function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message}\nExpected: ${expected}\nActual: ${actual}`);
  }
}

function assertContains(haystack, needle, message) {
  if (!haystack.includes(needle)) {
    throw new Error(`${message}\nExpected to contain: ${needle}\nActual: ${haystack}`);
  }
}

/**
 * Browser setup
 */
async function createBrowser(puppeteer, options = {}) {
  return await puppeteer.launch({
    headless: options.headless !== false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process'
    ],
    defaultViewport: {
      width: options.width || 1920,
      height: options.height || 1080
    }
  });
}

module.exports = {
  TestReporter,
  takeScreenshot,
  takeScreenshotOnError,
  waitForElement,
  waitForNetworkIdle,
  waitAndClick,
  waitAndType,
  setupNetworkMonitoring,
  setupConsoleMonitoring,
  elementExists,
  getElementText,
  getElementCount,
  clickElementByText,
  testAPIEndpoint,
  fillForm,
  submitForm,
  assert,
  assertEqual,
  assertContains,
  createBrowser
};
