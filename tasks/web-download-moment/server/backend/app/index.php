<?php

//                         d8b                                 
//                         88P        d8P                      
//                        d88      d888888P                    
//  d8888b d8888b  d8888b 888        ?88'   d888b8b   d888b8b  
// d8P' `Pd8P' ?88d8P' ?88?88        88P   d8P' ?88  d8P' ?88  
// 88b    88b  d8888b  d88 88b       88b   88b  ,88b 88b  ,88b 
// `?888P'`?8888P'`?8888P'  88b      `?8b  `?88P'`88b`?88P'`88b
//                                                          )88
//                                                         ,88P
//                                                     `?8888P 

require_once 'f_handlers/upload.php';
require_once 'f_handlers/download.php';
require_once 'f_handlers/preview.php';

ini_set('display_errors', 0);
ini_set('memory_limit', '32M');

define('TEXT_PREVIEW_LENGTH', 1024);
define('MAX_DIM', 368);
define('MAX_ZIP_ENTRIES', 25);
define('MAX_SIZE_PER_ZIP_ENTRY', 786432);
define('FILE_LIFETIME', 90);

function is_uuid($string) {
    return is_string($string) && preg_match('/^[a-f\d]{8}(-[a-f\d]{4}){4}[a-f\d]{8}$/i', $string);
}

function get_uuid() {
    return trim(file_get_contents('/proc/sys/kernel/random/uuid'));
}

$mod = isset($_SERVER['X_APP_MODULE']) ? $_SERVER['X_APP_MODULE'] : '';
$arg = isset($_SERVER['X_APP_ARG']) ? $_SERVER['X_APP_ARG'] : '';

switch ($mod) {
    case 'upload':
        die(upload_handler());
    case 'download':
        die(download_handler($arg));
    case 'preview':
        die(preview_handler($arg));
    default:
        break;
}
?>

<html>
    <head>
    </head>
    <body>
        <?php echo 'ogo'; ?>
    </body>
</html>

<?php
// SAS{3v3n_m15c0nFi6ur4t10n_C4pyb4rA_i5_4fra1d_0f_Y0u_n0W}

// include 'scripts/start_hoovering.php';
// FROM php:7.4.33-fpm

// zlib enjoyer? try packing this one then, perhaps there's a flag for 2.2: /var/www/html/blobus.txt


// Also rate this anecdote!

// One day Turtle’s phone rings, she picks it up and says: "Yes?" And they answer her: "yes."
// The turtle was surprised, but soon forgot about it.
// The next day the phone rang again.
// Turtle: "yes", and to her: "yes"
// On the third day, history repeated itself. The Turtle was already quite tired of this, and she went to the Owl.
// He comes, this way and that, he says, I: "yes", "yes" to me, the owl says: "don’t say "yes", say "at the machine"" The next day, the Turtle is contentedly waiting for the call. The phone rang.
// Turtle: "at the machine"
// To her: "Hello, is this Bath?"
// Turtle: "No, this is his brother Bolodya"
?>