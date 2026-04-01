<?php
/**
 * test_config_integration.php
 * Validates configuration integration with bbsengine6 and zoid6
 * Uses mocked/simulated integration (doesn't require live database)
 *
 * @since 20260401
 * Run: php test_config_integration.php
 */

// Load the configuration
require_once(__DIR__ . "/config-dev.php");

$tests_run = 0;
$tests_passed = 0;
$tests_failed = 0;

function assert_true($condition, $message) {
    global $tests_run, $tests_passed, $tests_failed;
    $tests_run++;

    if ($condition) {
        echo "✓ PASS: {$message}\n";
        $tests_passed++;
        return true;
    } else {
        echo "✗ FAIL: {$message}\n";
        $tests_failed++;
        return false;
    }
}

function assert_false($condition, $message) {
    return assert_true(!$condition, $message);
}

echo "=== Empyre Config Integration Test Suite ===\n\n";

// Test include paths
echo "--- Include Path Validation ---\n";
$include_paths = explode(":", get_include_path());
assert_true(
    in_array("/srv/www/zoid6/php", $include_paths),
    "zoid6 PHP path in include_path"
);
assert_true(
    in_array("/srv/www/bbsengine6/php/", $include_paths),
    "bbsengine6 PHP path in include_path"
);
assert_true(
    in_array("/srv/www/smarty/", $include_paths),
    "Smarty path in include_path"
);

// Test path constants are properly formed
echo "\n--- Path Formation Validation ---\n";
$vhostdir = constant("\\config\\VHOSTDIR");
$documentroot = constant("DOCUMENTROOT");

assert_true(
    $vhostdir === $documentroot,
    "VHOSTDIR matches DOCUMENTROOT"
);

assert_true(
    strpos($documentroot, "/srv/www/") === 0,
    "DOCUMENTROOT uses /srv/www/ prefix"
);

assert_true(
    substr($documentroot, -1) === "/",
    "DOCUMENTROOT ends with trailing slash"
);

// Test URL constants
echo "\n--- URL Constants Validation ---\n";
$siteurl = constant("\\config\\SITEURL");
$skinurl = constant("\\config\\SKINURL");
$jsurl = constant("\\config\\JSURL");
$imagesurl = constant("\\config\\IMAGESURL");

assert_true(
    strpos($siteurl, "http") === 0,
    "SITEURL uses http or https"
);

assert_true(
    substr($siteurl, -1) === "/",
    "SITEURL ends with trailing slash"
);

assert_true(
    strpos($skinurl, $siteurl) === 0,
    "SKINURL is based on SITEURL"
);

assert_true(
    strpos($jsurl, "/") === 0,
    "JSURL is absolute path starting with /"
);

// Test Smarty configuration
echo "\n--- Smarty Configuration Validation ---\n";
$smarty_templates_dir = constant("\\config\\SMARTYTEMPLATESDIR");
$smarty_plugins_dir = constant("\\config\\SMARTYPLUGINSDIR");
$smarty_compiled_dir = constant("\\config\\SMARTYCOMPILEDTEMPLATESDIR");

assert_true(
    is_array($smarty_templates_dir),
    "SMARTYTEMPLATESDIR is an array"
);

assert_true(
    count($smarty_templates_dir) >= 2,
    "SMARTYTEMPLATESDIR has multiple fallback paths"
);

assert_true(
    is_array($smarty_plugins_dir),
    "SMARTYPLUGINSDIR is an array"
);

assert_true(
    count($smarty_plugins_dir) >= 1,
    "SMARTYPLUGINSDIR has at least one path"
);

// Verify template directory precedence
$local_template_path = $smarty_templates_dir[0] ?? null;
assert_true(
    strpos($local_template_path ?? "", $vhostdir) === 0,
    "First template path is local (site-specific)"
);

$shared_template_path = $smarty_templates_dir[count($smarty_templates_dir)-1] ?? null;
assert_true(
    strpos($shared_template_path ?? "", "/srv/www/bbsengine6/") === 0,
    "Last template path is bbsengine6 framework (fallback)"
);

// Test site name validation
echo "\n--- Site Identity Validation ---\n";
$sitename = constant("\\config\\SITENAME");
$sitetitle = constant("\\config\\SITETITLE");

assert_true(
    $sitename === "empyre",
    "SITENAME is 'empyre'"
);

assert_true(
    strlen($sitetitle) > 0,
    "SITETITLE is not empty"
);

assert_true(
    strpos($sitetitle, "empyre") !== false || strpos($sitetitle, "Empyre") !== false,
    "SITETITLE mentions 'empyre'"
);

// Test logging configuration
echo "\n--- Logging Configuration Validation ---\n";
$log_prefix = constant("\\config\\LOGENTRYPREFIX");

assert_true(
    strlen($log_prefix) > 0,
    "LOGENTRYPREFIX is defined"
);

assert_true(
    strpos($log_prefix, "empyre") !== false,
    "LOGENTRYPREFIX includes 'empyre' for identification"
);

// Test analytics
echo "\n--- Analytics Configuration Validation ---\n";
$ga_account = constant("GOOGLEANALYTICSACCOUNT");

assert_true(
    strlen($ga_account) > 0,
    "GOOGLEANALYTICSACCOUNT is defined"
);

assert_true(
    strpos($ga_account, "UA-") === 0,
    "GOOGLEANALYTICSACCOUNT has valid format"
);

// Summary
echo "\n=== Integration Test Summary ===\n";
echo "Total: {$tests_run}\n";
echo "Passed: {$tests_passed}\n";
echo "Failed: {$tests_failed}\n";

if ($tests_failed === 0) {
    echo "\n✓ All integration tests passed!\n";
    exit(0);
} else {
    echo "\n✗ Some integration tests failed!\n";
    exit(1);
}
?>
