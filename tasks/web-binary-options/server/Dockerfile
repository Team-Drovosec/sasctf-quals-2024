FROM php:8.3.6-apache

RUN a2enmod cgi
RUN a2enmod include

# Disable vulnerable iconv encodings (CVE-2024-2961)
RUN cd /usr/lib/x86_64-linux-gnu/gconv/gconv-modules.d \
    && cat gconv-modules-extra.conf | grep -v -E 'CN-?EXT' > gconv-modules-extra-patched.conf \
    && mv gconv-modules-extra-patched.conf gconv-modules-extra.conf \
    && rm -f ../gconv-modules.cache \
    && iconvconfig \
    && iconv -l | grep -E 'CN-?EXT' && exit 1 || true

COPY php.ini "$PHP_INI_DIR/php.ini"
COPY app/ /var/www/html/

COPY skuf /opt/skuf
RUN tar -xvf /opt/skuf/avatar.tar -C /opt/skuf

COPY cgi-bin/ /usr/lib/cgi-bin/
RUN chmod +x /usr/lib/cgi-bin/*

COPY flag /flag
RUN export FLAG=no-flag
RUN chmod 511 /flag
