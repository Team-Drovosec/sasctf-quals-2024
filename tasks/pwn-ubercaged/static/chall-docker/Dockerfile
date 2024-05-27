FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt -y upgrade && \
    apt install -y file sudo build-essential curl git lsb-base lsb-release apt-utils libgdk-pixbuf2.0-0 libatk1.0-0 fonts-liberation libxcomposite1 libpango-1.0-0 libxext6 xdg-utils libx11-6 libcups2 libexpat1 libxcb1 libxss1 libdbus-1-3 libgbm1 libgtk-3-0 libpangocairo-1.0-0 libxdamage1 libatspi2.0-0 libxfixes3 libatk-bridge2.0-0 libxi6 libxrender1 libxcursor1 libnss3 libglib2.0-0 libasound2 ca-certificates libgcc1 libnspr4 libxtst6 libcairo2 libx11-xcb1 libdrm2 wget libxrandr2 libxcb-dri3-0 libc6 libappindicator3-1 netcat curl libvulkan1 libu2f-udev

RUN groupadd -g 1000 pwn && useradd -g pwn -m -u 1000 pwn -s /bin/bash

COPY ./ubercaged /ubercaged

RUN dpkg -i /ubercaged/chromium-browser-unstable_120.0.6099.228-1_amd64.deb

USER pwn

CMD ["bash"]
