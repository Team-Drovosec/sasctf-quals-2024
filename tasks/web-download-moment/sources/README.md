# C-style extension

## Building

`./build-extension.sh`

## Running

Running php with the extension: `php -dextension=./modules/filehoover.so -r '$v = new FileHoover([]); echo $v;'`

## Playing with PHAR

Creating test phar-archive:

1. Run the following command:

```bash
php --define phar.readonly=0 -dextension=./modules/filehoover.so -r '
    $v = new FileHoover("/tmp/files");
    echo $v . "\n";
    echo "Directory property (from PHP):" . $v->directory . "\n";
    echo $v->startHoovering() . "\n";
    $phar = new Phar("vzlom.phar");
    $phar->startBuffering();
    $phar->addFromString("123312.txt", "text");
    $phar->setStub("\n<?php echo __HALT_COMPILER(); ?>");
    $phar->setMetadata($v);
    $phar->stopBuffering();'
```

Loading test phar-archive:

```bash
php --define phar.readonly=0 -dextension=./modules/filehoover.so -r 'file_get_contents("phar://vzlom.phar");'
```
