FROM php:7.4.33-fpm

RUN apt-get update && apt-get install -y libfreetype-dev libjpeg62-turbo-dev libpng-dev libxpm-dev libwebp-dev libzip-dev \
	&& docker-php-ext-configure gd --enable-gd --with-webp --with-jpeg --with-xpm --with-freetype \
    && docker-php-ext-configure zip \
	&& docker-php-ext-install -j$(nproc) gd \
    && docker-php-ext-install -j$(nproc) zip

# # Install debugging tools
# RUN apt-get install -y gdb procps git python3 python3-pip libgmp-dev libmpfr-dev libreadline-dev texinfo iputils-ping netcat

# RUN bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# Disable vulnerable iconv encodings (CVE-2024-2961)
# RUN cd /usr/lib/x86_64-linux-gnu/gconv/ \
#     && cat gconv-modules | grep -v -E 'CN-?EXT' > gconv-modules-extra-patched.conf \
#     && mv gconv-modules-extra-patched.conf gconv-modules \
#     && rm -f gconv-modules.cache \
#     && iconvconfig \
#     && iconv -l | grep -E 'CN-?EXT' && exit 1 || true

# Make sure our custom extension is loaded 
COPY filehoover.so /usr/local/lib/php/extensions/no-debug-non-zts-20190902/

RUN cp /usr/local/etc/php/php.ini-development /usr/local/etc/php/php.ini && \
    echo "extension=filehoover" >> /usr/local/etc/php/php.ini

COPY app/ /var/www/html/
RUN mkdir /uploads && chown www-data /uploads

COPY flag /flag
RUN chmod 511 /flag

COPY entrypoint.sh /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/entrypoint
CMD ["entrypoint"]