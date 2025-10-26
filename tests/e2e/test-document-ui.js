/**
 * Puppeteer Test Script for Document Upload/Management UI
 * Analyzes current issues with document processing and bulk operations
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function testDocumentUI() {
  console.log('🚀 Starting Document UI Analysis...\n');

  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1920, height: 1080 },
    args: ['--start-maximized']
  });

  const page = await browser.newPage();

  // Enable console logging
  page.on('console', msg => console.log('Browser Console:', msg.text()));
  page.on('pageerror', error => console.error('Browser Error:', error.message));

  try {
    console.log('📍 Navigating to application...');
    await page.goto('http://localhost:3001', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Test 1: Check "New Document" tab
    console.log('\n=== TEST 1: New Document Tab ===');
    await page.click('a[href="/upload"]');
    await new Promise(resolve => setTimeout(resolve, 1000));

    const newDocTitle = await page.$eval('h2', el => el.textContent);
    console.log('✓ Page title:', newDocTitle);

    // Check if batch upload UI is visible
    const hasBatchUpload = await page.evaluate(() => {
      const fileInput = document.querySelector('input[type="file"]');
      return fileInput && fileInput.hasAttribute('multiple');
    });
    console.log('✓ Batch upload support:', hasBatchUpload ? 'YES' : 'NO');

    // Check if selected files list exists
    const hasFilesList = await page.$('.selected-files-list');
    console.log('✓ Selected files list:', hasFilesList ? 'EXISTS' : 'MISSING');

    // Screenshot
    await page.screenshot({ path: 'test-screenshots/01-new-document-tab.png', fullPage: true });
    console.log('📸 Screenshot saved: 01-new-document-tab.png');

    // Test 2: Check "Documents" tab
    console.log('\n=== TEST 2: Documents Tab ===');
    await page.click('a[href="/documents"]');
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Count documents
    const docCount = await page.evaluate(() => {
      const rows = document.querySelectorAll('.document-item, table tbody tr');
      return rows.length;
    });
    console.log('✓ Documents displayed:', docCount);

    // Check if checkboxes exist
    const hasCheckboxes = await page.evaluate(() => {
      const checkboxes = document.querySelectorAll('input[type="checkbox"]');
      return checkboxes.length;
    });
    console.log('✓ Checkboxes found:', hasCheckboxes);

    // Check if bulk delete button exists
    const hasBulkDeleteBtn = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.some(btn =>
        btn.textContent.toLowerCase().includes('delete selected') ||
        btn.textContent.toLowerCase().includes('bulk delete')
      );
    });
    console.log('✓ Bulk delete button:', hasBulkDeleteBtn ? 'EXISTS' : 'MISSING');

    // Check if process button exists for each document
    const hasProcessBtn = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.some(btn => btn.textContent.toLowerCase().includes('process'));
    });
    console.log('✓ Process button:', hasProcessBtn ? 'EXISTS' : 'MISSING');

    // Screenshot
    await page.screenshot({ path: 'test-screenshots/02-documents-tab.png', fullPage: true });
    console.log('📸 Screenshot saved: 02-documents-tab.png');

    // Test 3: Inspect document items structure
    console.log('\n=== TEST 3: Document Item Analysis ===');
    const documentStructure = await page.evaluate(() => {
      const firstDoc = document.querySelector('.document-item, table tbody tr');
      if (!firstDoc) return null;

      return {
        html: firstDoc.outerHTML.substring(0, 500),
        hasCheckbox: !!firstDoc.querySelector('input[type="checkbox"]'),
        hasEditBtn: !!firstDoc.querySelector('button[class*="edit"]') || Array.from(firstDoc.querySelectorAll('button')).some(b => b.className.includes('edit')),
        hasDeleteBtn: !!firstDoc.querySelector('button[class*="delete"]') || Array.from(firstDoc.querySelectorAll('button')).some(b => b.className.includes('delete')),
        hasProcessBtn: Array.from(firstDoc.querySelectorAll('button')).some(b => b.textContent.includes('Process')),
        hasViewBtn: !!firstDoc.querySelector('a[href*="/documents/"]'),
      };
    });

    if (documentStructure) {
      console.log('Document item structure:', {
        hasCheckbox: documentStructure.hasCheckbox,
        hasEditBtn: documentStructure.hasEditBtn,
        hasDeleteBtn: documentStructure.hasDeleteBtn,
        hasProcessBtn: documentStructure.hasProcessBtn,
        hasViewBtn: documentStructure.hasViewBtn,
      });
    }

    // Test 4: Check if we can select documents
    console.log('\n=== TEST 4: Selection Test ===');
    const checkboxes = await page.$$('input[type="checkbox"]');
    console.log('✓ Found', checkboxes.length, 'checkboxes');

    if (checkboxes.length > 0) {
      console.log('Attempting to click first checkbox...');
      await checkboxes[0].click();
      await new Promise(resolve => setTimeout(resolve, 500));

      const isChecked = await checkboxes[0].evaluate(el => el.checked);
      console.log('✓ Checkbox checked:', isChecked ? 'YES' : 'NO');

      // Screenshot after selection
      await page.screenshot({ path: 'test-screenshots/03-document-selected.png', fullPage: true });
      console.log('📸 Screenshot saved: 03-document-selected.png');
    }

    // Test 5: API endpoints check
    console.log('\n=== TEST 5: API Endpoints ===');
    const apiCheck = await page.evaluate(async () => {
      try {
        const healthRes = await fetch('http://localhost:9123/health');
        const health = await healthRes.json();

        const docsRes = await fetch('http://localhost:9123/api/documents');
        const docs = await docsRes.json();

        return {
          backend: 'RUNNING',
          documentsCount: docs.length,
          neo4j: health.neo4j?.status || 'unknown'
        };
      } catch (error) {
        return { error: error.message };
      }
    });
    console.log('API Status:', apiCheck);

    // Summary
    console.log('\n=== SUMMARY ===');
    console.log('Issues Found:');
    console.log('  1. Batch upload UI:', hasBatchUpload && hasFilesList ? '✅ Working' : '❌ Incomplete');
    console.log('  2. Bulk delete button:', hasBulkDeleteBtn ? '✅ Present' : '❌ Missing');
    console.log('  3. Process button:', hasProcessBtn ? '✅ Present' : '❌ Missing');
    console.log('  4. Checkboxes:', hasCheckboxes > 0 ? '✅ Present' : '❌ Missing');
    console.log('  5. Documents count:', docCount);

    console.log('\n✅ Analysis complete! Check test-screenshots/ folder for screenshots.');

  } catch (error) {
    console.error('\n❌ Error during analysis:', error.message);
    await page.screenshot({ path: 'test-screenshots/error.png', fullPage: true });
  } finally {
    await new Promise(resolve => setTimeout(resolve, 2000));
    await browser.close();
  }
}

// Run the test
testDocumentUI().catch(console.error);
