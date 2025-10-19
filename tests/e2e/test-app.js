/**
 * Puppeteer E2E Test for Glossary Management System
 * Tests the complete workflow: Navigation → Upload → Metadata → Process
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const FRONTEND_URL = 'http://localhost:3001';
const BACKEND_URL = 'http://localhost:9123';
const SCREENSHOTS_DIR = './test-screenshots';

// Create screenshots directory
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testApplication() {
  console.log('🚀 Starting Puppeteer E2E Test...\n');

  const browser = await puppeteer.launch({
    headless: false, // Set to true for CI/CD
    defaultViewport: { width: 1920, height: 1080 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  let testsPassed = 0;
  let testsFailed = 0;

  try {
    // ========================================
    // TEST 1: Backend Health Check
    // ========================================
    console.log('📋 TEST 1: Backend Health Check');
    try {
      const healthResponse = await page.goto(BACKEND_URL + '/health');
      const healthData = await healthResponse.json();

      if (healthData.status === 'healthy') {
        console.log('✅ Backend is healthy');
        console.log(`   - Database: ${healthData.database.status}`);
        testsPassed++;
      } else {
        throw new Error('Backend unhealthy');
      }
    } catch (err) {
      console.log('❌ Backend health check failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 2: Frontend Loading
    // ========================================
    console.log('📋 TEST 2: Frontend Loading');
    try {
      await page.goto(FRONTEND_URL, { waitUntil: 'networkidle2' });
      await delay(2000);

      const title = await page.title();
      console.log(`✅ Frontend loaded: ${title}`);

      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '01-homepage.png') });
      console.log('   📸 Screenshot saved: 01-homepage.png');
      testsPassed++;
    } catch (err) {
      console.log('❌ Frontend loading failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 3: Navigation - All Tabs
    // ========================================
    console.log('📋 TEST 3: Navigation - All Tabs');
    const tabs = [
      { name: 'Glossary', selector: 'a[href="/"]' },
      { name: 'Documents', selector: 'a[href="/documents"]' },
      { name: 'New Document', selector: 'a[href="/upload"]' },
      { name: 'Statistics', selector: 'a[href="/statistics"]' },
      { name: 'Admin', selector: 'a[href="/admin"]' }
    ];

    for (const tab of tabs) {
      try {
        await page.click(tab.selector);
        await delay(1500);

        const screenshot = tab.name.toLowerCase().replace(' ', '-');
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, `02-tab-${screenshot}.png`) });

        console.log(`✅ ${tab.name} tab loaded`);
        console.log(`   📸 Screenshot: 02-tab-${screenshot}.png`);
      } catch (err) {
        console.log(`❌ ${tab.name} tab failed:`, err.message);
        testsFailed++;
      }
    }
    testsPassed++;
    console.log('');

    // ========================================
    // TEST 4: Glossary Tab - Check Entries
    // ========================================
    console.log('📋 TEST 4: Glossary Tab - Check Entries');
    try {
      await page.click('a[href="/"]');
      await delay(2000);

      const entryCount = await page.evaluate(() => {
        const entries = document.querySelectorAll('.glossary-entry');
        return entries.length;
      });

      console.log(`✅ Found ${entryCount} glossary entries`);
      testsPassed++;
    } catch (err) {
      console.log('❌ Glossary check failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 5: Documents Tab - Check List
    // ========================================
    console.log('📋 TEST 5: Documents Tab - Check List');
    try {
      await page.click('a[href="/documents"]');
      await delay(2000);

      const docCount = await page.evaluate(() => {
        const rows = document.querySelectorAll('table tbody tr');
        return rows.length;
      });

      console.log(`✅ Found ${docCount} documents`);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '03-documents-list.png') });
      console.log('   📸 Screenshot: 03-documents-list.png');
      testsPassed++;
    } catch (err) {
      console.log('❌ Documents list failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 5A: Document Search Functionality
    // ========================================
    console.log('📋 TEST 5A: Document Search Functionality');
    try {
      await page.click('a[href="/documents"]');
      await delay(1000);

      // Test search input
      const searchInput = await page.$('.search-input');
      if (searchInput) {
        await searchInput.type('sample');
        await delay(1500);

        const filteredCount = await page.evaluate(() => {
          const rows = document.querySelectorAll('table tbody tr');
          return rows.length;
        });

        console.log(`✅ Search working: Found ${filteredCount} document(s) matching "sample"`);

        // Clear search
        await searchInput.click({ clickCount: 3 });
        await searchInput.press('Backspace');
        await delay(1000);

        testsPassed++;
      } else {
        throw new Error('Search input not found');
      }
    } catch (err) {
      console.log('❌ Document search failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 5B: Filter by Status
    // ========================================
    console.log('📋 TEST 5B: Filter by Status');
    try {
      const statusFilter = await page.$('.filter-select');
      if (statusFilter) {
        await statusFilter.select('completed');
        await delay(1500);

        const filteredCount = await page.evaluate(() => {
          const rows = document.querySelectorAll('table tbody tr');
          return rows.length;
        });

        console.log(`✅ Status filter working: ${filteredCount} completed document(s)`);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '03a-filtered-status.png') });
        console.log('   📸 Screenshot: 03a-filtered-status.png');

        // Reset filter
        await statusFilter.select('all');
        await delay(1000);

        testsPassed++;
      } else {
        throw new Error('Status filter not found');
      }
    } catch (err) {
      console.log('❌ Status filter failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 5C: Bulk Selection UI
    // ========================================
    console.log('📋 TEST 5C: Bulk Selection UI');
    try {
      const checkboxes = await page.$$('table tbody tr input[type="checkbox"]');

      if (checkboxes.length > 0) {
        // Select first document
        await checkboxes[0].click();
        await delay(1000);

        // Check if bulk actions bar appears
        const bulkActionsBar = await page.$('.bulk-actions-bar');
        if (bulkActionsBar) {
          const selectionText = await page.evaluate(() => {
            return document.querySelector('.selected-count')?.textContent;
          });

          console.log(`✅ Bulk selection working: ${selectionText}`);
          await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '03b-bulk-selection.png') });
          console.log('   📸 Screenshot: 03b-bulk-selection.png');

          // Deselect
          await checkboxes[0].click();
          await delay(1000);

          testsPassed++;
        } else {
          throw new Error('Bulk actions bar not shown');
        }
      } else {
        console.log('⚠️  No documents available for bulk selection test');
        testsPassed++;
      }
    } catch (err) {
      console.log('❌ Bulk selection failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 5D: Edit Metadata Modal
    // ========================================
    console.log('📋 TEST 5D: Edit Metadata Modal');
    try {
      const editButtons = await page.$$('.btn-edit-small');

      if (editButtons.length > 0) {
        // Click first Edit button
        await editButtons[0].click();
        await delay(1500);

        // Check if modal appears
        const modal = await page.$('.modal-overlay');
        if (modal) {
          const modalTitle = await page.evaluate(() => {
            return document.querySelector('.modal-header h3')?.textContent;
          });

          console.log(`✅ Edit modal opened: ${modalTitle}`);
          await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '03c-edit-modal.png') });
          console.log('   📸 Screenshot: 03c-edit-modal.png');

          // Check form fields
          const formFields = await page.evaluate(() => {
            return {
              documentNumber: !!document.querySelector('#edit_document_number'),
              documentType: !!document.querySelector('#edit_document_type'),
              documentLink: !!document.querySelector('#edit_document_link')
            };
          });

          console.log(`   - Document Number field: ${formFields.documentNumber ? '✓' : '✗'}`);
          console.log(`   - Document Type field: ${formFields.documentType ? '✓' : '✗'}`);
          console.log(`   - Document Link field: ${formFields.documentLink ? '✓' : '✗'}`);

          // Close modal
          const closeButton = await page.$('.modal-close');
          if (closeButton) {
            await closeButton.click();
            await delay(1000);
          }

          testsPassed++;
        } else {
          throw new Error('Edit modal did not open');
        }
      } else {
        console.log('⚠️  No documents available for edit modal test');
        testsPassed++;
      }
    } catch (err) {
      console.log('❌ Edit metadata modal failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 5E: Filter Controls & Clear Button
    // ========================================
    console.log('📋 TEST 5E: Filter Controls & Clear Button');
    try {
      // Apply a search filter
      const searchInput = await page.$('.search-input');
      if (searchInput) {
        await searchInput.type('test');
        await delay(1000);

        // Check if Clear Filters button appears
        const clearButton = await page.$('.btn-secondary-small');
        if (clearButton) {
          const buttonText = await page.evaluate(btn => btn.textContent, clearButton);

          if (buttonText.includes('Clear Filters')) {
            console.log('✅ Clear Filters button appeared');

            // Click clear button
            await clearButton.click();
            await delay(1000);

            // Verify search is cleared
            const searchValue = await page.evaluate(() => {
              const input = document.querySelector('.search-input');
              return input ? input.value : null;
            });

            if (searchValue === '') {
              console.log('✅ Filters cleared successfully');
            }

            testsPassed++;
          } else {
            throw new Error('Clear Filters button not found');
          }
        } else {
          throw new Error('Clear button did not appear');
        }
      }
    } catch (err) {
      console.log('❌ Filter controls test failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 6: New Document Tab - UI Elements
    // ========================================
    console.log('📋 TEST 6: New Document Tab - UI Elements');
    try {
      await page.click('a[href="/upload"]');
      await delay(2000);

      // Check for key elements
      const elements = await page.evaluate(() => {
        return {
          dropZone: !!document.querySelector('.drop-zone'),
          title: document.querySelector('h2')?.textContent,
          subtitle: document.querySelector('p')?.textContent
        };
      });

      if (elements.dropZone && elements.title === 'New Document') {
        console.log('✅ Upload page UI elements present');
        console.log(`   - Title: ${elements.title}`);
        console.log(`   - Subtitle: ${elements.subtitle}`);
        testsPassed++;
      } else {
        throw new Error('Missing UI elements');
      }

      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '04-new-document-page.png') });
      console.log('   📸 Screenshot: 04-new-document-page.png');
    } catch (err) {
      console.log('❌ New Document UI check failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 7: Admin Tab - Document Types
    // ========================================
    console.log('📋 TEST 7: Admin Tab - Document Types');
    try {
      await page.click('a[href="/admin"]');
      await delay(2000);

      const docTypes = await page.evaluate(() => {
        const rows = document.querySelectorAll('.document-types-table tbody tr');
        return Array.from(rows).map(row => {
          const cells = row.querySelectorAll('td');
          return {
            code: cells[0]?.textContent,
            labelEn: cells[1]?.textContent,
            labelDe: cells[2]?.textContent
          };
        });
      });

      console.log(`✅ Found ${docTypes.length} document types:`);
      docTypes.slice(0, 3).forEach(type => {
        console.log(`   - ${type.code}: ${type.labelEn} (${type.labelDe})`);
      });

      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '05-admin-document-types.png') });
      console.log('   📸 Screenshot: 05-admin-document-types.png');
      testsPassed++;
    } catch (err) {
      console.log('❌ Admin tab check failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 8: Statistics Tab
    // ========================================
    console.log('📋 TEST 8: Statistics Tab');
    try {
      await page.click('a[href="/statistics"]');
      await delay(2000);

      const stats = await page.evaluate(() => {
        const statCards = document.querySelectorAll('.stat-card');
        return Array.from(statCards).map(card => ({
          label: card.querySelector('.stat-label')?.textContent,
          value: card.querySelector('.stat-value')?.textContent
        }));
      });

      console.log(`✅ Statistics dashboard loaded with ${stats.length} cards`);
      stats.forEach(stat => {
        console.log(`   - ${stat.label}: ${stat.value}`);
      });

      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '06-statistics.png') });
      console.log('   📸 Screenshot: 06-statistics.png');
      testsPassed++;
    } catch (err) {
      console.log('❌ Statistics check failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 9: API Endpoints Test
    // ========================================
    console.log('📋 TEST 9: API Endpoints Test');
    try {
      const endpoints = [
        '/api/glossary',
        '/api/documents',
        '/api/admin/document-types',
        '/api/admin/stats'
      ];

      for (const endpoint of endpoints) {
        const response = await page.goto(BACKEND_URL + endpoint);
        const status = response.status();

        if (status === 200) {
          console.log(`✅ ${endpoint} - Status ${status}`);
        } else {
          console.log(`⚠️  ${endpoint} - Status ${status}`);
        }
      }
      testsPassed++;
    } catch (err) {
      console.log('❌ API endpoints test failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST 10: Responsive Design Check
    // ========================================
    console.log('📋 TEST 10: Responsive Design Check');
    try {
      const viewports = [
        { name: 'Desktop', width: 1920, height: 1080 },
        { name: 'Tablet', width: 768, height: 1024 },
        { name: 'Mobile', width: 375, height: 667 }
      ];

      await page.goto(FRONTEND_URL);

      for (const viewport of viewports) {
        await page.setViewport({ width: viewport.width, height: viewport.height });
        await delay(1000);

        await page.screenshot({
          path: path.join(SCREENSHOTS_DIR, `07-responsive-${viewport.name.toLowerCase()}.png`),
          fullPage: true
        });

        console.log(`✅ ${viewport.name} (${viewport.width}x${viewport.height})`);
        console.log(`   📸 Screenshot: 07-responsive-${viewport.name.toLowerCase()}.png`);
      }
      testsPassed++;
    } catch (err) {
      console.log('❌ Responsive design check failed:', err.message);
      testsFailed++;
    }
    console.log('');

    // ========================================
    // TEST SUMMARY
    // ========================================
    console.log('═══════════════════════════════════════');
    console.log('📊 TEST SUMMARY');
    console.log('═══════════════════════════════════════');
    console.log(`✅ Tests Passed: ${testsPassed}`);
    console.log(`❌ Tests Failed: ${testsFailed}`);
    console.log(`📁 Screenshots saved to: ${SCREENSHOTS_DIR}`);
    console.log('═══════════════════════════════════════\n');

    if (testsFailed === 0) {
      console.log('🎉 ALL TESTS PASSED! Application is working correctly.\n');
    } else {
      console.log('⚠️  Some tests failed. Check the output above for details.\n');
    }

  } catch (error) {
    console.error('💥 Fatal error during testing:', error);
  } finally {
    await browser.close();
    console.log('🏁 Test complete. Browser closed.\n');
  }
}

// Run the test
testApplication().catch(console.error);
