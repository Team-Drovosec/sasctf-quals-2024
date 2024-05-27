FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y nginx
COPY nginx.conf /etc/nginx/nginx.conf

COPY frontend/deploy.tar /tmp/deploy.tar
RUN mkdir /var/www/lab
RUN tar -xvf /tmp/deploy.tar -C /var/www/lab

COPY backend .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]