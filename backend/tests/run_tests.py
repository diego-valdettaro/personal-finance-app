#!/usr/bin/env python3
"""
Test runner script for the finance app backend.
Run this script to execute all tests (users, accounts, people).

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --type users       # Run only user tests
    python run_tests.py --type accounts    # Run only account tests
    python run_tests.py --type people      # Run only people tests
"""

import subprocess
import sys
import os
import argparse

def run_tests(test_type="all"):
    """Run tests with pytest."""
    # Change to the tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Determine which tests to run
    if test_type == "users":
        test_files = ["test_users.py"]
        print("Running user tests...")
    elif test_type == "accounts":
        test_files = ["test_accounts.py"]
        print("Running account tests...")
    elif test_type == "people":
        test_files = ["test_people.py"]
        print("Running people tests...")
    else:  # all
        test_files = ["test_users.py", "test_accounts.py", "test_people.py"]
        print("Running all tests (users, accounts, people)...")
    
    print("=" * 50)
    
    # Run pytest with selected test files
    cmd = [
        sys.executable, "-m", "pytest", 
        *test_files,
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        print("Note: Account and People tests may fail until API endpoints are properly implemented.")
        return e.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run finance app backend tests")
    parser.add_argument(
        "--type", 
        choices=["all", "users", "accounts", "people"], 
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    args = parser.parse_args()
    exit_code = run_tests(args.type)
    sys.exit(exit_code)
