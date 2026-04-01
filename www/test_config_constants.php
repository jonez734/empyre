<?php
/**
 * test_config_constants.php
 * Validates that all required config\* namespace constants are defined
 *
 * @since 20260401
 * Run: php test_config_constants.php
 */

// Load the configuration
require_once(__DIR__ . "/config-dev.php");

$tests_run = 0;
$tests_passed = 0;
$tests_failed = 0;

/**
 * Test helper function - check if a namespaced constant exists
 */
function test_constant_defined($constant_name, $namespace = "config") {
    global $tests_run, $tests_passed, $tests_failed;
    $tests_run++;

    $full_name = "\\{$namespace}\\{$constant_name}";
    $defined = defined($full_name);

    if ($defined) {
        echo "✓ PASS: {$full_name} is defined\n";
        $tests_passed++;
    } else {
        echo "✗ FAIL: {$full_name} is not defined\n";
        $tests_failed++;
    }

    return $defined;
}

/**
 * Test helper function - verify constant has expected type
 */
function test_constant_type($constant_name, $expected_type, $namespace = "config") {
    global $tests_run, $tests_passed, $tests_failed;
    $tests_run++;

    $full_name = "\\{$namespace}\\{$constant_name}";

    if (!defined($full_name)) {
        echo "✗ FAIL: {$full_name} is not defined (cannot check type)\n";
        $tests_failed++;
        return false;
    }

    $value = constant($full_name);
    $actual_type = gettype($value);

    if ($actual_type === $expected_type) {
        echo "✓ PASS: {$full_name} is {$expected_type}\n";
        $tests_passed++;
        return true;
    } else {
        echo "✗ FAIL: {$full_name} is {$actual_type}, expected {$expected_type}\n";
        $tests_failed++;
        return false;
    }
}

echo "=== Empyre Config Constants Test Suite ===\n\n";

// Test basic constants
echo "--- Basic Site Constants ---\n";
test_constant_defined("SITENAME");
test_constant_defined("SITEADMINEMAIL");
test_constant_defined("SITETITLE");
test_constant_defined("SITEURL");
test_constant_defined("SITEDESCRIPTION");

// Test path constants
echo "\n--- Path Constants ---\n";
test_constant_defined("VHOSTDIR");
test_constant_type("VHOSTDIR", "string");

test_constant_defined("SKINDIR");
test_constant_type("SKINDIR", "string");

test_constant_defined("SKINURL");
test_constant_type("SKINURL", "string");

test_constant_defined("JSURL");
test_constant_type("JSURL", "string");

test_constant_defined("IMAGESURL");
test_constant_type("IMAGESURL", "string");

// Test Smarty-related constants
echo "\n--- Smarty Configuration Constants ---\n";
test_constant_defined("SMARTYCOMPILEDTEMPLATESDIR");
test_constant_type("SMARTYCOMPILEDTEMPLATESDIR", "string");

test_constant_defined("SMARTYPLUGINSDIR");
test_constant_type("SMARTYPLUGINSDIR", "array");

test_constant_defined("SMARTYTEMPLATESDIR");
test_constant_type("SMARTYTEMPLATESDIR", "array");

// Test logging constant
echo "\n--- Logging Constants ---\n";
test_constant_defined("LOGENTRYPREFIX");
test_constant_type("LOGENTRYPREFIX", "string");

// Test analytics constant
echo "\n--- Analytics Constants ---\n";
test_constant_defined("GOOGLEANALYTICSACCOUNT");
test_constant_type("GOOGLEANALYTICSACCOUNT", "string");

// Test that DOCUMENTROOT was defined (it's a global, not namespaced)
echo "\n--- Global Constants (backward compatibility) ---\n";
if (defined("DOCUMENTROOT")) {
    echo "✓ PASS: DOCUMENTROOT is defined (global)\n";
    $tests_passed++;
} else {
    echo "✗ FAIL: DOCUMENTROOT is not defined\n";
    $tests_failed++;
}
$tests_run++;

// Summary
echo "\n=== Test Summary ===\n";
echo "Total: {$tests_run}\n";
echo "Passed: {$tests_passed}\n";
echo "Failed: {$tests_failed}\n";

if ($tests_failed === 0) {
    echo "\n✓ All tests passed!\n";
    exit(0);
} else {
    echo "\n✗ Some tests failed!\n";
    exit(1);
}
?>
