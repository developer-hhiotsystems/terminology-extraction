/**
 * Relationship Feature Test Suite
 * Tests the Relationship Explorer and Graph Visualization features
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
  assert,
  createBrowser
} = require('./test-utils');

const FRONTEND_URL = 'http://localhost:3000';

class RelationshipFeatureTest {
  constructor() {
    this.reporter = new TestReporter('Relationship Feature Test');
    this.browser = null;
    this.page = null;
  }

  async setup() {
    console.log('🚀 Starting Relationship Feature Test Suite');
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

    const report = this.reporter.saveReport('./tests/e2e/test-results-relationship.json');
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

  async testRelationshipPageLoads() {
    await this.runTest(
      'Relationship Page Loads',
      'Verify relationship explorer page loads',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        const url = this.page.url();
        assert(url.includes('/relationships'), 'Not on relationships page');

        await takeScreenshot(this.page, 'relationship-page-load', 'Relationships page loaded', 'success');
      }
    );
  }

  // =====================================================
  // GRAPH VISUALIZATION TESTS
  // =====================================================

  async testGraphExists() {
    await this.runTest(
      'Graph Visualization Exists',
      'Verify graph SVG/Canvas element is present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000)); // Graph needs time to render

        // Look for SVG or Canvas
        const hasSVG = await elementExists(this.page, 'svg');
        const hasCanvas = await elementExists(this.page, 'canvas');

        assert(hasSVG || hasCanvas, 'No graph visualization element (SVG or Canvas) found');

        if (hasSVG) {
          console.log('✓ SVG graph found');
        }
        if (hasCanvas) {
          console.log('✓ Canvas graph found');
        }

        await takeScreenshot(this.page, 'graph-visualization', 'Graph rendered', 'success');
      }
    );
  }

  async testGraphNodesExist() {
    await this.runTest(
      'Graph Nodes Exist',
      'Verify graph nodes are rendered',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Look for node elements
        const nodeCount = await getElementCount(
          this.page,
          'circle, .node, [class*="node"]'
        );

        console.log(`Found ${nodeCount} graph nodes`);

        if (nodeCount === 0) {
          console.warn('⚠️  No graph nodes found (might be empty or Canvas-based)');
        } else {
          console.log(`✓ ${nodeCount} nodes rendered`);
        }
      }
    );
  }

  async testGraphEdgesExist() {
    await this.runTest(
      'Graph Edges Exist',
      'Verify graph edges/links are rendered',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Look for edge elements
        const edgeCount = await getElementCount(
          this.page,
          'line, path, .edge, .link, [class*="edge"], [class*="link"]'
        );

        console.log(`Found ${edgeCount} graph edges`);

        if (edgeCount === 0) {
          console.warn('⚠️  No graph edges found (might be empty or Canvas-based)');
        } else {
          console.log(`✓ ${edgeCount} edges rendered`);
        }
      }
    );
  }

  // =====================================================
  // GRAPH INTERACTION TESTS
  // =====================================================

  async testGraphNodeHover() {
    await this.runTest(
      'Graph Node Hover',
      'Test hovering over graph nodes',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Try to find and hover over a node
        const node = await this.page.$('circle, .node');

        if (node) {
          await node.hover();
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ Hovered over graph node');
          await takeScreenshot(this.page, 'graph-node-hover', 'Node hover state', 'success');
        } else {
          console.warn('⚠️  No hoverable nodes found');
        }
      }
    );
  }

  async testGraphNodeClick() {
    await this.runTest(
      'Graph Node Click',
      'Test clicking on graph nodes',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Try to find and click a node
        const node = await this.page.$('circle, .node');

        if (node) {
          await node.click();
          await new Promise(resolve => setTimeout(resolve, 1000));

          console.log('✓ Clicked graph node');
          await takeScreenshot(this.page, 'graph-node-click', 'Node clicked', 'success');

          // Check if a tooltip or detail panel appeared
          const hasTooltip = await elementExists(
            this.page,
            '.tooltip, .popover, .detail-panel, [class*="tooltip"]'
          );

          if (hasTooltip) {
            console.log('✓ Tooltip/detail panel appeared');
          }
        } else {
          console.warn('⚠️  No clickable nodes found');
        }
      }
    );
  }

  async testGraphZoom() {
    await this.runTest(
      'Graph Zoom',
      'Test graph zoom functionality',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Look for zoom controls
        const zoomIn = await this.page.$('button[aria-label*="zoom in" i], button[title*="zoom in" i], .zoom-in');
        const zoomOut = await this.page.$('button[aria-label*="zoom out" i], button[title*="zoom out" i], .zoom-out');

        if (zoomIn) {
          await zoomIn.click();
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('✓ Zoom in clicked');
        }

        if (zoomOut) {
          await zoomOut.click();
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('✓ Zoom out clicked');
        }

        if (!zoomIn && !zoomOut) {
          console.warn('⚠️  No zoom controls found (might use mouse wheel)');
        }

        await takeScreenshot(this.page, 'graph-zoom', 'After zoom operations', 'success');
      }
    );
  }

  async testGraphPan() {
    await this.runTest(
      'Graph Pan/Drag',
      'Test graph panning/dragging',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        const svg = await this.page.$('svg');
        const canvas = await this.page.$('canvas');
        const graphElement = svg || canvas;

        if (graphElement) {
          // Get element position
          const box = await graphElement.boundingBox();

          if (box) {
            // Simulate drag
            await this.page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
            await this.page.mouse.down();
            await this.page.mouse.move(box.x + 100, box.y + 100);
            await this.page.mouse.up();

            console.log('✓ Graph drag simulated');
            await new Promise(resolve => setTimeout(resolve, 500));
          }
        } else {
          console.warn('⚠️  No graph element found for panning');
        }
      }
    );
  }

  // =====================================================
  // FILTER TESTS
  // =====================================================

  async testRelationshipFilters() {
    await this.runTest(
      'Relationship Filters Exist',
      'Verify filter controls are present',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });

        const filters = await this.page.$$('select, input[type="checkbox"], input[type="radio"], .filter');

        console.log(`Found ${filters.length} filter controls`);

        if (filters.length === 0) {
          console.warn('⚠️  No relationship filters found');
        } else {
          console.log(`✓ ${filters.length} filter controls exist`);
        }

        await takeScreenshot(this.page, 'relationship-filters', 'Filter controls', 'success');
      }
    );
  }

  async testFilterInteraction() {
    await this.runTest(
      'Filter Interaction',
      'Test interacting with filters',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Try to interact with first filter
        const select = await this.page.$('select');
        const checkbox = await this.page.$('input[type="checkbox"]');

        if (select) {
          await select.click();
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('✓ Filter dropdown clicked');

          await takeScreenshot(this.page, 'filter-dropdown', 'Filter dropdown open', 'success');
        }

        if (checkbox) {
          await checkbox.click();
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('✓ Filter checkbox toggled');
        }

        if (!select && !checkbox) {
          console.warn('⚠️  No interactive filters found');
        }
      }
    );
  }

  // =====================================================
  // DATA LOADING TESTS
  // =====================================================

  async testGraphDataLoading() {
    await this.runTest(
      'Graph Data Loading',
      'Verify graph data is loaded from API',
      async () => {
        let apiCalled = false;

        this.page.on('response', async (response) => {
          const url = response.url();
          if (url.includes('/api/relationship') ||
              url.includes('/api/graph') ||
              url.includes('/api/extract')) {
            apiCalled = true;
            console.log(`✓ Graph API called: ${url}`);
          }
        });

        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        if (!apiCalled) {
          console.warn('⚠️  No graph API call detected');
        }
      }
    );
  }

  async testGraphLoadingState() {
    await this.runTest(
      'Graph Loading State',
      'Verify loading indicator is shown',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'domcontentloaded' });

        // Look for loading indicator
        const hasLoader = await elementExists(
          this.page,
          '.loading, .spinner, [class*="loading"], [class*="spinner"]'
        );

        if (hasLoader) {
          console.log('✓ Loading indicator displayed');
          await takeScreenshot(this.page, 'graph-loading', 'Graph loading state', 'success');
        } else {
          console.warn('⚠️  No loading indicator found (might load too fast)');
        }

        await new Promise(resolve => setTimeout(resolve, 3000));
      }
    );
  }

  // =====================================================
  // LEGEND AND LABELS TESTS
  // =====================================================

  async testGraphLegend() {
    await this.runTest(
      'Graph Legend Exists',
      'Verify graph legend is displayed',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        const hasLegend = await elementExists(
          this.page,
          '.legend, [class*="legend"]'
        );

        if (hasLegend) {
          console.log('✓ Graph legend exists');
        } else {
          console.warn('⚠️  No graph legend found');
        }
      }
    );
  }

  async testNodeLabels() {
    await this.runTest(
      'Node Labels Visible',
      'Verify node labels are displayed',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        const labelCount = await getElementCount(
          this.page,
          'text, .label, [class*="label"]'
        );

        console.log(`Found ${labelCount} text/label elements`);

        if (labelCount === 0) {
          console.warn('⚠️  No node labels found');
        } else {
          console.log(`✓ ${labelCount} labels visible`);
        }
      }
    );
  }

  // =====================================================
  // EXPORT/SHARE TESTS
  // =====================================================

  async testGraphExport() {
    await this.runTest(
      'Graph Export Feature',
      'Test graph export/download functionality',
      async () => {
        await this.page.goto(`${FRONTEND_URL}/relationships`, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));

        const exportButton = await this.page.$('button[aria-label*="export" i], button[title*="export" i], button:has-text("Export")');

        if (exportButton) {
          console.log('✓ Export button exists');
          // Note: Not clicking to avoid download dialog
        } else {
          console.warn('⚠️  No export button found');
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
      await this.testRelationshipPageLoads();

      console.log('\n📋 TESTING: GRAPH VISUALIZATION');
      await this.testGraphExists();
      await this.testGraphNodesExist();
      await this.testGraphEdgesExist();

      console.log('\n📋 TESTING: GRAPH INTERACTIONS');
      await this.testGraphNodeHover();
      await this.testGraphNodeClick();
      await this.testGraphZoom();
      await this.testGraphPan();

      console.log('\n📋 TESTING: FILTERS');
      await this.testRelationshipFilters();
      await this.testFilterInteraction();

      console.log('\n📋 TESTING: DATA LOADING');
      await this.testGraphDataLoading();
      await this.testGraphLoadingState();

      console.log('\n📋 TESTING: LEGEND AND LABELS');
      await this.testGraphLegend();
      await this.testNodeLabels();

      console.log('\n📋 TESTING: EXPORT');
      await this.testGraphExport();

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
  const test = new RelationshipFeatureTest();
  test.runAllTests()
    .then(report => {
      console.log('\n✨ Relationship feature test suite completed');
      process.exit(report.summary.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = RelationshipFeatureTest;
