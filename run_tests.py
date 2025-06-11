#!/usr/bin/env python3
"""
Test runner for the Enhanced Stock Tracker application.
Runs all unit tests and generates coverage reports.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def run_tests():
    """Run all unit tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / "tests"
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

def run_coverage():
    """Run tests with coverage report."""
    try:
        import coverage
        
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        success = run_tests()
        
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='coverage_html')
        print(f"\nHTML coverage report generated in 'coverage_html' directory")
        
        return success
        
    except ImportError:
        print("Coverage module not installed. Running tests without coverage.")
        return run_tests()

if __name__ == "__main__":
    print("Enhanced Stock Tracker - Test Suite")
    print("="*40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        success = run_coverage()
    else:
        success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
