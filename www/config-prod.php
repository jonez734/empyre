<?php

namespace {
    /*
     * @since 20190817
     * @since 20221104
     */
    $includepath = get_include_path().":/srv/www/zoid6/php:/srv/www/bbsengine6/php/:/srv/www/smarty/";
    if (set_include_path($includepath) === false)
    {
        print("include path fail");
    }

    // require_once("zoid6.php");
}

namespace config {

    define("SITEADMINEMAIL", "empyre <empyre@projects.zoidtechnologies.com>");

    define("SITETITLE", "Empyre - Turn-based multi-player economy game");
    define("SITEURL", "https://zoidtechnologies.com/empyre/");
//    define("SITEKEYWORDS", "project achilles, monosodium glutamate, mono-sodium glutamate, msg, glutamate, disodium glutamate, truth in labeling, health, nutrition, consumer protection, food additives");
    define("SITEDESCRIPTION", "Empyre");
    //define("SITETYPE", "website");

    define("config\VHOSTDIR", "/srv/www/vhosts/zoidtechnologies.com/html/empyre/");
    define("DOCUMENTROOT", \config\VHOSTDIR);

    define("SKINDIR", DOCUMENTROOT . "skin/");
    define("SKINURL", SITEURL . "skin/");
    
    define("JSURL", "/empyre/js/");

    define("IMAGESURL", "https://zoidtechnologies.com/static/");

    // Define namespaced SMARTY constants for Smarty template engine
    // These are used by the template system to locate template files
    // Path array allows fallback search: site-specific → shared → framework
    define("config\SMARTYCOMPILEDTEMPLATESDIR", \config\VHOSTDIR . "templates_c");
    define("config\SMARTYPLUGINSDIR", [ 0 => \config\VHOSTDIR . "smarty/", 1 => "/srv/www/zoid6/smarty/"]);
    define("config\SMARTYTEMPLATESDIR", [
        0 => \config\VHOSTDIR . "skin/tmpl/",           // Empyre-specific templates
        1 => "/srv/www/zoid6/shared/skin/tmpl/",        // Shared zoid6 templates
        2 => "/srv/www/zoid6/skin/tmpl/",               // zoid6 project templates
        3 => "/srv/www/bbsengine6/skin/tmpl/"           // bbsengine6 framework templates
    ]);

    // Include zoid6config.php to create global aliases for backward compatibility
    // This converts namespaced constants (config\SMARTYTEMPLATESDIR) to global constants (SMARTYTEMPLATESDIR)
    require_once("/srv/www/zoid6/php/zoid6config.php");

    define("config\LOGENTRYPREFIX", "empyreprod");

//    define("STATICSKINURL", "/static/skin/");

    // define("ENGINEURL", "https://engine.zoidtechnologies.com/"); @see zoid6

    /**
     * @since 20200422
     * 3
     */
    define("GOOGLEANALYTICSACCOUNT", "UA-23705021-1");
} /* config namespace */
?>
