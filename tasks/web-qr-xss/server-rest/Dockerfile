FROM node:21-alpine

ENV LANG="C.UTF-8" PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV FLAG_IMAGE="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAM0AAADNCAAAAAA+16u1AAACPUlEQVR42u3aSY7jMBAEQP//09MfGLIzucFohE4CLMsMHwq1ff79petDQ0NDQ0NDQ0NDQ0NDQ0Ozq/n8fg2/MXzf/OHhI+kJaGhojmvGgWOkCU4+v9s5AQ0NzR3N/+LI8C54rvoTgjfT0NB8gSZIOIJ4mP4GDQ3NN2uCT4OUh4aG5qs0qXWnBDpTYdHQ0BzXBJ3Gy3ePO7c0NDQLY8Y6nM2TlSDYXZzi0tDQBNXFcGLZP1J1PuImCg0NzRlNEL+ClCf4NI148QSFhobmtGYxQgUNympGkgY2GhqaQ5o0WQnugp7FMM6lwxMaGpp3mjScpSnKYgpFQ0PzTlNlHUEp0ndIugPR0NCc0cx7EUlsaQ4471508ZCGhuagpgpJ1TeC4We/WUlDQ3NHszjiCLoh4xPVvQ0aGpo7mmprud9fXlhz3K5vaGho7tU3aWuiz2y6v42GhuagZt6umO87Bcwg70m3pmhoaI5rFnebqlZlcNTARUNDc1GTDjCDlCfYeK7mowtTXBoamh3N4oJiugDdTzxoaGjeadIaJU1vduYmq3NPGhqaMxVB1YFIFx7nmmrkSUNDc1JTbUQsBrb+a8EElIaG5pAmjUFV7jLfakirmtX6hoaGZqcvsB2cqlQm/WdpaGieaPrFh3QgGvRO71RrNDQ0VzSL/Y6qlnkX02hoaCrNYu7Sv+VJTKOhoanqm2CrIe1tBC8ISDQ0NCc11ZwybX8sRtAnnVsaGpo/cNHQ0NDQ0NDQ0NDQ0NDQ0DTXD0TBzhJz/3iXAAAAAElFTkSuQmCC"

RUN apk update
RUN apk add --no-cache zlib-dev udev nss ca-certificates
RUN apk add --no-cache chromium
RUN apk add --no-cache nginx redis python3 py3-pip
RUN yarn cache clean
RUN rm -rf /tmp/* /etc/apk/* /var/cache/apk/* /usr/share/man

COPY nginx.conf /etc/nginx/nginx.conf
COPY certs /etc/nginx/ssl

COPY frontend/deploy.tar /tmp/deploy.tar
RUN mkdir /var/www/rest
RUN tar -xvf /tmp/deploy.tar -C /var/www/rest

WORKDIR /bot
COPY bot .
RUN npm install

WORKDIR /app
COPY backend .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]