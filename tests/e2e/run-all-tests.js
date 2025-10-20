/**
 * Master Test Runner
 * Runs all E2E test suites and generates consolidated report
 */

const fs = require('fs');
const path = require('path');

const ComprehensiveFeatureTest = require('./comprehensive-feature-test');
const APIIntegrationTest = require('./api-integration-test');
const SearchFeatureTest = require('./search-feature-test');
const RelationshipFeatureTest = require('./relationship-feature-test');
const EnhancedGlossaryTest = require('./enhanced-glossary-test');

class MasterTestRunner {
  constructor() {
    this.startTime = new Date();
    this.reports = [];
    this.testSuites = [
      { name: 'Comprehensive Features', class: ComprehensiveFeatureTest, priority: 'HIGH' },
      { name: 'API Integration', class: APIIntegrationTest, priority: 'HIGH' },
      { name: 'Search Features', class: SearchFeatureTest, priority: 'HIGH' },
      { name: 'Relationship Explorer', class: RelationshipFeatureTest, priority: 'MEDIUM' },
      { name: 'Enhanced Glossary', class: EnhancedGlossaryTest, priority: 'MEDIUM' }
    ];
  }

  async runAllTests() {
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║       GLOSSARY APP - COMPREHENSIVE E2E TEST SUITE          ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log(`Started at: ${this.startTime.toLocaleString()}\n`);

    for (const suite of this.testSuites) {
      console.log('\n' + '═'.repeat(60));
      console.log(`Running: ${suite.name} [${suite.priority}]`);
      console.log('═'.repeat(60));

      try {
        const testInstance = new suite.class();
        const report = await testInstance.runAllTests();
        this.reports.push({
          suiteName: suite.name,
          priority: suite.priority,
          report: report
        });

        console.log(`\n✅ ${suite.name} completed`);
      } catch (error) {
        console.error(`\n❌ ${suite.name} failed: ${error.message}`);
        this.reports.push({
          suiteName: suite.name,
          priority: suite.priority,
          report: {
            summary: { total: 0, passed: 0, failed: 1 },
            error: error.message
          }
        });
      }

      // Small delay between suites
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    return this.generateConsolidatedReport();
  }

  generateConsolidatedReport() {
    const endTime = new Date();
    const duration = endTime - this.startTime;

    // Calculate totals
    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;

    const suiteResults = this.reports.map(({ suiteName, priority, report }) => {
      const summary = report.summary || { total: 0, passed: 0, failed: 0 };

      totalTests += summary.total || 0;
      totalPassed += summary.passed || 0;
      totalFailed += summary.failed || 0;

      return {
        suite: suiteName,
        priority: priority,
        total: summary.total || 0,
        passed: summary.passed || 0,
        failed: summary.failed || 0,
        passRate: summary.passRate || '0.00',
        error: report.error || null
      };
    });

    // Identify broken features
    const brokenFeatures = [];

    this.reports.forEach(({ suiteName, report }) => {
      if (report.tests) {
        const failedTests = report.tests.filter(t => t.status === 'failed');

        failedTests.forEach(test => {
          brokenFeatures.push({
            feature: `${suiteName} - ${test.name}`,
            suite: suiteName,
            testName: test.name,
            errors: test.errors || [],
            priority: this.getPriorityForFeature(test.name)
          });
        });
      }
    });

    const consolidatedReport = {
      testDate: this.startTime.toISOString(),
      endTime: endTime.toISOString(),
      duration: `${(duration / 1000).toFixed(2)}s`,
      summary: {
        totalSuites: this.testSuites.length,
        totalTests: totalTests,
        passed: totalPassed,
        failed: totalFailed,
        passRate: totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(2) : '0.00'
      },
      suites: suiteResults,
      brokenFeatures: brokenFeatures.sort((a, b) => {
        const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      }),
      recommendations: this.generateRecommendations(brokenFeatures, suiteResults)
    };

    // Save consolidated report
    const reportPath = path.join(__dirname, 'test-results-consolidated.json');
    fs.writeFileSync(reportPath, JSON.stringify(consolidatedReport, null, 2));

    // Print summary
    this.printConsolidatedSummary(consolidatedReport);

    return consolidatedReport;
  }

  getPriorityForFeature(testName) {
    const highPriority = ['api', 'search', 'navigation', 'load'];
    const lowPriority = ['export', 'keyboard', 'hover'];

    const nameLower = testName.toLowerCase();

    if (highPriority.some(keyword => nameLower.includes(keyword))) {
      return 'HIGH';
    } else if (lowPriority.some(keyword => nameLower.includes(keyword))) {
      return 'LOW';
    }

    return 'MEDIUM';
  }

  generateRecommendations(brokenFeatures, suiteResults) {
    const recommendations = [];

    // Check for API failures
    const apiFailures = brokenFeatures.filter(f => f.suite === 'API Integration');
    if (apiFailures.length > 0) {
      recommendations.push({
        category: 'API Integration',
        severity: 'CRITICAL',
        issue: `${apiFailures.length} API integration test(s) failed`,
        action: 'Verify backend server is running on http://localhost:9123 and API endpoints are functioning'
      });
    }

    // Check for search failures
    const searchFailures = brokenFeatures.filter(f => f.suite === 'Search Features');
    if (searchFailures.length > 0) {
      recommendations.push({
        category: 'Search',
        severity: 'HIGH',
        issue: `${searchFailures.length} search feature test(s) failed`,
        action: 'Review FTS5 search implementation and autocomplete functionality'
      });
    }

    // Check for relationship failures
    const relationshipFailures = brokenFeatures.filter(f => f.suite === 'Relationship Explorer');
    if (relationshipFailures.length > 0) {
      recommendations.push({
        category: 'Relationships',
        severity: 'MEDIUM',
        issue: `${relationshipFailures.length} relationship test(s) failed`,
        action: 'Check graph visualization library and relationship API endpoints'
      });
    }

    // Check overall pass rate
    const totalPassRate = parseFloat(suiteResults.reduce((sum, s) => sum + parseFloat(s.passRate), 0) / suiteResults.length);
    if (totalPassRate < 70) {
      recommendations.push({
        category: 'Overall Quality',
        severity: 'CRITICAL',
        issue: `Low overall pass rate: ${totalPassRate.toFixed(2)}%`,
        action: 'Comprehensive review needed - multiple systems are failing'
      });
    }

    return recommendations;
  }

  printConsolidatedSummary(report) {
    console.log('\n\n');
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║              CONSOLIDATED TEST REPORT                      ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log(`📅 Test Date: ${new Date(report.testDate).toLocaleString()}`);
    console.log(`⏱️  Duration: ${report.duration}`);
    console.log('');

    console.log('📊 OVERALL SUMMARY');
    console.log('─'.repeat(60));
    console.log(`Total Test Suites: ${report.summary.totalSuites}`);
    console.log(`Total Tests: ${report.summary.totalTests}`);
    console.log(`✅ Passed: ${report.summary.passed}`);
    console.log(`❌ Failed: ${report.summary.failed}`);
    console.log(`📈 Pass Rate: ${report.summary.passRate}%`);
    console.log('');

    console.log('📋 TEST SUITE RESULTS');
    console.log('─'.repeat(60));
    report.suites.forEach(suite => {
      const icon = suite.failed === 0 ? '✅' : '❌';
      console.log(`${icon} ${suite.suite} [${suite.priority}]`);
      console.log(`   Tests: ${suite.total} | Passed: ${suite.passed} | Failed: ${suite.failed} | Pass Rate: ${suite.passRate}%`);
      if (suite.error) {
        console.log(`   ERROR: ${suite.error}`);
      }
    });
    console.log('');

    if (report.brokenFeatures.length > 0) {
      console.log('🔴 BROKEN FEATURES');
      console.log('─'.repeat(60));

      const highPriority = report.brokenFeatures.filter(f => f.priority === 'HIGH');
      const mediumPriority = report.brokenFeatures.filter(f => f.priority === 'MEDIUM');
      const lowPriority = report.brokenFeatures.filter(f => f.priority === 'LOW');

      if (highPriority.length > 0) {
        console.log('\n🔥 HIGH PRIORITY:');
        highPriority.forEach(f => {
          console.log(`  • ${f.feature}`);
          f.errors.slice(0, 2).forEach(err => {
            console.log(`    - ${err.message}`);
          });
        });
      }

      if (mediumPriority.length > 0) {
        console.log('\n⚠️  MEDIUM PRIORITY:');
        mediumPriority.forEach(f => {
          console.log(`  • ${f.feature}`);
        });
      }

      if (lowPriority.length > 0) {
        console.log('\n💡 LOW PRIORITY:');
        lowPriority.forEach(f => {
          console.log(`  • ${f.feature}`);
        });
      }
    } else {
      console.log('✨ NO BROKEN FEATURES - ALL TESTS PASSED!');
    }

    if (report.recommendations.length > 0) {
      console.log('\n\n💡 RECOMMENDATIONS');
      console.log('─'.repeat(60));
      report.recommendations.forEach(rec => {
        console.log(`\n[${rec.severity}] ${rec.category}`);
        console.log(`Issue: ${rec.issue}`);
        console.log(`Action: ${rec.action}`);
      });
    }

    console.log('\n\n📁 Detailed reports saved:');
    console.log('  - tests/e2e/test-results-consolidated.json');
    console.log('  - tests/e2e/test-results-comprehensive.json');
    console.log('  - tests/e2e/test-results-api.json');
    console.log('  - tests/e2e/test-results-search.json');
    console.log('  - tests/e2e/test-results-relationship.json');
    console.log('  - tests/e2e/test-results-enhanced-glossary.json');
    console.log('');

    console.log('📸 Screenshots saved in: tests/e2e/test-screenshots/');
    console.log('');
  }
}

// Run if executed directly
if (require.main === module) {
  const runner = new MasterTestRunner();

  runner.runAllTests()
    .then(report => {
      console.log('\n✨ All test suites completed!');
      process.exit(report.summary.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('\n💥 Fatal error in test runner:', error);
      process.exit(1);
    });
}

module.exports = MasterTestRunner;
