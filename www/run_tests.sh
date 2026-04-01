#!/bin/bash
#
# run_tests.sh
# Test runner script for Empyre configuration validation
# Executes all test suites and reports results
#
# @since 20260401
# Usage: ./run_tests.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Empyre Configuration Test Suite"
echo "========================================"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: test_config_constants.php
echo "Running test_config_constants.php..."
echo "--- Validating configuration constants ---"
if php test_config_constants.php; then
    echo ""
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo ""
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "========================================"
echo ""

# Test 2: test_config_integration.php
echo "Running test_config_integration.php..."
echo "--- Validating configuration integration ---"
if php test_config_integration.php; then
    echo ""
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo ""
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "========================================"
echo ""

# Test 3: test_config.php
echo "Running test_config.php..."
echo "--- Running comprehensive validation ---"
if php test_config.php; then
    echo ""
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo ""
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "========================================"
echo "Test Suite Summary"
echo "========================================"
echo "Test suites passed: $TESTS_PASSED"
echo "Test suites failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "✓ All test suites passed!"
    exit 0
else
    echo "✗ Some test suites failed!"
    exit 1
fi
