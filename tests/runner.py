"""
MedBill Enterprise - Automated Master Test Runner & Code Metrics Reporter
Executes all unit, integration, and tariff calculation test suites.
Reports execution time, pass/fail status, and Lines of Code (LOC) inventory.
"""

import os
import sys
import time
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def count_lines_of_code(root_dir: str):
    total_lines = 0
    file_counts = {}

    for dirpath, _, filenames in os.walk(root_dir):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue

        for f in filenames:
            if f.endswith((".py", ".html", ".js", ".css", ".md", ".json", ".ts", ".tsx")):
                filepath = os.path.join(dirpath, f)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                        lines = len(file.readlines())
                        total_lines += lines
                        rel_path = os.path.relpath(filepath, root_dir)
                        file_counts[rel_path] = lines
                except Exception:
                    pass

    return total_lines, file_counts


def run_all_tests():
    print("=" * 80)
    print("[*] MEDBILL ENTERPRISE - AUTOMATED TEST SUITE & VERIFICATION RUNNER")
    print("=" * 80)

    test_dir = os.path.join(PROJECT_ROOT, "tests")

    start_time = time.time()
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    duration = time.time() - start_time

    print("\n" + "=" * 80)
    print("[*] CODEBASE SCALE & LINE COUNT AUDIT")
    print("=" * 80)
    total_loc, file_counts = count_lines_of_code(PROJECT_ROOT)
    print(f"Total Project Lines of Code (LOC): {total_loc:,} lines across {len(file_counts)} files")
    print("-" * 80)
    print(f"Total Tests Executed: {result.testsRun}")
    print(f"Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Execution Duration: {duration:.3f} seconds")
    print(f"Test Suite Status: {'[PASS] ALL TESTS PASSED' if result.wasSuccessful() else '[FAIL] TESTS FAILED'}")
    print("=" * 80)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
