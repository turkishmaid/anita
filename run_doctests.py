#!/usr/bin/env python3

import doctest
import sys
from pathlib import Path


def run_all_doctests():
    """Run doctests for all modules in the anita package."""
    anita_dir = Path("anita")
    test_files = []

    for py_file in anita_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            module_name = f"anita.{py_file.stem}"
            try:
                module = __import__(module_name, fromlist=[py_file.stem])
                print(f"\n=== Testing {module_name} ===")
                result = doctest.testmod(module, verbose=True)
                test_files.append((module_name, result))
            except ImportError as e:
                print(f"Could not import {module_name}: {e}")

    # Summary
    print("\n=== SUMMARY ===")
    total_tests = total_failures = 0
    for name, (failures, tests) in test_files:
        total_tests += tests
        total_failures += failures
        status = "PASS" if failures == 0 else "FAIL"
        print(f"{name}: {tests} tests, {failures} failures [{status}]")

    print(f"\nOverall: {total_tests} tests, {total_failures} failures")
    return total_failures == 0


if __name__ == "__main__":
    success = run_all_doctests()
    sys.exit(0 if success else 1)
