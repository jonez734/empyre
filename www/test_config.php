<?php
/**
 * test_config.php
 * Comprehensive configuration validation test suite
 * Combines constant validation, type checking, and integration tests
 *
 * @since 20260401
 * Run: php test_config.php
 */

// Load the configuration
require_once(__DIR__ . "/config-dev.php");

class EmpyreConfigTest {
    private $tests_run = 0;
    private $tests_passed = 0;
    private $tests_failed = 0;
    private $failed_tests = [];

    public function run() {
        echo "=== Empyre Comprehensive Config Test Suite ===\n\n";

        $this->test_basic_constants();
        $this->test_path_constants();
        $this->test_smarty_constants();
        $this->test_logging_constants();
        $this->test_analytics_constants();
        $this->test_include_paths();
        $this->test_constants_are_readable();
        $this->test_url_formation();

        $this->print_summary();

        return $this->tests_failed === 0 ? 0 : 1;
    }

    private function test_basic_constants() {
        echo "--- Basic Site Constants ---\n";

        $this->assert_constant_exists("\\config\\SITENAME", "string");
        $this->assert_constant_exists("\\config\\SITEADMINEMAIL", "string");
        $this->assert_constant_exists("\\config\\SITETITLE", "string");
        $this->assert_constant_exists("\\config\\SITEURL", "string");
        $this->assert_constant_exists("\\config\\SITEDESCRIPTION", "string");

        // Validate content
        $sitename = constant("\\config\\SITENAME");
        $this->assert($sitename === "empyre", "SITENAME equals 'empyre'");

        echo "\n";
    }

    private function test_path_constants() {
        echo "--- Path Constants ---\n";

        $this->assert_constant_exists("\\config\\VHOSTDIR", "string");
        $this->assert_constant_exists("\\config\\SKINDIR", "string");
        $this->assert_constant_exists("\\config\\SKINURL", "string");
        $this->assert_constant_exists("\\config\\JSURL", "string");
        $this->assert_constant_exists("\\config\\IMAGESURL", "string");

        // Validate path structure
        $vhostdir = constant("\\config\\VHOSTDIR");
        $this->assert(
            substr($vhostdir, -1) === "/",
            "VHOSTDIR ends with slash"
        );

        $skindir = constant("\\config\\SKINDIR");
        $this->assert(
            strpos($skindir, $vhostdir) === 0,
            "SKINDIR is under VHOSTDIR"
        );

        echo "\n";
    }

    private function test_smarty_constants() {
        echo "--- Smarty Configuration ---\n";

        $this->assert_constant_exists("\\config\\SMARTYCOMPILEDTEMPLATESDIR", "string");
        $this->assert_constant_exists("\\config\\SMARTYPLUGINSDIR", "array");
        $this->assert_constant_exists("\\config\\SMARTYTEMPLATESDIR", "array");

        // Validate array contents
        $templates_dir = constant("\\config\\SMARTYTEMPLATESDIR");
        $this->assert(
            count($templates_dir) >= 2,
            "SMARTYTEMPLATESDIR has multiple fallback paths"
        );

        $plugins_dir = constant("\\config\\SMARTYPLUGINSDIR");
        $this->assert(
            count($plugins_dir) >= 1,
            "SMARTYPLUGINSDIR is not empty"
        );

        // Verify local paths come first
        $local_tmpl_path = $templates_dir[0] ?? "";
        $vhostdir = constant("\\config\\VHOSTDIR");
        $this->assert(
            strpos($local_tmpl_path, $vhostdir) === 0,
            "First template path is local (site-specific)"
        );

        echo "\n";
    }

    private function test_logging_constants() {
        echo "--- Logging Configuration ---\n";

        $this->assert_constant_exists("\\config\\LOGENTRYPREFIX", "string");

        $prefix = constant("\\config\\LOGENTRYPREFIX");
        $this->assert(
            strlen($prefix) > 0 && strlen($prefix) < 100,
            "LOGENTRYPREFIX has reasonable length"
        );

        echo "\n";
    }

    private function test_analytics_constants() {
        echo "--- Analytics Configuration ---\n";

        $this->assert_constant_exists("GOOGLEANALYTICSACCOUNT", "string");

        $ga_account = constant("GOOGLEANALYTICSACCOUNT");
        $this->assert(
            strlen($ga_account) > 0,
            "GOOGLEANALYTICSACCOUNT is not empty"
        );

        echo "\n";
    }

    private function test_include_paths() {
        echo "--- Include Path Configuration ---\n";

        $include_paths = explode(":", get_include_path());

        $this->assert(
            in_array("/srv/www/zoid6/php", $include_paths),
            "zoid6 PHP path in include_path"
        );

        $this->assert(
            in_array("/srv/www/bbsengine6/php/", $include_paths),
            "bbsengine6 PHP path in include_path"
        );

        $this->assert(
            in_array("/srv/www/smarty/", $include_paths),
            "Smarty path in include_path"
        );

        echo "\n";
    }

    private function test_constants_are_readable() {
        echo "--- Constant Readability ---\n";

        // Try to read all major constants and verify they don't error
        try {
            $sitename = constant("\\config\\SITENAME");
            $siteurl = constant("\\config\\SITEURL");
            $vhostdir = constant("\\config\\VHOSTDIR");
            $smarty_dir = constant("\\config\\SMARTYTEMPLATESDIR");

            $this->assert(true, "All constants readable without error");
        } catch (Exception $e) {
            $this->assert(false, "Constant read error: " . $e->getMessage());
        }

        echo "\n";
    }

    private function test_url_formation() {
        echo "--- URL Formation ---\n";

        $siteurl = constant("\\config\\SITEURL");
        $skinurl = constant("\\config\\SKINURL");

        $this->assert(
            strpos($siteurl, "http://") === 0 || strpos($siteurl, "https://") === 0,
            "SITEURL uses http or https protocol"
        );

        $this->assert(
            strpos($skinurl, $siteurl) === 0,
            "SKINURL is derived from SITEURL"
        );

        echo "\n";
    }

    private function assert_constant_exists($constant_name, $expected_type) {
        $this->tests_run++;

        if (!defined($constant_name)) {
            echo "✗ FAIL: {$constant_name} is not defined\n";
            $this->tests_failed++;
            $this->failed_tests[] = "Constant not defined: {$constant_name}";
            return false;
        }

        $value = constant($constant_name);
        $actual_type = gettype($value);

        if ($actual_type !== $expected_type) {
            echo "✗ FAIL: {$constant_name} is {$actual_type}, expected {$expected_type}\n";
            $this->tests_failed++;
            $this->failed_tests[] = "{$constant_name} has wrong type";
            return false;
        }

        echo "✓ PASS: {$constant_name} ({$expected_type})\n";
        $this->tests_passed++;
        return true;
    }

    private function assert($condition, $message) {
        $this->tests_run++;

        if (!$condition) {
            echo "✗ FAIL: {$message}\n";
            $this->tests_failed++;
            $this->failed_tests[] = $message;
            return false;
        }

        echo "✓ PASS: {$message}\n";
        $this->tests_passed++;
        return true;
    }

    private function print_summary() {
        echo "=== Test Summary ===\n";
        echo "Total: {$this->tests_run}\n";
        echo "Passed: {$this->tests_passed}\n";
        echo "Failed: {$this->tests_failed}\n";

        if ($this->tests_failed > 0) {
            echo "\nFailed tests:\n";
            foreach ($this->failed_tests as $test) {
                echo "  - {$test}\n";
            }
            echo "\n✗ Some tests failed!\n";
        } else {
            echo "\n✓ All tests passed!\n";
        }
    }
}

$tester = new EmpyreConfigTest();
exit($tester->run());
?>
