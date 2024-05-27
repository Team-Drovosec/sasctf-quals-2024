#include "filehoover.h"
#include "php.h"
#include "zend.h"
#include "zend_API.h"
#include "zend_compile.h"
#include "zend_ini.h"
#include "zend_types.h"

zend_class_entry* filehoover_ce;

// Just a stub that prints "called constructor" to the console and it's arguments
PHP_METHOD(FileHoover, __construct)
{
    zval* path = NULL;

    if (zend_parse_parameters(ZEND_NUM_ARGS(), "z", &path) == FAILURE) {
        return;
    }

    if (!path || Z_TYPE_P(path) != IS_STRING) {
        php_error_docref(NULL, E_WARNING, "Expected string, got %s", zend_zval_type_name(path));
        return;
    }

    zend_update_property(filehoover_ce, getThis(), "directory", sizeof("directory") - 1, path);

    LOG_MESSAGE("Called %s, directory: %s\n", "__construct", Z_STRVAL_P(path));
}

PHP_METHOD(FileHoover, __wakeup)
{
    zval ret_val;
    CALL_TO_STRING(getThis(), &ret_val);
    LOG_MESSAGE("Called %s, Object: %s\n", "__wakeup", Z_STRVAL(ret_val));
}

PHP_METHOD(FileHoover, __destruct)
{
    zval ret_val;
    CALL_TO_STRING(getThis(), &ret_val);
    LOG_MESSAGE("Called %s, Object: %s\n", "__destruct", Z_STRVAL(ret_val));
}

PHP_METHOD(FileHoover, __toString)
{
    // Dump the directory name
    zval* directory = READ_PROPERTY("directory");

    // Copy string to local buffer
    char local_buffer[2048] = { 0 };
    memcpy(local_buffer, Z_STRVAL_P(directory), Z_STRLEN_P(directory));

    // Format the output
    char fmt_buffer[2048];
    zend_sprintf(fmt_buffer, "FileHoover(directory = \"%s\")", local_buffer);

    RETURN_STRING(fmt_buffer);
}

PHP_METHOD(FileHoover, startHoovering)
{
    zval ret_val;
    CALL_TO_STRING(getThis(), &ret_val);
    LOG_MESSAGE("Called %s, Object: %s\n", "startHoovering", Z_STRVAL(ret_val));

    zval* directory = READ_PROPERTY("directory");
    LOG_MESSAGE("Hoovering directory: %s\n", Z_STRVAL_P(directory));

    uint32_t removed = 0;

    while (1) {
        DIR* dir = opendir(Z_STRVAL_P(directory));
        if (!dir) {
            LOG_MESSAGE("Failed to open directory: %s\n", Z_STRVAL_P(directory));
            return;
        }

        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            // Cheeck if entry is a file, if so, get the creation time
            struct stat file_stat;
            char file_path[4096];
            snprintf(file_path, sizeof(file_path), "%s/%s", Z_STRVAL_P(directory), entry->d_name);

            if (stat(file_path, &file_stat) == -1) {
                LOG_MESSAGE("Failed to stat file: %s\n", file_path);
                continue;
            }

            // Check if the entry is a file
            if (!S_ISREG(file_stat.st_mode)) {
                continue;
            }

            time_t current_time = time(NULL);

            LOG_MESSAGE("Found file: %s, created: %ld seconds ago, creation time: %s",
                        entry->d_name,
                        current_time - file_stat.st_ctime,
                        ctime(&file_stat.st_ctime));

            // Check if the file is older than FILE_MAX_LIVE_TIME_SEC seconds
            if (current_time - file_stat.st_ctime < FILE_MAX_LIVE_TIME_SEC) {
                continue;
            }

            LOG_MESSAGE("File: %s is older than %d seconds - removing\n",
                        entry->d_name,
                        FILE_MAX_LIVE_TIME_SEC);

            // Remove the file
            if (unlink(file_path) == -1) {
                LOG_MESSAGE("Failed to remove file: %s\n", file_path);
                continue;
            }

            removed++;
        }

        closedir(dir);

        LOG_MESSAGE("Hoovered %d files, sleeping for %d seconds\n", removed, SLEEP_TIME_SEC);
        removed = 0;

        sleep(SLEEP_TIME_SEC);
    }
}

PHP_MINIT_FUNCTION(filehoover)
{
    zend_class_entry ce;

    INIT_CLASS_ENTRY(ce, "FileHoover", filehoover_functions);
    filehoover_ce = zend_register_internal_class(&ce);

    zend_declare_property_string(
        filehoover_ce, "directory", sizeof("directory") - 1, "", ZEND_ACC_PUBLIC);

    return SUCCESS;
}