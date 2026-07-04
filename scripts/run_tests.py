#!/usr/bin/env python3
"""
VOYO Test Runner

Convenient script to run different test suites.

Usage:
    python run_tests.py                    # Run all fast tests
    python run_tests.py --all              # Run all tests including slow
    python run_tests.py --integration      # Run integration tests only
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --api              # Run API tests
    python run_tests.py --academic         # Run academic benchmarking tests
    python run_tests.py --coverage         # Run tests with coverage report
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_pytest(args, extra_args):
    """Run pytest with given arguments"""
    cmd = ["python", "-m", "pytest"]

    # Add test directories based on args
    test_dirs = []
    if args.integration:
        test_dirs.append("tests/integration")
    if args.unit:
        test_dirs.append("tests/unit")
    if args.api:
        test_dirs.append("tests/api")
    if args.tools:
        test_dirs.append("tests/tools")
    if args.e2e:
        test_dirs.append("tests/e2e")
    if args.academic:
        test_dirs.append("tests/academic")

    # Default to all tests if no specific category selected
    if not test_dirs and not args.all:
        # Run all tests except academic and slow
        cmd.extend([
            "tests/",
            "-m", "not slow and not academic",
            "-v"
        ])
    elif test_dirs:
        cmd.extend(test_dirs)
        cmd.extend(["-v"])
    else:
        cmd.append("tests/")

    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    # Add marker for slow tests if requested
    if args.all:
        cmd.extend(["-m", ""])
    elif args.slow:
        cmd.extend(["-m", "slow"])

    # Add any extra arguments
    cmd.extend(extra_args)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="VOYO Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Test category options
    parser.add_argument("--all", action="store_true",
                       help="Run all tests including slow and academic")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests only")
    parser.add_argument("--unit", action="store_true",
                       help="Run unit tests only")
    parser.add_argument("--api", action="store_true",
                       help="Run API tests only")
    parser.add_argument("--tools", action="store_true",
                       help="Run tool tests only")
    parser.add_argument("--e2e", action="store_true",
                       help="Run end-to-end tests only")
    parser.add_argument("--academic", action="store_true",
                       help="Run academic benchmarking tests")
    parser.add_argument("--slow", action="store_true",
                       help="Include slow-running tests")

    # Output options
    parser.add_argument("--coverage", action="store_true",
                       help="Run tests with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args, remaining = parser.parse_known_args()

    return run_pytest(args, remaining)


if __name__ == "__main__":
    sys.exit(main())