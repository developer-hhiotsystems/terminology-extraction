#!/usr/bin/env python
"""Run comprehensive test suite with reporting"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results"""
    print("\n" + "="*70)
    print(f"  {description}")
    print("="*70 + "\n")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"\n[OK] {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[FAIL] {description} failed with exit code {e.returncode}")
        return False

def main():
    print("\n" + "="*70)
    print("  Comprehensive Test Suite")
    print("="*70)

    project_root = Path(__file__).parent.parent

    # Ensure we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\n[WARN] Not running in virtual environment")
        print("Activate with: .\\venv\\Scripts\\activate\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    results = []

    # Unit tests
    results.append(run_command(
        "pytest tests/unit -v --tb=short",
        "Unit Tests"
    ))

    # Integration tests
    results.append(run_command(
        "pytest tests/integration -v --tb=short",
        "Integration Tests"
    ))

    # Code coverage
    results.append(run_command(
        "pytest tests/ --cov=src/backend --cov-report=term-missing --cov-report=html",
        "Code Coverage Analysis"
    ))

    # Python code quality (if installed)
    try:
        import pylint
        results.append(run_command(
            "pylint src/backend --disable=C0114,C0115,C0116",
            "Python Code Quality (pylint)"
        ))
    except ImportError:
        print("\n[SKIP] pylint not installed, skipping code quality checks")

    # Summary
    print("\n" + "="*70)
    print("  Test Summary")
    print("="*70)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n[OK] All tests passed!\n")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test suite(s) failed\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
