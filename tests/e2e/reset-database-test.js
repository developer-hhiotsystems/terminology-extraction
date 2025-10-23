/**
 * Database Reset Test - Verify Reset Functionality via UI
 */

const puppeteer = require('puppeteer');
const path = require('path');

const FRONTEND_URL = 'http://localhost:3001';
const BACKEND_URL = 'http://localhost:9123';
const SCREENSHOT_DIR = path.join(__dirname, 'test-screenshots');

async function resetDatabase() {
  console.log('\n🚀 Starting Database Reset Test');
  console.log('================================\n');

  const browser = await puppeteer.launch({
    headless: false, // Show browser so you can see what's happening
    defaultViewport: { width: 1920, height: 1080 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  try {
    // Step 1: Navigate to homepage
    console.log('📍 Step 1: Navigating to homepage...');
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle2', timeout: 10000 });
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Take screenshot
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-1-homepage.png'), fullPage: true });
    console.log('✅ Homepage loaded\n');

    // Step 2: Check current database stats
    console.log('📍 Step 2: Checking current database stats...');
    const statsResponse = await fetch(`${BACKEND_URL}/api/admin/stats`);
    const statsBefore = await statsResponse.json();
    console.log('📊 Current database stats:', {
      entries: statsBefore.total_glossary_entries || 0,
      documents: statsBefore.total_documents || 0
    });
    console.log('');

    // Step 3: Navigate to glossary page
    console.log('📍 Step 3: Navigating to glossary page...');
    await page.goto(`${FRONTEND_URL}/`, { waitUntil: 'networkidle2', timeout: 10000 });
    await new Promise(resolve => setTimeout(resolve, 2000));

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-2-glossary.png'), fullPage: true });
    console.log('✅ Glossary page loaded\n');

    // Step 4: Find Reset DB button
    console.log('📍 Step 4: Looking for Reset DB button...');

    // Look for the Reset DB button
    const resetButton = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find(btn =>
        btn.textContent.includes('Reset') &&
        (btn.textContent.includes('DB') || btn.textContent.includes('Database'))
      );
    }).then(handle => handle.asElement());

    if (!resetButton) {
      console.log('❌ Reset DB button not found!');
      console.log('📸 Taking screenshot of page...');
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-3-button-not-found.png'), fullPage: true });

      // Print all buttons on page for debugging
      const allButtons = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('button')).map(btn => ({
          text: btn.textContent.trim(),
          class: btn.className,
          title: btn.title
        }));
      });
      console.log('\n📋 All buttons found on page:');
      allButtons.forEach((btn, i) => {
        console.log(`  ${i + 1}. "${btn.text}" (class: ${btn.class}, title: ${btn.title})`);
      });

      throw new Error('Reset DB button not found on page');
    }

    console.log('✅ Reset DB button found!\n');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-3-button-found.png'), fullPage: true });

    // Step 5: Click Reset DB button
    console.log('📍 Step 5: Clicking Reset DB button...');
    await resetButton.click();
    await new Promise(resolve => setTimeout(resolve, 1000));

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-4-modal-opened.png'), fullPage: true });
    console.log('✅ Modal should be open\n');

    // Step 6: Look for confirmation button
    console.log('📍 Step 6: Looking for confirmation button...');

    await new Promise(resolve => setTimeout(resolve, 500));

    // Find the "Yes, Reset Database" confirmation button
    const confirmButton = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find(btn =>
        btn.textContent.includes('Yes') ||
        btn.textContent.includes('Reset')
      );
    }).then(handle => handle.asElement());

    if (!confirmButton) {
      console.log('⚠️  Confirmation button not found, modal might not have opened');
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-5-confirm-not-found.png'), fullPage: true });
      throw new Error('Confirmation button not found');
    }

    console.log('✅ Confirmation button found!\n');

    // Step 7: Confirm reset
    console.log('📍 Step 7: Confirming database reset...');
    console.log('⚠️  WARNING: This will DELETE all data!\n');

    await confirmButton.click();
    console.log('✅ Reset confirmed, waiting for operation...');

    // Wait for reset to complete
    await new Promise(resolve => setTimeout(resolve, 3000));

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-6-reset-complete.png'), fullPage: true });
    console.log('');

    // Step 8: Verify reset
    console.log('📍 Step 8: Verifying database was reset...');

    const statsAfterResponse = await fetch(`${BACKEND_URL}/api/admin/stats`);
    const statsAfter = await statsAfterResponse.json();

    console.log('📊 Database stats after reset:', {
      entries: statsAfter.total_glossary_entries || 0,
      documents: statsAfter.total_documents || 0
    });

    // Check if database was actually reset
    const wasReset = (statsAfter.total_glossary_entries === 0 || statsAfter.total_glossary_entries < statsBefore.total_glossary_entries);

    if (wasReset) {
      console.log('');
      console.log('✅ ✅ ✅ DATABASE RESET SUCCESSFUL! ✅ ✅ ✅');
      console.log('');
      console.log('📊 Reset Summary:');
      console.log(`   Before: ${statsBefore.total_glossary_entries || 0} entries`);
      console.log(`   After:  ${statsAfter.total_glossary_entries || 0} entries`);
      console.log(`   Deleted: ${(statsBefore.total_glossary_entries || 0) - (statsAfter.total_glossary_entries || 0)} entries`);
    } else {
      console.log('');
      console.log('⚠️  Database might not have been reset (same entry count)');
      console.log('   This could mean the database was already empty');
    }

    console.log('\n================================');
    console.log('🎉 Test Complete!\n');

    // Keep browser open for 3 seconds so you can see the result
    await new Promise(resolve => setTimeout(resolve, 3000));

  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    console.error('\n📸 Screenshot saved for debugging\n');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'reset-error.png'), fullPage: true });
  } finally {
    await browser.close();
  }
}

// Run the test
resetDatabase().catch(console.error);
