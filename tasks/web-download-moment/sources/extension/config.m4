PHP_ARG_ENABLE(filehoover, whether to enable filehoover extension, [ --enable-filehoover Enable the filehoover support], no, yes)
if test "$PHP_FILEHOOVER" = "yes"; then
    AC_DEFINE(HAVE_FILEHOOVER, 1, [Whether you have filehoover])
    PHP_NEW_EXTENSION(filehoover, filehoover.c, $ext_shared)
fi