#!/bin/bash

php-fpm --daemonize
php /var/www/html/scripts/start_hoovering.php