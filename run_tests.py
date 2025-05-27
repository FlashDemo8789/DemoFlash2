#!/usr/bin/env python3
"""
Test runner for FLASH API
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running FLASH API Tests...")
    print("-" * 50)
    
    # Set up environment
    os.environ["ENVIRONMENT"] = "testing"
    
    # Run pytest with coverage
    cmd = [
        "pytest",
        "-v",
        "--cov=api_server",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("\n❌ pytest not found. Please install: pip install pytest pytest-cov")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())