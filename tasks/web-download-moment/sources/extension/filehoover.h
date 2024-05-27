#ifndef __FILEHOOVER_H__
#define __FILEHOOVER_H__

#include "zend_compile.h"
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "php.h"

#define PHP_MY_EXTENSION_VERSION "1.0"
#define PHP_MY_EXTENSION_EXTNAME "filehoover"

#define FILE_MAX_LIVE_TIME_SEC 90
#define SLEEP_TIME_SEC 15

#define LOG_MESSAGE(fmt, message, ...)                                                             \
    {                                                                                              \
        char curr_time_str[80];                                                                    \
        GET_CUR_TIME_STR(curr_time_str);                                                           \
        php_printf("[LOG] [%s] " fmt, curr_time_str, message, ##__VA_ARGS__);                      \
    }

#define GET_CUR_TIME_STR(buffer)                                                                   \
    {                                                                                              \
        time_t rawtime;                                                                            \
        struct tm* timeinfo;                                                                       \
        time(&rawtime);                                                                            \
        timeinfo = localtime(&rawtime);                                                            \
        strftime(buffer, 80, "%Y-%m-%d %H:%M:%S", timeinfo);                                       \
    }

#define READ_PROPERTY(name)                                                                        \
    zend_read_property(filehoover_ce, getThis(), name, sizeof(name) - 1, 0, NULL)

#define CALL_TO_STRING(OBJ, RET_VAL)                                                               \
    {                                                                                              \
        zend_fcall_info fci;                                                                       \
        memset(&fci, 0, sizeof(fci));                                                              \
                                                                                                   \
        fci.size = sizeof(fci);                                                                    \
        ZVAL_STRING(&fci.function_name, "__toString");                                             \
        fci.object = Z_OBJ_P(OBJ);                                                                 \
        fci.retval = RET_VAL;                                                                      \
        fci.param_count = 0;                                                                       \
        fci.params = NULL;                                                                         \
                                                                                                   \
        if (zend_call_function(&fci, NULL) == FAILURE) {                                           \
            php_printf("Failed to call __toString\n");                                             \
            return;                                                                                \
        }                                                                                          \
                                                                                                   \
        zval_ptr_dtor(&fci.function_name);                                                         \
    }

#define Z_FILEHOOVER_P(zv)                                                                         \
    ((filehoover_object_t*)((char*)(Z_OBJ_P(zv)) - XtOffsetOf(filehoover_object_t, std)))

PHP_METHOD(FileHoover, __construct);
PHP_METHOD(FileHoover, __wakeup);
PHP_METHOD(FileHoover, __destruct);
PHP_METHOD(FileHoover, __toString);
PHP_METHOD(FileHoover, startHoovering);
PHP_MINIT_FUNCTION(filehoover);

ZEND_BEGIN_ARG_INFO_EX(arginfo_filehoover_construct, 0, 0, 1)
ZEND_ARG_INFO(0, directory)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_filehoover_wakeup, 0, 0, 0)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_filehoover_destruct, 0, 0, 0)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_filehoover_tostring, 0, 0, 0)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_filehoover_starthoovering, 0, 0, 0)
ZEND_END_ARG_INFO()

const zend_function_entry filehoover_functions[] = {
    PHP_ME(FileHoover,
           __construct,
           arginfo_filehoover_construct,
           ZEND_ACC_PUBLIC | ZEND_ACC_CTOR)                                                      //
    PHP_ME(FileHoover, __wakeup, arginfo_filehoover_wakeup, ZEND_ACC_PUBLIC)                     //
    PHP_ME(FileHoover, __destruct, arginfo_filehoover_destruct, ZEND_ACC_PUBLIC | ZEND_ACC_DTOR) //
    PHP_ME(FileHoover, __toString, arginfo_filehoover_tostring, ZEND_ACC_PUBLIC)                 //
    PHP_ME(FileHoover,
           startHoovering,
           arginfo_filehoover_starthoovering,
           ZEND_ACC_PUBLIC) //
    PHP_FE_END
};

#define phpext_my_extension_ptr &filehoover_module_entry

zend_module_entry filehoover_module_entry = { STANDARD_MODULE_HEADER,
                                              PHP_MY_EXTENSION_EXTNAME,
                                              NULL,
                                              PHP_MINIT(filehoover),
                                              NULL,
                                              NULL,
                                              NULL,
                                              NULL,
                                              PHP_MY_EXTENSION_VERSION,
                                              STANDARD_MODULE_PROPERTIES };

ZEND_GET_MODULE(filehoover)

#endif // __FILEHOOVER_H__