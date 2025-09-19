#!/usr/bin/env python3
"""
Test runner script for the finance app backend.
Run this script to execute all tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --type users       # Run only user tests
    python run_tests.py --type accounts    # Run only account tests
    python run_tests.py --type people      # Run only people tests
    python run_tests.py --type transactions # Run only transaction tests
    python run_tests.py --type postings    # Run only posting tests
    python run_tests.py --type splits      # Run only splits tests
    python run_tests.py --type budgets     # Run only budget tests
    python run_tests.py --type reports     # Run only report tests
    python run_tests.py --type fx_rates    # Run only FX rates tests
    python run_tests.py --type auth        # Run only authentication tests
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
    elif test_type == "splits":
        test_files = ["test_splits_package.py"]
        print("Running splits tests...")
    elif test_type == "budgets":
        test_files = ["test_budgets.py"]
        print("Running budget tests...")
    elif test_type == "reports":
        test_files = ["test_reports.py"]
        print("Running report tests...")
    elif test_type == "transactions":
        test_files = ["test_transactions.py"]
        print("Running transaction tests...")
    elif test_type == "postings":
        test_files = ["test_postings.py"]
        print("Running posting tests...")
    elif test_type == "fx_rates":
        test_files = ["test_fx_rates.py"]
        print("Running FX rates tests...")
    elif test_type == "auth":
        test_files = ["test_auth.py"]
        print("Running authentication tests...")
    else:  # all
        test_files = [
            "test_users.py", 
            "test_accounts.py", 
            "test_people.py",
            "test_transactions.py",
            "test_postings.py",
            "test_budgets.py",
            "test_reports.py",
            "test_splits_package.py",
            "test_fx_rates.py",
            "test_auth.py"
        ]
        print("Running all tests...")
    
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
        choices=["all", "users", "accounts", "people", "splits", "budgets", "reports", "transactions", "postings", "fx_rates", "auth"], 
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    args = parser.parse_args()
    exit_code = run_tests(args.type)
    sys.exit(exit_code)
