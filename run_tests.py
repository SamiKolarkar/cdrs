"""
Run all CDRS tests.

Usage:
    python run_tests.py
    python run_tests.py -v     (verbose)
"""

import unittest
import sys

loader = unittest.TestLoader()
suite = loader.discover(start_dir="tests", pattern="test_*.py")

verbosity = 2 if "-v" in sys.argv else 1
runner = unittest.TextTestRunner(verbosity=verbosity)
result = runner.run(suite)

sys.exit(0 if result.wasSuccessful() else 1)
