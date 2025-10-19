const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Starting browser automation test...\n');

  const browser = await puppeteer.launch({
    headless: false, // Show the browser so we can see what's happening
    slowMo: 100, // Slow down operations by 100ms
  });

  try {
    const page = await browser.newPage();

    // Listen for console messages from the page
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      console.log(`[Browser ${type.toUpperCase()}]:`, text);
    });

    // Listen for page errors
    page.on('pageerror', error => {
      console.error('❌ [Page Error]:', error.message);
    });

    // Listen for failed requests
    page.on('requestfailed', request => {
      console.error('❌ [Request Failed]:', request.url());
    });

    console.log('📱 Navigating to http://localhost:3001...');
    await page.goto('http://localhost:3001', { waitUntil: 'networkidle0' });

    const currentUrl = page.url();
    console.log('✅ Current URL:', currentUrl);

    // Take initial screenshot
    await page.screenshot({ path: 'docs/test-1-homepage.png', fullPage: true });
    console.log('📸 Screenshot saved: test-1-homepage.png\n');

    // Wait a moment for React to render
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Check if we're on the glossary page (it's the default route)
    const pageTitle = await page.title();
    console.log('📄 Page title:', pageTitle);

    // Find the search input
    console.log('\n🔍 Looking for search input...');
    const searchInput = await page.$('input[type="text"][placeholder*="Search"]');

    if (!searchInput) {
      console.error('❌ Search input not found!');
      await page.screenshot({ path: 'docs/test-error-no-input.png', fullPage: true });
      await browser.close();
      return;
    }
    console.log('✅ Search input found');

    // Type "Reactor" into the search box
    console.log('\n⌨️  Typing "Reactor" into search box...');
    await searchInput.click();
    await searchInput.type('Reactor', { delay: 100 });

    // Take screenshot after typing
    await page.screenshot({ path: 'docs/test-2-after-typing.png', fullPage: true });
    console.log('📸 Screenshot saved: test-2-after-typing.png');

    // Get the current URL before search
    const urlBeforeSearch = page.url();
    console.log('📍 URL before search:', urlBeforeSearch);

    // Find and click the search button
    console.log('\n🔘 Looking for search button...');
    const searchButton = await page.$('button[type="submit"]');

    if (searchButton) {
      console.log('✅ Search button found (type="submit")');
      console.log('🖱️  Clicking search button...');
      await searchButton.click();
    } else {
      // Try pressing Enter instead
      console.log('⚠️  Submit button not found, trying Enter key...');
      await searchInput.press('Enter');
    }

    // Wait for navigation or response
    console.log('\n⏳ Waiting for results...');
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check URL after search
    const urlAfterSearch = page.url();
    console.log('📍 URL after search:', urlAfterSearch);

    if (urlBeforeSearch !== urlAfterSearch) {
      console.log('⚠️  URL CHANGED! Navigation occurred.');
    } else {
      console.log('✅ URL stayed the same (no navigation)');
    }

    // Take screenshot after search
    await page.screenshot({ path: 'docs/test-3-after-search.png', fullPage: true });
    console.log('📸 Screenshot saved: test-3-after-search.png');

    // Check for entries on the page
    const entryCards = await page.$$('.entry-card');
    console.log(`\n📊 Found ${entryCards.length} entry cards on page`);

    // Check for empty state
    const emptyState = await page.$('.empty-state');
    if (emptyState) {
      const emptyText = await page.evaluate(el => el.textContent, emptyState);
      console.log('⚠️  Empty state found:', emptyText);
    }

    // Check for error messages
    const errorState = await page.$('.error');
    if (errorState) {
      const errorText = await page.evaluate(el => el.textContent, errorState);
      console.error('❌ Error state found:', errorText);
    }

    // Check for toast notifications
    await new Promise(resolve => setTimeout(resolve, 500));
    const toasts = await page.$$('.Toastify__toast');
    if (toasts.length > 0) {
      console.log(`\n📬 Found ${toasts.length} toast notification(s)`);
      for (const toast of toasts) {
        const toastText = await page.evaluate(el => el.textContent, toast);
        console.log('  Toast:', toastText);
      }
    }

    // Get first few entry terms if any exist
    if (entryCards.length > 0) {
      console.log('\n📝 First 5 entries:');
      for (let i = 0; i < Math.min(5, entryCards.length); i++) {
        const termText = await entryCards[i].$eval('h3', el => el.textContent);
        console.log(`  ${i + 1}. ${termText}`);
      }
    }

    console.log('\n✅ Test completed! Check the screenshots in the docs/ folder.');

  } catch (error) {
    console.error('\n❌ Test failed with error:', error.message);
    console.error(error.stack);
  } finally {
    // Keep browser open for 5 seconds so we can see the result
    console.log('\n⏳ Keeping browser open for 5 seconds...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    await browser.close();
    console.log('👋 Browser closed');
  }
})();
