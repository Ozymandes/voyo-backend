#!/usr/bin/env python3
"""
Quick Test Runner

Runs a subset of fast tests to verify basic functionality.
Use this for quick smoke tests before committing or deploying.
"""

import sys
import subprocess
from pathlib import Path


def run_quick_tests():
    """Run quick smoke tests"""
    print("🔥 Running Quick Smoke Tests...")
    print("=" * 60)

    # List of quick test files to run
    quick_tests = [
        "tests/integration/cleo/test_cleo.py",
        "tests/integration/database/test_db_simple.py",
        "tests/tools/test_tool_format.py",
        "tests/e2e/test_safeguards.py"
    ]

    cmd = [
        "python", "-m", "pytest",
        *quick_tests,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ All quick tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_quick_tests())